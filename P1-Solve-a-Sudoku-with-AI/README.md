- Implement "naked twins" strategy and solve a diagonal sudoku based on AIND's code from https://github.com/udacity/aind-sudoku

- Question 1 (Naked Twins)
Q: How do we use constraint propagation to solve the naked twins problem?  
A:
1. Go through each unit from the unitlist.
2. In a given unit, first identify boxes with the value that has 2 candidate digits. Within these boxes, check if any two boxes have identical values. If there are a pair of naked twins in a unit, remove each of the twins digits from all other boxes which have more than 2 candidate digits in this unit.
3. After eliminating naked twins in this unit, if the new sodoku is the same as the old sodoku, it means nothing is modified in this unit, then we can go to the next unit and repeat step 2.
4. If the new sodoku is different from the old sodoku, it means we have eliminated from other boxes in this unit. In this case, return the new sodoku dictionary

- Question 2 (Diagonal Sudoku)
Q: How do we use constraint propagation to solve the diagonal sudoku problem?  
A: All we need to do is to add 2 more units representing the diagonal unit to unitlist. For each unit in unitlist, we need to make sure sodoku's rule is satisfied. diag_units = [['A1', 'B2', 'C3', 'D4', 'E5', 'F6', 'G7', 'H8', 'I9'], ['A9', 'B8', 'C7', 'D6', 'E5', 'F4', 'G3', 'H2', 'I1']]
