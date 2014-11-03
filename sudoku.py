#!/usr/bin/python

import numpy as np
import re
import copy
import sys


"""Given a coordinate (x,y), then affected[x][y] is the list of coordinates in the same row, column and square of (x,y)"""
affected = [[{(i,y) for i in xrange(9)} | {(x,i) for i in xrange(9)} | {(3*(x/3)+i, 3*(y/3)+j) for i in xrange(3) for j in xrange(3)} for y in xrange(9)] for x in xrange(9)]

def in_row(elem, r, grid):
    """Check whether elem is in row r"""
    return elem in grid[r,:]


def in_column(elem, c, grid):
    """Check whether elem in in column c"""
    return elem in grid[:,c]


def in_square(elem,r,c,grid):
    """Check whether elem is in the square where (r,c) is"""
    r_tl = 3*(r/3) #index of the row of the top left corner of the 3x3 grid (r,c) is in
    c_tl = 3*(c/3) #index of the column of the top left corner of the 3x3 grid (r,c) is in
    return elem in grid[r_tl:r_tl+3, c_tl:c_tl+3]


def string_to_grid(line):
    """From the string representation of a sudoku puzzle to an array"""
    return np.reshape(np.array([0 if line[i]=='.' else int(line[i]) for i in xrange(len(line))]), (9,9))


def feasibility_set(grid):
    """Returns a list of set of feasible values for each cell. cell_sets[9*x+y] is the set of feasibile values for the cell (x,y).
    The feasibility set of a cell is set to {-1} if the value for 
    that cell has already been fixed. An empty set means that no values are feasibile for that cell"""
    total_set = set(range(1,10))
    row_sets = map(lambda x: x-{0}, [set(grid[i,:]) for i in xrange(len(grid))])
    column_sets = map(lambda x: x-{0}, [set(grid[:,i]) for i in xrange(len(grid))])
    square_sets = map(lambda x: x-{0}, [set((grid[3*i : 3*i+3  ,  3*j : 3*j+3].flatten())) for i in xrange(3) for j in xrange(3)])

    cell_sets = [{-1} if grid[x][y] != 0 else total_set - row_sets[x] - column_sets[y] - square_sets[3*(x/3) + (y/3)] for x in xrange(9) for y in xrange(9)]

    return cell_sets


def fix_singles(grid, cell_sets):
    """Find cells with just one feasible value and fix them. 
    Return false if not possible (thus the grid passed cannot be solved), true otherwise"""
    for i in xrange(9):
        for j in xrange(9):
            if len(cell_sets[9*i+j]) == 1 and (cell_sets[9*i+j] != {-1}): #if the cell has just one feasible value and has not been fixed yet
                grid[i][j] = cell_sets[9*i+j].pop() #set the cell to that value
                cell_sets[9*i+j].add(-1) #set the value of the cell as fixed
                if not remove_possibility(grid[i][j], i, j, cell_sets): #update the feasibility list
                    return False
    return True


def remove_possibility(elem, x, y, cell_sets):
    """Remove elem from the feasibility list of all the cell affected by the cell in (x,y). 
    Return false if that would lead to an infeasable grid, true otherwise"""
    for (i,j) in affected[x][y]:
        cell_sets[9*i+j] -= {elem}
        if not cell_sets[9*i+j]: #if a feasibility set become empty then the grid becomes infeasible
            return False
    return True


def check_fixed_values(grid):
    """Check whether grid has infeasible fixed values"""
    for r in xrange(9):
        for c in xrange(9):
            elem = grid[r][c]
            if elem != 0:
                grid[r][c] = 0
                if (in_row(elem, r, grid) or in_column(elem, c, grid) or in_square(elem,r,c,grid)):
                    grid[r][c] = elem
                    return False
                grid[r][c] = elem
    return True


def check_format(grid):
    """Check whether grid is a 9x9 array with elements in [0-9]"""
    if (len(grid) != 9):
        return False
    else:
        for row in grid:
            if len(row) !=9:
                return False
            for elem in row:
                if elem not in range(10):
                    return False
    return True


def solve_sudoku(grid, cell_sets, solution, x=0, y=0):
    """Try to solve the grid by backtracking assuming all the elements in cells (i,j) for i<x and j<y are already fixed"""    
    #find the first empty cell
    while(x<9 and grid[x][y] != 0):
        x = x + (y+1)/9
        y = (y+1)%9

    if(x>=9): #no more empy cells to fill
	solution.append(grid)
        return True

    #try to fill the cell
    for i in cell_sets[9*x+y]:
            new_cell_sets = copy.deepcopy(cell_sets)
            new_grid = grid.copy()
            new_grid[x][y] = i
            new_cell_sets[9*x+y] = {-1}
            if remove_possibility(i, x, y, new_cell_sets) and fix_singles(new_grid, new_cell_sets) and solve_sudoku(new_grid, new_cell_sets, solution, x + (y+1)/9, (y+1)%9):      #try to solve the rest of the grid given the cell x,y is fixed to i
                return True
    return False

def solve(grid):
    """Solve the sudoku puzzle. Return false if cannot be solved, true otherwise"""
    if not (check_format(grid) and check_fixed_values(grid)):
        return False
    
    solution = []
    cell_sets = feasibility_set(grid)

    if fix_singles(grid, cell_sets) and solve_sudoku(grid, cell_sets, solution):
        return solution[0]
    else:
        return false


def solve_test_file(filename):
    """Solve a batch of sudoku instances from a test file"""
    input_file = open(filename, 'r')
    for (i,line) in enumerate(input_file):
        print "\nSolving %d: %s" % (i, line[:-1])
        grid = string_to_grid(line[:-1])
        print "Initial grid: \n" + str(grid)
        grid = solve(grid)
        if grid is False:
            print "UNSOLVABLE sudoku"
        else:
            print "Final grid: \n" + str(grid)
            correct = check_fixed_values(grid) and not np.any(grid==0)
            if correct:
                print "The result is correct!"
            else:
                print "The result is WRONG!"
                return False
    return True

def print_usage():
        print "USAGE:\t./sudoku input output \nTESTING MODE:\t./sudoku -t {easy,hard}"

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print_usage()
    else:
        if (sys.argv[1] == "-t"):
            if (sys.argv[2] == "easy"):
                print "Test passed? " + str(solve_test_file("easy.txt"))
            elif sys.argv[2] == "hard":
                print "Test passed? " + str(solve_test_file("hard.txt"))
            else:
                print_usage()
        else:
            try:
                grid = np.genfromtxt(sys.argv[1], delimiter=',')
                grid = solve(grid)
                np.savetxt(sys.argv[2], grid, fmt='%d', delimiter=",")
            except IOError:
                print "Error opening " + sys.argv[1]
