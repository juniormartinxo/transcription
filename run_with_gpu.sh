#!/bin/bash

# Script to run the transcription API with GPU support
echo "🚀 Starting Transcription API with GPU support"
echo "=========================================="

# Activate virtual environment
source venv/bin/activate

# Check if PyTorch can use GPU
python -c "import torch; print(f'PyTorch version: {torch.__version__}'); print(f'CUDA available: {torch.cuda.is_available()}'); print(f'GPU devices: {torch.cuda.device_count()}')"

# Run the API
echo "Starting FastAPI server..."
python main.py