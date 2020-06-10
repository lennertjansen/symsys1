from pysat.formula import CNF
from pysat.solvers import MinisatGH
from ortools.sat.python import cp_model
import gurobipy as gp
from gurobipy import GRB
import clingo

###
### Propagation function to be used in the recursive sudoku solver
###
def propagate(sudoku_possible_values, k):
    # simplest/naive propagation strategy: every time you encounter a single
    # possible value in a unit, remove it from all other possible values in the unit

    # row-wise removal of lone singles
    for row in sudoku_possible_values:
        lone_singles = [value[0] for value in row if len(value) == 1]
        for i, possible_row_values in enumerate(row):
            if len(possible_row_values) > 1:
                possible_row_values_update = [value for value in possible_row_values if value not in lone_singles]
                row[i] = possible_row_values_update

    # column-wise removal of lone singles
    for col_index in range(k ** 2):
        certain_col_values = []
        for row_index in range(k ** 2):
            if len(sudoku_possible_values[row_index][col_index]) == 1:
                certain_col_values.append(sudoku_possible_values[row_index][col_index][0])

        for row_index in range(k ** 2):
            if len(sudoku_possible_values[row_index][col_index]) > 1:
                possible_col_values_update = [value for value in sudoku_possible_values[row_index][col_index] if value not in certain_col_values]
                sudoku_possible_values[row_index][col_index] = possible_col_values_update

    # block-wise removal of certain values
    for i1 in range(k):
        for j1 in range(k):
            certain_block_values = []
            for i2 in range(k):
                for j2 in range(k):
                    row_index = i1 * k + i2
                    col_index = j1 * k + j2

                    possible_block_values = sudoku_possible_values[row_index][col_index]
                    if len(possible_block_values) == 1:
                        certain_block_values.append(possible_block_values[0])

            for i2 in range(k):
                for j2 in range(k):
                    row_index = i1 * k + i2
                    col_index = j1 * k + j2

                    possible_block_values = sudoku_possible_values[row_index][col_index]
                    if len(possible_block_values) > 1:
                        possible_block_values_update = [value for value in sudoku_possible_values[row_index][col_index] if value not in certain_block_values]
                        sudoku_possible_values[row_index][col_index] = possible_block_values_update


    return sudoku_possible_values;

###
### Solver that uses SAT encoding
###
def solve_sudoku_SAT(sudoku, k):

    formula = CNF()

    num_rows = num_cols = num_values = k ** 2

    # creates propositional variables indicated as unique positive integers
    def s(row, col, value):
        return (k ** 4) * row + (k ** 2) * col + value

    def s_extract(row, col, pos_lit):
        return pos_lit - ((k ** 4) * row + (k ** 2) * col)

    # at least one number in each entry
    for row in range(num_rows):
        for col in range(num_cols):
            clause = []

            # if entry already given append unit clause
            if sudoku[row][col] != 0:
                clause.append(s(row, col, sudoku[row][col]))

            # else append disjunction
            else:
                for value in range(1, num_values + 1):
                    clause.append(s(row, col, value))
            formula.append(clause)


    # each value can appear at most once in every row
    for col in range(num_cols):
        for value in range(1, num_values + 1):
            for row1 in range(num_rows - 1):
                for row2 in range(row1 + 1, num_rows):
                    clause = [-s(row1, col, value), -s(row2, col, value)]
                    formula.append(clause)

    # each value can appear at most once in every column
    for row in range(num_cols):
        for value in range(1, num_values + 1):
            for col1 in range(num_cols - 1):
                for col2 in range(col1 + 1, num_cols):
                    clause = [-s(row, col1, value), -s(row, col2, value)]
                    formula.append(clause)

    # each value can appear at most once in every block
    for value in range(1, num_values + 1):
        for i in range(k):
            for j in range(k):
                for x in range(k):
                    for y in range(k):
                        for y1 in range(y + 1, k):
                            clause = [-s(k*i + x, k*j + y, value),
                                      -s(k*i + x, k*j + y1, value)]
                            formula.append(clause)

    for value in range(1, num_values + 1):
        for i in range(k):
            for j in range(k):
                for x in range(k):
                    for y in range(k):
                        for x1 in range(x + 1, k):
                            for l in range(k):
                                clause = [-s(k*i + x, k*j + y, value),
                                          -s(k*i + x1, k*j + l, value)]
                                formula.append(clause)

    solver = MinisatGH()
    solver.append_formula(formula)

    answer = solver.solve()

    pos_lits = [value for value in solver.get_model() if value > 0]

    count = 0
    for row in range(num_rows):
        for col in range(num_cols):
            if sudoku[row][col] == 0:
                sudoku[row][col] = s_extract(row, col, pos_lits[count])
            count += 1


    return sudoku

###
### Solver that uses CSP encoding
###
def solve_sudoku_CSP(sudoku,k):

    model = cp_model.CpModel()
    vars = []
    num_rows = num_cols = num_values = k ** 2

    # binary approach, i.e., make binary variables s_rcv = I{entry_rc == v}
    for row in range(num_rows):
        row_vars = []

        for col in range(num_cols):
            # if entry already given, set variable s_rcv to 1 for appropriate subscripts
            entry_vars = []
            if  sudoku[row][col] == 0:
                for value in range(1, num_values + 1):
                    entry_vars.append(model.NewBoolVar('r{}c{}v{}'.format(row, col, value)))
                row_vars.append(entry_vars)

            else:
                for value in range(1, num_values + 1):
                    if sudoku[row][col] != value:
                        entry_vars.append(model.NewIntVar(0, 0, 'r{}c{}v{}'.format(row, col, value)))
                    else:
                        entry_vars.append(model.NewIntVar(1, 1,'r{}c{}v{}'.format(row, col, value)))
                row_vars.append(entry_vars)

        vars.append(row_vars)

    # every cell/entry must be filled with one value
    for row in range(num_rows):
        for col in range(num_cols):
            model.Add(sum(vars[row][col]) == 1)


    # every value must appear once in every row
    for row in range(num_rows):
        for value_index in range(num_values):
            value_occurence_per_row = []
            for col in range(num_cols):
                value_occurence_per_row.append(vars[row][col][value_index])
            model.Add(sum(value_occurence_per_row) == 1)


    # every value must appear once in every col
    for col in range(num_cols):
        for value_index in range(num_values):
            value_occurence_per_col = []
            for row in range(num_rows):
                value_occurence_per_col.append(vars[row][col][value_index])
            model.Add(sum(value_occurence_per_col) == 1)


    # every value must appear once in every block
    for i1 in range(k):
        for j1 in range(k):
            for value_index in range(num_values):
                value_occurence_per_block = []

                for i2 in range(k):
                    for j2 in range(k):
                        row_index = i1 * k + i2
                        col_index = j1 * k + j2

                        value_occurence_per_block.append(vars[row_index][col_index][value_index])

                model.Add(sum(value_occurence_per_block) == 1)


    solver = cp_model.CpSolver()
    answer = solver.Solve(model)

    if answer == cp_model.FEASIBLE:
        for row in range(num_rows):
            for col in range(num_cols):
                if sudoku[row][col] == 0:
                    for value_index in range(num_values):
                        if solver.Value(vars[row][col][value_index]) == 1:
                            sudoku[row][col] = value_index + 1

    return sudoku

###
### Solver that uses ASP encoding
###
def solve_sudoku_ASP(sudoku,k):

    # empty string to be filled with answer set program
    asp_code = ""

    asp_code += """
        #const k={}.
        #const km={}.
        #const kk={}.
        cell_index(0..km).
        cell_value(1..kk).
    """.format(k, (k**2) - 1, k ** 2)

    num_rows = num_cols = num_values = k ** 2

    # create atoms for given entries and their corresponding values
    for row in range(num_rows):
        for col in range(num_cols):
            for value in range(1, num_values + 1):
                if sudoku[row][col] != 0:
                    if sudoku[row][col] == value:
                        asp_code += """
                            given_cell({}, {}, {}).
                        """.format(row, col, value)

    # make remaining cells empty cell types and fill sudoku entries with corresponding given values
    asp_code += """
        empty_cell(R, C) :- cell_index(R), cell_index(C), not given_cell(R, C).
        sudoku(R, C, V) :- given_cell(R, C, V).
    """

    # enforce every cell must be filled with exactly one value, by using a
    # cardinality rule, expressing the set of permitted values using
    # conditonial literals
    asp_code += """
        1 { sudoku(R, C, V) : cell_value(V) } 1 :- empty_cell(R, C).
    """

    # row, col, and block constraints respectively
    asp_code += """
        :- cell_index(R), sudoku(R, C, V), sudoku(R, C1, V), C != C1.
        :- cell_index(C), sudoku(R, C, V), sudoku(R1, C, V), R != R1.
    """
    asp_code += """
        block_index(R, N) :- cell_index(R), M = R / k, N = M * k.
        same_block(R, R1) :- cell_index(R), cell_index(R1), block_index(R, RS), block_index(R1, RS).
        :- same_block(R, R1), same_block(C, C1), R != R1, sudoku(R, C, V), sudoku(R1, C1, V).
        :- same_block(R, R1), same_block(C, C1), C != C1, sudoku(R, C, V), sudoku(R1, C1, V).
    """

    # show statement indicating we are only interested in sudoku values if printed
    asp_code += """
        #show sudoku/3.
    """

    control = clingo.Control()
    control.add("base", [], asp_code)
    control.ground([("base", [])])

    def on_model(model):
        for atom in model.symbols(atoms = True):
            if atom.name == "sudoku":
                if sudoku[atom.arguments[0].number][atom.arguments[1].number] == 0:
                    sudoku[atom.arguments[0].number][atom.arguments[1].number] = atom.arguments[2].number

    # ask clingo to find a single model for program (necessary for empty input)
    control.configuration.solve.models = 1
    answer = control.solve(on_model=on_model)

    if answer.satisfiable == True:
        print("Found solution")
    else:
        print("Did not find solution");

    return sudoku

###
### Solver that uses ILP encoding
###
def solve_sudoku_ILP(sudoku,k):

    model = gp.Model()
    vars = []
    num_rows = num_cols = num_values = k ** 2

    # Make binary variables
    for row in range(num_rows):
        row_vars = []

        for col in range(num_cols):

            entry_vars = []
            if sudoku[row][col] == 0:
                for value in range(1, num_values + 1):
                    entry_vars.append(model.addVar(vtype = GRB.BINARY,
                    name = "r{}c{}v{}".format(row, col, value)))
                row_vars.append(entry_vars)
            else:
                for value in range(1, num_values + 1):
                    if sudoku[row][col] != value:
                        entry_vars.append(model.addVar(vtype = GRB.INTEGER,
                        lb = 0, ub = 0, name = "r{}c{}v{}".format(row, col, value)))
                    else:
                        entry_vars.append(model.addVar(vtype = GRB.INTEGER,
                        lb = 1, ub = 1, name = "r{}c{}v{}".format(row, col, value)))
                row_vars.append(entry_vars)
        vars.append(row_vars)

    # every entry must be filled with exactly one value
    for row in range(num_rows):
        for col in range(num_cols):
            model.addConstr(gp.quicksum(vars[row][col]) == 1)

    # row constraints
    for row in range(num_rows):
        for value_index in range(num_values):
            value_occurence_per_row = []
            for col in range(num_cols):
                value_occurence_per_row.append(vars[row][col][value_index])
            model.addConstr(gp.quicksum(value_occurence_per_row) == 1)

    # column constraints
    for col in range(num_cols):
        for value_index in range(num_values):
            value_occurence_per_col = []
            for row in range(num_rows):
                value_occurence_per_col.append(vars[row][col][value_index])
            model.addConstr(gp.quicksum(value_occurence_per_col) == 1)

    # block constraints
    for i1 in range(k):
        for j1 in range(k):
            for value_index in range(num_values):
                value_occurence_per_block = []

                for i2 in range(k):
                    for j2 in range(k):
                        row_index = i1 * k + i2
                        col_index = j1 * k + j2

                        value_occurence_per_block.append(vars[row_index][col_index][value_index])
                model.addConstr(gp.quicksum(value_occurence_per_block) == 1)


    model.optimize()

    if model.status == GRB.OPTIMAL:
        for row in range(num_rows):
            for col in range(num_cols):
                if sudoku[row][col] == 0:
                    for value_index in range(num_values):
                        if vars[row][col][value_index].x == 1:
                            sudoku[row][col] = value_index + 1





    return sudoku;
