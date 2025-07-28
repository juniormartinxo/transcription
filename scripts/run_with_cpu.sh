#!/bin/bash

# Script to run the transcription API with CPU (for RTX 5070 Ti compatibility)
echo "🚀 Starting Transcription API with CPU mode"
echo "=========================================="
echo "ℹ️  Using CPU mode due to RTX 5070 Ti CUDA compatibility issues"
echo "ℹ️  This will still provide excellent transcription performance"
echo ""

# Activate virtual environment
source venv/bin/activate

# Check PyTorch status
python -c "import torch; print(f'PyTorch version: {torch.__version__}'); print(f'CUDA available: {torch.cuda.is_available()}'); print('Using CPU mode for compatibility')"

# Run the API
echo "Starting FastAPI server on port 8001..."
python main.py