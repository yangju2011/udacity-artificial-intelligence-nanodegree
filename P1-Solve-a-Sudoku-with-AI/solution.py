assignments = []

rows = 'ABCDEFGHI'
cols = '123456789'

def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [s+t for s in A for t in B]
    pass

boxes = cross(rows, cols)
row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
# add diagonal unit
diag_units = [[rows[i] + cols[i] for i in range(len(rows))],[rows[i] + cols[-i-1] for i in range(len(rows))]]

unitlist = row_units + column_units + square_units + diag_units
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)

def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """

    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values


def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """
    old_values = values.copy()
    for unit in unitlist:
        twins = None
        twos = [s for s in unit if len(values[s]) == 2] 
        i = 0 
        while i < len(twos):
            j = i + 1
            while j < len(twos):
                if values[twos[i]] == values[twos[j]]:
                    # remove from this unit only
                    twins = values[twos[i]] # remove this val from all other member in this unit  
                    for s in unit: # the same unit, for all boxes
                        val2 = values[s]
                        if val2 != twins:
                            for i in twins: # '23'
                                val2 = val2.replace(i,'') # remove twins from candidate
                            values = assign_value(values, s, val2)                  
                    if old_values != values: # different values
                        return values # break the loop and return the updated value
                    else: # updated value is the same old value, no update, move to the next unit
                        break
                j += 1    
            if twins: # dentify twins, but nothing returned, indicating no update
                break
            i += 1                   
    # if after go through everything, still the same, means no more twins
    return old_values

    
def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    assert len(grid) == 81
    grids = dict(zip(boxes,grid))
    for s in grids:
        if grids[s] == '.': # empty boxes:
            grids[s] = '123456789'
    return grids           
    pass

def display(values):
    """
    Display the values as a 2-D grid.
    Input: The sudoku in dictionary form
    Output: None
    """
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    return

def eliminate(values):
    """
    Go through all the boxes, and whenever there is a box with a value, eliminate this value from the values of all its peers.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    filled_cells = [s for s in values if len(values[s]) == 1] #solved box and value
    empty_cells = [s for s in values if len(values[s]) > 1]
    for s in empty_cells:
        filled_peer_cells = [c for c in peers[s] if c in filled_cells]
        peer_value = ''.join([values[c] for c in filled_peer_cells]) # 1-9, v.s. 2345, solved values
        val = values[s]
        for i in peer_value:
            val = val.replace(i,'')
        values = assign_value(values, s, val)
    return values
    pass

def only_choice(values):
    """
    Go through all the units, and whenever there is a unit with a value that only fits in one box, assign the value to this box.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    for unit in unitlist: 
        digit_count = {}
        for s in unit:
            val = values[s]
            for i in val:
                if i not in digit_count:
                    digit_count[i] = 1
                else:
                    digit_count[i] += 1
        for d in digit_count:
            if digit_count[d] == 1: # appear only once
                for s in unit:
                    if d in values[s]:
                        values = assign_value(values, s, d)
    return values

def reduce_puzzle(values):
    """
    Iterate eliminate() and only_choice(). If at some point, there is a box with no available values, return False.
    If the sudoku is solved, return the sudoku.
    If after an iteration of both functions, the sudoku remains the same, return the sudoku.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    stalled = False
    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])

        values = eliminate(values)
        values = only_choice(values)
        values = naked_twins(values)
        
        # Check how many boxes have a determined value, to compare
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after
        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values

def search(values):
    "Using depth-first search and propagation, create a search tree and solve the sudoku."
    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)
    if values is False:
        return False # recurive param called attemp
    else:
        unsolved = [box for box in values.keys() if len(values[box]) > 1]
        if len(unsolved) == 0:
            return values
        else:
            box = sorted(unsolved, key = lambda s: len(values[s]))[0] 
            
            # Now use recursion to solve each one of the resulting sudokus, and if one returns a value (not False), return that answer!
            for val in values[box]: #'89',one by one solve
                new_values = values.copy() # use copy to get the new values
                new_values = assign_value(new_values, box, val)
                attemp = search(new_values)
                if attemp: 
                    return attemp # return in the loop will stop the loop

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    solution = search(grid_values(grid)) #make sure only 1 number in each unit
    for unit in unitlist:
        values = sorted([solution[s] for s in unit])
        if values != ['1','2','3','4','5','6','7','8','9']:
            return False
    return solution # only when all units satisfy 


if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
