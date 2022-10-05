class Solver():    
    def solveSudoku(self, board):
        self.helper(board, 0, 0)

    def helper(self, board, row, col):
        if row == len(board):
            return True
            
        nrow = 0
        ncol = 0
        
        if col == len(board)-1:
            nrow = row + 1
            ncol = 0
        
        else:
            nrow = row
            ncol = col + 1
        
        if board[row][col] != '.':
            if self.helper(board, nrow, ncol):
                return True
        else:
            # fill the place
            for i in range(1, 10):
                if self.isSafe(board, row, col, i):
                    board[row][col] = str(i)
                    if self.helper(board, nrow, ncol):
                        return True
                    else:
                            board[row][col] = '.'
        return False

    def isSafe(self, board, row, col, number):
        # column
        for i in range(len(board)):
            if board[i][col] == str(number):
                return False

        # row
        for j in range(len(board)):
            if board[row][j] == str(number):
                return False

        # grid
        sr = 3 * (row//3)
        sc = 3 * (col//3)

        for i in range(sr, sr+3):
            for j in range(sc, sc+3):
                if board[i][j] == str(number):
                    return False
        
        return True
        
board = [["5","3",".",".","7",".",".",".","."],["6",".",".","1","9","5",".",".","."],[".","9","8",".",".",".",".","6","."],["8",".",".",".","6",".",".",".","3"],["4",".",".","8",".","3",".",".","1"],["7",".",".",".","2",".",".",".","6"],[".","6",".",".",".",".","2","8","."],[".",".",".","4","1","9",".",".","5"],[".",".",".",".","8",".",".","7","9"]]

print("Before solving")
for row in board:
    print(row)

print()
solver = Solver()
solver.solveSudoku(board)

print("After solving")
for row in board:
    print(row)
