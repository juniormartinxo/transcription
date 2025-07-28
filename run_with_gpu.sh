#!/bin/bash

# Script to run the transcription API with RTX 5070 Ti GPU support
echo "🚀 Starting Transcription API with RTX 5070 Ti GPU Support"
echo "=========================================="
echo "✅ Using PyTorch Nightly with CUDA 12.8 for RTX 5070 Ti compatibility"
echo ""

# Activate virtual environment
source venv/bin/activate

# Configure CUDA libraries path
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$(python -c "import nvidia.cudnn; print(nvidia.cudnn.__path__[0])")/lib

# Check GPU status
python -c "import torch; print(f'PyTorch version: {torch.__version__}'); print(f'CUDA available: {torch.cuda.is_available()}'); print(f'CUDA version: {torch.version.cuda}'); print(f'GPU devices: {torch.cuda.device_count()}'); print(f'GPU name: {torch.cuda.get_device_name(0)}')"
echo ""

# Run the API on port 8000 (back to original port)
echo "Starting FastAPI server on port 8000..."
python main.py