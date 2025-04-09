# Handwritten Mathematical Equation Solver

A deep learning-based system to recognize and solve handwritten mathematical equations using computer vision and symbolic computation.

## 📌 Overview

With the growing reliance on digital tools in education and communication, there is a rising demand for systems that can efficiently interpret handwritten mathematical content. This project aims to address that by providing a solution capable of:

- Recognizing handwritten mathematical characters and symbols.
- Forming valid equations from segmented character images.
- Solving:
  - Arithmetic equations
  - Systems of linear equations
  - Polynomial equations

## 🚀 Features

- ✍️ Handwriting recognition using a Convolutional Neural Network (CNN)
- 🧮 Symbolic solving using custom Python logic and libraries
- 🖼️ Image preprocessing and segmentation for accurate character extraction
- 📘 Educational use-case: Ideal for students to verify handwritten solutions
- 📝 Integration potential with digital note-taking apps

## 🛠️ Tech Stack

- Python
- TensorFlow / Keras
- OpenCV
- SymPy

## 🔍 How It Works

1. **Image Input**: User draws or uploads a handwritten equation.
2. **Preprocessing**: Image is cleaned, binarized, and segmented line-by-line and character-by-character.
3. **Character Recognition**: Each character is passed through a trained CNN model to predict its class.
4. **Equation Formation**: Recognized characters are combined to form a mathematical expression.
5. **Equation Solving**: The expression is parsed and solved using symbolic computation.
6. **Output**: The solution is displayed to the user.


