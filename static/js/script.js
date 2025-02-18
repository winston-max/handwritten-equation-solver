const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
const clearButton = document.getElementById('clear');
const solveButton = document.getElementById('solve');
const uploadButton = document.getElementById('uploadButton');
const uploadInput = document.getElementById('upload');
const equationDisplay = document.getElementById('equation');
const solutionDisplay = document.getElementById('solution');

let isDrawing = false;
let lastX = 0;
let lastY = 0;

// Set canvas background to white
ctx.fillStyle = 'white';
ctx.fillRect(0, 0, canvas.width, canvas.height);
ctx.strokeStyle = 'black';
ctx.lineWidth = 4;
ctx.lineCap = 'round';

// Mouse events
canvas.addEventListener('mousedown', (e) => {
    isDrawing = true;
    [lastX, lastY] = [e.offsetX, e.offsetY];
});
canvas.addEventListener('mousemove', draw);
canvas.addEventListener('mouseup', () => isDrawing = false);
canvas.addEventListener('mouseout', () => isDrawing = false);

// Touch events for mobile devices
canvas.addEventListener('touchstart', (e) => {
    isDrawing = true;
    const touch = e.touches[0];
    const rect = canvas.getBoundingClientRect();
    [lastX, lastY] = [touch.clientX - rect.left, touch.clientY - rect.top];
});
canvas.addEventListener('touchmove', (e) => {
    if (!isDrawing) return;
    const touch = e.touches[0];
    const rect = canvas.getBoundingClientRect();
    draw({ offsetX: touch.clientX - rect.left, offsetY: touch.clientY - rect.top });
});
canvas.addEventListener('touchend', () => isDrawing = false);

// Draw function
function draw(e) {
    if (!isDrawing) return;
    ctx.beginPath();
    ctx.moveTo(lastX, lastY);
    ctx.lineTo(e.offsetX, e.offsetY);
    ctx.stroke();
    [lastX, lastY] = [e.offsetX, e.offsetY];
}

// Clear canvas
clearButton.addEventListener('click', () => {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = 'white';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    equationDisplay.textContent = '';
    solutionDisplay.textContent = '';
});

// Solve equation
solveButton.addEventListener('click', solveEquation);

// Upload image
uploadButton.addEventListener('click', () => {
    uploadInput.click();
});

uploadInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = (event) => {
            const img = new Image();
            img.onload = () => {
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
                solveEquation();
            };
            img.src = event.target.result;
        };
        reader.readAsDataURL(file);
    }
});

function solveEquation() {
    const image = canvas.toDataURL();
    fetch('/solve', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ image }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            equationDisplay.textContent = 'Invalid Equation';
            solutionDisplay.textContent = data.error;
        } else {
            equationDisplay.textContent = data.equation;
            solutionDisplay.textContent = data.solution;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        equationDisplay.textContent = 'Error';
        solutionDisplay.textContent = 'Failed to solve the equation.';
    });
}
