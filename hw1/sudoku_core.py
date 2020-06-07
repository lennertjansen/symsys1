from pysat.formula import CNF
from pysat.solvers import MinisatGH
import numpy as np

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
    num_clauses = 0

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
            num_clauses += 1


    # each value can appear at most once in every row
    for col in range(num_cols):
        for value in range(1, num_values + 1):
            for row1 in range(num_rows - 1):
                for row2 in range(row1 + 1, num_rows):
                    clause = [-s(row1, col, value), -s(row2, col, value)]
                    formula.append(clause)
                    num_clauses += 1

    # each value can appear at most once in every column
    for row in range(num_cols):
        for value in range(1, num_values + 1):
            for col1 in range(num_cols - 1):
                for col2 in range(col1 + 1, num_cols):
                    clause = [-s(row, col1, value), -s(row, col2, value)]
                    formula.append(clause)
                    num_clauses += 1

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
                            num_clauses += 1

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
                                num_clauses += 1

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
    return None;

###
### Solver that uses ASP encoding
###
def solve_sudoku_ASP(sudoku,k):
    return None;

###
### Solver that uses ILP encoding
###
def solve_sudoku_ILP(sudoku,k):
    return None;
