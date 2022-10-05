from flask import Flask, request, jsonify
import collections

app = Flask(__name__)

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

if __name__ == "__main__":
    app.run(debug=True)