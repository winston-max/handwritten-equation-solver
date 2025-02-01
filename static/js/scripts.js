const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
const clearButton = document.getElementById('clear');
const solveButton = document.getElementById('solve');
const equationDisplay = document.getElementById('equation');
const solutionDisplay = document.getElementById('solution');

let isDrawing = false;

// Set up drawing properties
ctx.lineWidth = 4;
ctx.lineCap = 'round';
ctx.strokeStyle = 'black';

// Function to start drawing
canvas.addEventListener('mousedown', (e) => {
    isDrawing = true;
    ctx.beginPath();
    ctx.moveTo(e.offsetX, e.offsetY);
});

// Function to draw while moving the mouse
canvas.addEventListener('mousemove', (e) => {
    if (isDrawing) {
        ctx.lineTo(e.offsetX, e.offsetY);
        ctx.stroke();
    }
});

// Function to stop drawing
canvas.addEventListener('mouseup', () => {
    isDrawing = false;
});

// Clear the canvas
clearButton.addEventListener('click', () => {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    equationDisplay.textContent = '';
    solutionDisplay.textContent = '';
});

// Send the canvas image to the backend for solving
solveButton.addEventListener('click', () => {
    const image = canvas.toDataURL('image/png');
    fetch('/solve', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ image: image }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert('Error: ' + data.error);
        } else {
            equationDisplay.textContent = data.equation;
            solutionDisplay.textContent = data.solution;
        }
    });
});