###
### Propagation function to be used in the recursive sudoku solver
###
def propagate(sudoku_possible_values,k):

    # check rows for naked pairs
    # for row in sudoku_possible_values:
    #     print(row)
    #     for possible_row_values in row:
    #         naked_pair = False
    #         possible_values_to_remove = []
    #         if len(possible_row_values) == 2:
    #             if row.count(possible_row_values) > 1:
    #                 print('Naked stuff found')
    #                 naked_pair = True
    #                 possible_values_to_remove.append(possible_row_values)

    # simplest/naive propagation strategy: every time you encounter a single
    # possible value in a unit, remove it from all other possible values in the unit

    # row-wise removal of lone singles
    for row in sudoku_possible_values:
        lone_singles = [value[0] for value in row if len(value) == 1]
        for i, possible_row_values in enumerate(row):
            if len(possible_row_values) > 1:
                possible_row_values_update = [value for value in possible_row_values if value not in lone_singles]
                row[i] = possible_row_values_update
    # #
    # # # column-wise removal of lone singles
    # # # print('Before')
    # # # print(sudoku_possible_values)
    for col_index in range(k ** 2):
        # TODO: see if you can speed this up, this seems excessive
        certain_col_values = []
        for row_index in range(k ** 2):
            if len(sudoku_possible_values[row_index][col_index]) == 1:
                certain_col_values.append(sudoku_possible_values[row_index][col_index][0])

        for row_index in range(k ** 2):
            if len(sudoku_possible_values[row_index][col_index]) > 1:
                # print('My man')
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
def solve_sudoku_SAT(sudoku,k):
    return None;

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
