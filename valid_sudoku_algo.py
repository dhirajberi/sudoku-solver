import collections
def isValidSudoku(board):
    cols = collections.defaultdict(set)
    rows = collections.defaultdict(set)
    squares = collections.defaultdict(set)  # key = (r /3, c /3)

    for r in range(9):
        for c in range(9):
            # skip if it's empty cell
            if board[r][c] == ".":
                continue
                
            # if element is present in row, col or square then return false, it's not valid suduko.
            if (board[r][c] in rows[r] or board[r][c] in cols[c] or board[r][c] in squares[(r // 3, c // 3)]):
                return False
            
            # otherwise add it into row, col, and square
            cols[c].add(board[r][c])
            rows[r].add(board[r][c])
            squares[(r // 3, c // 3)].add(board[r][c])

    # valid suduko
    return True
