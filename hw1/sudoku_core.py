###
### Propagation function to be used in the recursive sudoku solver
###
def propagate(sudoku_possible_values,k):

    print(sudoku_possible_values)

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
    for row in sudoku_possible_values:
        print(row)
        lone_singles = [value[0] for value in row if len(value) == 1]
        print(lone_singles)

        for possible_row_values in row:
            if len(possible_row_values) > 1:
                print('Hier')
                # print(possible_row_values)
                possible_row_values_update = [value for value in possible_row_values if value not in lone_singles]
                possible_row_values = possible_row_values_update
                # print(possible_row_values)

        print(row)



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
