from flask import Flask, render_template, request, jsonify
import cv2
import numpy as np
from tensorflow.keras.models import model_from_json
from sympy import symbols, Eq, sympify, SympifyError, I, re, im
from sympy import solve as sympy_solve
from PIL import Image
import base64
import io
import logging

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Load the model
def load_model():
    try:
        logging.info('Loading Model...')
        with open('model/model.json', 'r') as model_file:
            loaded_model_json = model_file.read()
        model = model_from_json(loaded_model_json)

        logging.info('Loading weights...')
        model.load_weights("model/model.weights.h5")
        return model
    except Exception as e:
        logging.error(f"An error occurred while loading the model: {e}")
        return None

model = load_model()
labels = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '+', '-', 'x', 'i']  # Added 'i' for imaginary unit

# Function to predict from an array
def predictFromArray(arr):
    try:
        result = np.argmax(model.predict(arr), axis=-1)
        return result
    except Exception as e:
        logging.error(f"An error occurred during prediction: {e}")
        return None


class Solver:
    def __init__(self, equation):
        self.equation = str(equation)
        self.leftEqu = []

    def convertEquationIntoGeneralForm(self):
        try:
            if '=' not in self.equation:
                logging.error("Equation does not contain '=' symbol.")
                return  # Exit if '=' is missing

            equalIndx = self.equation.index('=')
            leftSide = self.equation[:equalIndx]
            rightSide = self.equation[equalIndx + 1:]

            # Convert exponentiation from '^' to '**'
            leftSide = leftSide.replace('^', '**')
            rightSide = rightSide.replace('^', '**')

            # Move everything to the left side
            fullEquation = f"({leftSide}) - ({rightSide})"

            self.equation = fullEquation + "= 0"
            self.leftEqu = fullEquation  # Correctly formatted left-hand side

            # Debugging: Print the processed equation
            print("Equation after processing:", self.leftEqu)

        except Exception as e:
            logging.error(f"An error occurred while converting the equation: {e}")

    def solveEquation(self):
        try:
            self.convertEquationIntoGeneralForm()

            # Ensure leftEqu is not empty
            if not self.leftEqu.strip():
                logging.error("Equation is empty after processing.")
                return None

            # Debugging: Print before parsing
            print("Equation before sympify:", self.leftEqu)

            # Parse the equation into a SymPy expression
            x = symbols('x')  # Define the variable
            sympy_eq = Eq(sympify(self.leftEqu), 0)  # Create a SymPy equation

            # Debugging: Check SymPy equation format
            print("Parsed SymPy Equation:", sympy_eq)

            # Solve the equation (including complex roots)
            roots = sympy_solve(sympy_eq, x, dict=True)  # Get roots as a list of dictionaries
            simplified_roots = [root[x] for root in roots]  # Extract roots from dictionaries

            return simplified_roots

        except SympifyError as e:
            logging.error(f"SymPy could not parse the equation: {e}")
            return None
        except Exception as e:
            logging.error(f"An error occurred while solving the equation: {e}")
            return None


# Route to serve the webpage
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle equation solving
@app.route('/solve', methods=['POST'])
def solve():
    try:
        # Get the image data from the request
        image_data = request.json['image']
        image_data = base64.b64decode(image_data.split(',')[1])
        image = Image.open(io.BytesIO(image_data)).convert('L')  # Convert to grayscale
        image.save('canvas.jpg')

        # Process the image and predict the equation
        img = cv2.imread('canvas.jpg', cv2.IMREAD_GRAYSCALE)
        img = ~img
        ret, thresh = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
        ctrs, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnt = sorted(ctrs, key=lambda ctr: cv2.boundingRect(ctr)[0])
        img_data = []
        rects = []
        for c in cnt:
            x, y, w, h = cv2.boundingRect(c)
            rect = [x, y, w, h]
            rects.append(rect)
        final_rect = [i for i in rects]
        for r in final_rect:
            x, y, w, h = r[0], r[1], r[2], r[3]
            img = thresh[y:y+h+10, x:x+w+10]
            img = cv2.resize(img, (28, 28))
            img = np.reshape(img, (1, 28, 28))
            img_data.append(img)

        mainEquation = []
        for i in range(len(img_data)):
            img_data[i] = np.array(img_data[i])
            img_data[i] = img_data[i].reshape(-1, 28, 28, 1)
            result = predictFromArray(img_data[i])
            if result is None:
                return jsonify({'error': 'Prediction failed'})
            i = result[0]
            mainEquation.append(labels[i])

        StringEquation = ""
        for i in range(len(mainEquation)):
            a = mainEquation[i]
            if a.isdigit() == False and a.isalpha() == False and i < len(mainEquation)-1:
                if a == mainEquation[i+1] == '-':
                    StringEquation += '='
                else:
                    StringEquation += a
            if a.isalpha() == True:
                if i > 0:
                    if mainEquation[i-1].isdigit():
                        StringEquation += "*" + a
                    else:
                        StringEquation += a
                else:
                    StringEquation += a
            if a.isdigit() == True:
                if i > 0:
                    if mainEquation[i-1].isdigit():
                        StringEquation += a
                    elif mainEquation[i-1].isalpha():
                        StringEquation += "^" + a
                    else:
                        StringEquation += a
                else:
                    StringEquation += a

        newStr = ""
        l = list(StringEquation)
        for i in range(len(l)):
            if l[i] == "=":
                newStr = l[:i+1] + l[i+2:]
        equ = ""
        for i in newStr:
            equ += i

        # Debugging: Print the equation string
        logging.debug(f"Equation string: {equ}")

        # Check if the equation is valid
        if not equ or '=' not in equ:
            return jsonify({'error': 'Invalid equation format'})

        # Solve the equation
        solution = Solver(equ)
        roots = solution.solveEquation()
        if roots is None:
            return jsonify({'error': 'Failed to solve the equation'})

        # Format roots (only add imaginary part if it's non-zero)
        formatted_roots = []
        for root in roots:
            real_part = re(root)
            imag_part = im(root)
            if imag_part == 0:
                # Real root
                formatted_roots.append(str(real_part))
            else:
                # Complex root
                formatted_roots.append(f"{real_part} + {imag_part}i")

        str1 = ', '.join(formatted_roots)

        return jsonify({'equation': equ, 'solution': str1})
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
