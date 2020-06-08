from pysat.formula import CNF
from pysat.solvers import MinisatGH
from ortools.sat.python import cp_model

import gurobipy as gp
from gurobipy import GRB

# for debugging, TODO: remove before submission
import pdb

###
### Propagation function to be used in the recursive sudoku solver
###
def propagate(sudoku_possible_values, k):
    # TODO: test how this function handles unsolvable input
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
        # TODO: see if you can speed this up, this seems excessive
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

    # General scheme of computations:
    # 1) take in put x (i.e., sudoku) and encode in CNF (in=sudoku --> out=CNF formula phi)
    # 2) feed CNF/formula into SAT solver (in=phi --> out=satisfiable (bool), truth assignment alpha)
    # 3) if satisfiable: extract/decode sudoku solution from alpha - else: return input sudoku / error

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

    #TODO: add if statement for when answer==False!!!!
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

    #TODO: add a propagation strategy

    model = cp_model.CpModel()
    vars = []
    num_rows = num_cols = num_values = k ** 2

    # New approach: binary approach, i.e., make binary variables s_rcv = I{entry_rc == v}
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
    return None;

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
