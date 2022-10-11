from crypt import methods
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import collections
import cv2
import numpy as np
from tensorflow.keras.models import load_model
import imutils

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
    classes = np.arange(0, 10)
    model = load_model('model/model-OCR.h5')
    input_size = 48

    image = request.files['image']

    def get_perspective(img, location, height = 900, width = 900):
        """Takes an image and location os interested region.
            And return the only the selected region with a perspective transformation"""
        pts1 = np.float32([location[0], location[3], location[1], location[2]])
        pts2 = np.float32([[0, 0], [width, 0], [0, height], [width, height]])

        # Apply Perspective Transform Algorithm
        matrix = cv2.getPerspectiveTransform(pts1, pts2)
        result = cv2.warpPerspective(img, matrix, (width, height))
        return result

    def get_InvPerspective(img, masked_num, location, height = 900, width = 900):
        """Takes original image as input"""
        pts1 = np.float32([[0, 0], [width, 0], [0, height], [width, height]])
        pts2 = np.float32([location[0], location[3], location[1], location[2]])

        # Apply Perspective Transform Algorithm
        matrix = cv2.getPerspectiveTransform(pts1, pts2)
        result = cv2.warpPerspective(masked_num, matrix, (img.shape[1], img.shape[0]))
        return result

    def find_board(img):
        """Takes an image as input and finds a sudoku board inside of the image"""
        # print(img)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        bfilter = cv2.bilateralFilter(gray, 13, 20, 20)
        edged = cv2.Canny(bfilter, 30, 180)
        keypoints = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours  = imutils.grab_contours(keypoints)

        newimg = cv2.drawContours(img.copy(), contours, -1, (0, 255, 0), 3)
        # cv2.imshow("Contour", newimg)


        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:15]
        location = None
        
        # Finds rectangular contour
        for contour in contours:
            approx = cv2.approxPolyDP(contour, 15, True)
            if len(approx) == 4:
                location = approx
                break
        result = get_perspective(img, location)
        return result, location


    # split the board into 81 individual images
    def split_boxes(board):
        """Takes a sudoku board and split it into 81 cells. 
            each cell contains an element of that board either given or an empty cell."""
        rows = np.vsplit(board,9)
        boxes = []
        for r in rows:
            cols = np.hsplit(r,9)
            for box in cols:
                box = cv2.resize(box, (input_size, input_size))/255.0
                # cv2.imshow("Splitted block", box)
                # cv2.waitKey(50)
                boxes.append(box)
        cv2.destroyAllWindows()
        return boxes

    def displayNumbers(img, numbers, color=(0, 255, 0)):
        """Displays 81 numbers in an image or mask at the same position of each cell of the board"""
        W = int(img.shape[1]/9)
        H = int(img.shape[0]/9)
        for i in range (9):
            for j in range (9):
                if numbers[(j*9)+i] !=0:
                    cv2.putText(img, str(numbers[(j*9)+i]), (i*W+int(W/2)-int((W/4)), int((j+0.7)*H)), cv2.FONT_HERSHEY_COMPLEX, 2, color, 2, cv2.LINE_AA)
        return img

    # Read image

    img = cv2.imread(image) #replace Image

    # extract board from input image
    board, location = find_board(img)

    # print("board",board)
    gray = cv2.cvtColor(board, cv2.COLOR_BGR2GRAY)
    # print(gray.shape)
    rois = split_boxes(gray)
    rois = np.array(rois).reshape(-1, input_size, input_size, 1)

    # get prediction
    prediction = model.predict(rois)
    # print(prediction)

    predicted_numbers = []
    # get classes from prediction
    for i in prediction: 
        index = (np.argmax(i)) # returns the index of the maximum number of the array
        predicted_number = classes[index]
        predicted_numbers.append(str(predicted_number))

    # reshape the list 

    board_num = np.array(predicted_numbers).astype('U').reshape(9, 9)

    res = board_num.tolist()

    for r in range(len(res)):
        for c in range(len(res)):
            if res[r][c] == "0":
                res[r][c] = "."

    return jsonify({"board": res})    

if __name__ == "__main__":
    app.run(debug=True)