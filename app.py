from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import collections

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return render_template('index.html')

@app.route("/input-board", methods=['POST'])
def input_board():
    suduko = []
    row1 = request.form.get('row1',type=list)
    row2 = request.form.get('row2',type=list)
    row3 = request.form.get('row3',type=list)
    row4 = request.form.get('row4',type=list)
    row5 = request.form.get('row5',type=list)
    row6 = request.form.get('row6',type=list)
    row7 = request.form.get('row7',type=list)
    row8 = request.form.get('row8',type=list)
    row9 = request.form.get('row9',type=list)
    suduko.append(row1)
    suduko.append(row2)
    suduko.append(row3)
    suduko.append(row4)
    suduko.append(row5)
    suduko.append(row6)
    suduko.append(row7)
    suduko.append(row8)
    suduko.append(row9)
    return jsonify({"board": suduko})

# check if sudoku is valid or not
@app.route("/isvalid", methods=['POST'])
def isvalid():
    board = request.get_json()
    board = board['board']

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
                return jsonify({"valid": False})
            
            # otherwise add it into row, col, and square
            cols[c].add(board[r][c])
            rows[r].add(board[r][c])
            squares[(r // 3, c // 3)].add(board[r][c])

    # valid suduko
    return jsonify({"valid": True})

# solve sudoku
@app.route("/solve", methods=['POST'])
def solveSudoku():
    board = request.get_json()
    board = board['board']

    helper(board, 0, 0)
    return jsonify({"solution": board})

def helper(board, row, col):
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
        if helper(board, nrow, ncol):
            return True
    else:
        # fill the place
        for i in range(1, 10):
            if isSafe(board, row, col, i):
                board[row][col] = str(i)
                if helper(board, nrow, ncol):
                    return True
                else:
                        board[row][col] = '.'
    return False

def isSafe(board, row, col, number):
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

# image input
@app.route("/image-input", methods=['POST'])
def imageInput():
    pass

if __name__ == "__main__":
    app.run(debug=True)