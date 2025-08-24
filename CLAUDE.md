# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a full-stack audio transcription application with a FastAPI backend and Next.js frontend. The backend uses WhisperX for speech-to-text and PyAnnote.Audio for speaker diarization, running background transcription tasks with support for both CPU and GPU execution including special RTX 5070 Ti compatibility. The frontend provides a modern React interface for uploading files and managing transcriptions.

## Directory Structure

The project is organized with separate directories for API and frontend:
```
.
├── api/                    # Backend API (FastAPI)
│   ├── main.py            # API entry point
│   ├── requirements.txt   # Python dependencies  
│   ├── src/               # API source code
│   ├── venv/              # Python virtual environment
│   ├── scripts/           # Setup and utility scripts
│   └── Dockerfile         # API container build
├── frontend/              # Frontend (Next.js)
│   ├── src/               # React components and pages
│   ├── package.json       # Node.js dependencies
│   └── Dockerfile         # Frontend container build
├── public/                # Shared data directory
│   ├── audios/            # Uploaded audio files
│   ├── transcriptions/    # Generated transcriptions
│   └── videos/            # Uploaded video files
├── logs/                  # Application logs
└── docker-compose.yml     # Container orchestration
```

## Common Commands

### Full Stack Development
```bash
# Run both backend and frontend simultaneously (recommended)
python run_full_stack.py              # Starts API + Next.js frontend

# Backend only (FastAPI) - With Hot Reload
cd api && python run_local.py         # Auto-setup and run with hot reload
cd api && python run_venv.py          # Auto-setup with venv and hot reload
cd api && python run_dev.py           # Development server with hot reload
cd api && ./dev.sh                    # Quick development server (bash)
cd api && ./scripts/setup_local.sh    # Manual setup only
cd api && ./scripts/setup_venv.sh     # Manual venv setup only
cd api && source venv/bin/activate    # Activate existing venv

# Frontend only (Next.js)
cd frontend && npm run dev             # Development server (with Turbopack)
cd frontend && npm run build          # Production build (with Turbopack)  
cd frontend && npm start              # Start production server
cd frontend && npm run lint           # ESLint checking

# Docker (isolated deployment)
docker-compose up --build             # Build and run containerized
docker-compose up -d                  # Run in background
docker-compose logs -f transcriber    # View logs
```

### GPU/CPU Execution
```bash
# GPU execution with RTX 5070 Ti support
cd api && ./scripts/run_with_gpu.sh   # Requires PyTorch Nightly
cd api && ./scripts/setup_rtx5070ti.sh # Setup RTX 5070 Ti compatibility

# CPU fallback (always works)
cd api && ./scripts/run_with_cpu.sh   # Force CPU mode
```

### Runtime Commands
```bash
# Start API server
cd api && python main.py              # Direct execution
cd api && uvicorn main:app --host 0.0.0.0 --port 8000 --reload  # With reload

# Check status
curl http://localhost:8000/health     # Health check
curl http://localhost:8000/docs       # API documentation

# Test transcription
curl -X POST "http://localhost:8000/transcribe/" -F "file=@audio.wav"

# Extract audio from video and transcribe
curl -X POST "http://localhost:8000/transcribe/extract-audio" -F "file=@video.mp4"
```

### Testing and Debugging
```bash
# View logs
tail -f logs/app.log                  # Application logs
tail -f public/logs/app.log           # Alternative log location

# Check GPU status
cd api && python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"
cd api && python check_gpu.py         # GPU compatibility check

# Debug Docker
docker-compose exec transcriber bash  # Shell into container
docker-compose logs transcriber       # Container logs

# Fix permissions if needed
cd api && ./scripts/fix_permissions.sh # Fix directory/file permissions
```

## Architecture

### Full Stack Architecture
This is a full-stack application with separate backend and frontend components:
- **Backend**: FastAPI service (`api/main.py`) running on port 8000
- **Frontend**: Next.js React application (`frontend/`) running on port 3000
- **Communication**: REST API endpoints with CORS enabled for cross-origin requests
- **Development**: Can run independently or together using `run_full_stack.py`

### Backend Service Layer
- **TranscriptionService** (`api/src/services/transcription.py`): Orchestrates transcription tasks, manages persistence in JSON file, handles background processing
- **AudioTranscriber** (`api/src/services/audio_transcriber.py`): Wraps WhisperX and PyAnnote models, handles device selection (CPU/GPU), manages model loading and caching
- **VideoAudioExtractor** (`api/src/services/video_extractor.py`): Extracts audio from video files using FFmpeg, supports multiple video formats
- **VideoFrameExtractor** (`api/src/services/video_frame_extractor.py`): Extracts frames from video files for visual analysis

### Frontend Architecture
- **Framework**: Next.js 15.5.0 with React 19.1.0 and TypeScript
- **Styling**: TailwindCSS 4.x with PostCSS for utility-first styling
- **Components**: Modular React components in `frontend/src/components/`
- **API Integration**: Axios for HTTP requests to backend API (`frontend/src/lib/api.ts`)
- **Build System**: Turbopack for fast development and production builds
- **Linting**: ESLint with Next.js and TypeScript configurations

### Configuration Architecture
- **AppConfig** (`api/src/config/config.py`): Pydantic-based configuration with environment variable loading, includes ModelSize enum and path helpers
- **Environment Loading**: Uses python-dotenv with fallback defaults, supports both .env files and direct environment variables

### Task Management
- **Background Processing**: FastAPI BackgroundTasks for non-blocking transcription
- **Task Persistence**: JSON-based storage in `public/transcriptions/tasks.json` with fallback to temp directory
- **Task States**: PENDING → PROCESSING → COMPLETED/FAILED with datetime tracking
- **Task Schema**: Pydantic models in `api/src/models/schemas.py` with proper serialization

### API Layer Structure
- **Route Organization**: Separate routers for `/transcribe` and `/health` endpoints
- **Dependency Injection**: FastAPI Depends() pattern for service instantiation
- **Error Handling**: Consistent HTTPException usage with detailed logging
- **File Validation**: Content-type and extension checking with size limits (100MB audio, 500MB video)
- **Video Support**: `/transcribe/extract-audio` endpoint automatically creates 4 transcriptions with different configurations
- **Frame Extraction**: `/transcribe/extract-frames` endpoint for extracting video frames

### Logging Architecture
- **Global Logger Setup**: Centralized configuration in `api/src/core/logger_config.py`
- **Colored Formatting**: Custom ColoredFormatter for development visibility
- **Module-specific Loggers**: `get_logger(__name__)` pattern throughout codebase
- **Dual Output**: Console (colored) + file logging with UTF-8 encoding

## Key Implementation Details

### GPU Compatibility Handling
The service has sophisticated device selection logic in AudioTranscriber:
- Automatic CUDA detection with force_cpu override
- RTX 5070 Ti requires PyTorch Nightly due to sm_120 architecture
- TF32 optimization enabled for compatible GPUs
- Warning suppression for known compatibility issues

### File Processing Flow
1. **Upload Validation**: Size limits (100MB for audio, 500MB for video), content-type flexibility (accepts both MIME and extension)
2. **Task Creation**: Unique task_id with timestamp and random hex
3. **Background Processing**: WhisperX transcription + PyAnnote diarization
4. **Result Storage**: Text files in `public/transcriptions/` with task status updates

### Video Processing Flow
1. **Video Upload**: Accepts common formats (.mp4, .avi, .mov, .mkv, etc.)
2. **Audio Extraction**: FFmpeg converts to WAV (16kHz, mono)
3. **Auto-Transcription**: Creates 4 versions automatically:
   - `limpa`: No timestamps, no diarization (clean text)
   - `timestamps`: With timestamps, no diarization
   - `diarization`: No timestamps, with speaker identification
   - `completa`: Full features (timestamps + diarization)
4. **Cleanup**: Removes temporary video file after extraction

### Model Management
Models are lazy-loaded and cached in the AudioTranscriber instance:
- WhisperX models downloaded to `cache/huggingface/`
- PyAnnote pipeline requires HuggingFace token and model acceptance
- Compute type automatically selected (float16 for GPU, int8 for CPU)

### Docker Architecture
- **Multi-stage Build**: python:3.10-slim base with system dependencies
- **Non-root Execution**: appuser for security
- **Volume Strategy**: Bind mounts for development, named volumes for caches
- **Health Checks**: Curl-based endpoint monitoring
- **Resource Limits**: 4GB memory limit with 2GB reservation

## Environment Configuration

### Required Variables
```bash
HUGGING_FACE_HUB_TOKEN=<token>        # Required for PyAnnote models
```

### Optional Variables (with defaults)
```bash
VERSION_MODEL=turbo                   # whisperx model size
FORCE_CPU=false                       # force CPU over GPU
LOG_LEVEL=INFO                        # logging verbosity
AUDIOS_DIR=./public/audios           # upload directory
TRANSCRIPTIONS_DIR=./public/transcriptions  # output directory
LOG_FILE=./public/logs/app.log       # log file path
```

## Deployment Considerations

### RTX 5070 Ti Compatibility
This hardware requires PyTorch Nightly (2.9.0.dev+cu128) due to CUDA sm_120 architecture. The regular PyTorch (2.7.1) only supports up to sm_90. Scripts handle this automatically.

### Production Deployment
- Use `python run_venv.py` for isolated dependencies
- Set `FORCE_CPU=false` only if GPU is properly configured
- Monitor `logs/app.log` for model loading and transcription status
- HuggingFace models download on first use (requires internet)

### Development Workflow
- Use `./run_dev.sh` for full development (backend + frontend) - **RECOMMENDED**
- Use `python run_full_stack.py` for full development alternative
- Use `cd api && python run_local.py` for backend-only development  
- Use `cd api && venv/bin/python main.py` for manual backend startup
- Use `cd frontend && npm run dev` for frontend-only development
- Check `/health` endpoint for service status (backend)
- Access frontend at `http://localhost:3000`
- Test with small audio files first (model loading takes time)
- Use `/docs` endpoint for interactive API testing
- Test video extraction with `/transcribe/extract-audio` endpoint

### Troubleshooting Scripts
- If `run_dev.sh` fails with Python path errors, ensure you're using the corrected version
- Backend logs are saved to `backend.log` in root directory
- Frontend logs are saved to `frontend.log` in root directory  
- Use `curl http://localhost:8000/health` and `curl http://localhost:3000/api/health` to test endpoints

## API Endpoints

### Backend API Endpoints (Port 8000)
- `POST /transcribe/`: Upload audio file for transcription
- `GET /transcribe/{task_id}`: Check transcription status
- `GET /transcribe/{task_id}/download`: Download completed transcription
- `GET /transcribe/`: List all transcription tasks
- `POST /transcribe/extract-audio`: Extract audio from video and auto-transcribe (4 versions)
- `POST /transcribe/extract-frames`: Extract frames from video files
- `POST /transcribe/{task_id}/cancel`: Cancel a running transcription
- `DELETE /transcribe/{task_id}`: Delete transcription task and files
- `GET /transcribe/{task_id}/files`: Get task file information
- `GET /health`: Service health check

### Frontend URLs (Port 3000)
- `http://localhost:3000/`: Main dashboard with file upload and task management
- `http://localhost:3000/api/health`: Frontend health check endpoint
- Interactive UI for uploading audio/video files and monitoring transcriptions

## Recent Improvements and Fixes

### Multiple File Upload Implementation (August 2024)
- ✅ **Batch Upload Support**: Implemented multiple file upload functionality for both audio and video files
- ✅ **Backend Batch Endpoints**: Added `/transcribe/batch-audio` and `/transcribe/batch-video` endpoints
- ✅ **Frontend UI**: Updated FileUploader component to handle multiple files with individual progress tracking
- ✅ **Dashboard Integration**: Enhanced TranscriptionDashboard with batch task support and visual indicators

### Performance Optimizations (August 2024)
- ✅ **Fixed Critical Polling Bug**: Resolved "Cannot access 'intervalId' before initialization" error causing frontend freezing during uploads
- ✅ **Optimized Progress Updates**: Added throttling and debouncing to progress callbacks (50ms debounce, 1% threshold)
- ✅ **Adaptive Polling**: Implemented smart polling intervals (5s for ≤5 tasks, 10s for >5 tasks)
- ✅ **Reduced Re-renders**: Optimized state updates to prevent unnecessary component re-renders
- ✅ **Integer Progress Display**: Progress percentages now show as integers instead of decimals

### Video Processing Enhancements (August 2024)
- ✅ **Consistent Transcription Creation**: Fixed batch video upload to create all 4 transcription types (limpa, timestamps, diarization, completa) like individual uploads
- ✅ **Folder Naming Cleanup**: Removed "batch_video_" prefix from automatically generated folder names
- ✅ **Improved Error Handling**: Enhanced error reporting and fallback mechanisms for batch operations

### Docker Implementation (August 2024)
- ✅ **Full-Stack Docker Setup**: Complete containerization with separate frontend and backend containers
- ✅ **Production-Ready Configuration**: Optimized Dockerfiles with multi-stage builds, non-root users, and security hardening
- ✅ **Development Support**: Docker Compose with hot-reload volumes for development workflow
- ✅ **Automated Setup**: Added `docker-start.sh` script for easy initialization with health checks
- ✅ **Documentation**: Comprehensive README.Docker.md with troubleshooting and best practices

### Directory Structure Separation (August 2024)
- ✅ **API/Frontend Separation**: Restructured project into separate `./api/` and `./frontend/` directories
- ✅ **Backend Migration**: Moved all Python/FastAPI files to `api/` directory (main.py, src/, requirements.txt, venv/, scripts/)
- ✅ **Configuration Updates**: Updated docker-compose.yml, run scripts, and configuration paths for new structure
- ✅ **Script Corrections**: Fixed `run_dev.sh` and `run_full_stack.py` to work with separated directories
- ✅ **Path Adjustments**: Updated API config to use relative paths (`../public/`) for shared data directories
- ✅ **Documentation Updates**: Revised all commands and paths in CLAUDE.md to reflect new structure

### Script Path Resolution Fixes (August 2024)
- ✅ **run_dev.sh Python Path Issue**: Fixed incorrect Python path resolution when executing from root but needing to run in `api/` directory
- ✅ **Directory Navigation Bug**: Resolved frontend startup failure due to incorrect directory context after backend initialization
- ✅ **Virtual Environment Detection**: Improved venv path detection to work correctly with new `api/venv/` location
- ✅ **Absolute Path Usage**: Implemented `CURRENT_DIR` variable usage to prevent directory navigation issues
- ✅ **Debug Logging**: Added Python command logging to help troubleshoot path resolution problems

## Docker Usage

### Quick Start
```bash
# Copy environment template and configure
cp .env.example .env
# Edit .env and add your HUGGING_FACE_HUB_TOKEN

# Easy startup with automated checks
./docker-start.sh

# Or manual startup
docker compose up --build -d

# Production deployment
docker compose -f docker-compose.prod.yml up -d --build
```

### Docker Architecture
- **Backend**: FastAPI container (port 8000) with WhisperX and PyAnnote
- **Frontend**: Next.js container (port 3000) with React interface  
- **Networking**: Isolated bridge network for secure service communication
- **Volumes**: Persistent data storage + optimized caching for models
- **Security**: Non-root users, no-new-privileges, security-hardened containers

### Container URLs
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000  
- **API Documentation**: http://localhost:8000/docs
- **Health Checks**: Automatic monitoring with 30s intervals

## Important Bug Fixes

### Frontend Freezing Issue (Fixed August 2024)
**Problem**: Frontend would freeze completely when uploading multiple files (especially 6+ videos)
**Root Cause**: Variable scoping issue in polling function - `intervalId` referenced before initialization
**Solution**: Restructured polling logic with proper variable initialization and cleanup

### Inconsistent Transcription Creation (Fixed August 2024) 
**Problem**: Batch video uploads only created "limpa" transcription, while individual uploads created all 4 types
**Root Cause**: Batch endpoint used simplified logic instead of mirroring individual endpoint behavior
**Solution**: Updated batch processing to create all 4 transcription variants (limpa, timestamps, diarization, completa)

### Performance Issues (Fixed August 2024)
**Problem**: UI became unresponsive during file uploads due to excessive progress updates
**Root Cause**: Progress callbacks firing for every small increment without throttling
**Solution**: Implemented debouncing (50ms), throttling (1% threshold), and optimized state updates

## Technical Debt and Maintenance

### Code Quality Improvements
- Implemented proper error boundaries and loading states
- Added TypeScript strict typing throughout the application  
- Optimized API calls with proper retry mechanisms and timeout handling
- Enhanced logging with structured formats and appropriate levels

### Performance Monitoring
- Real-time progress tracking for individual and batch uploads
- Memory usage optimization with proper cleanup of event listeners
- Efficient polling strategies that adapt to system load
- Optimized Docker resource allocation (6GB backend, 1GB frontend)

### Security Enhancements  
- Container security hardening with non-root users
- Proper secrets management for API tokens
- CORS configuration for secure cross-origin requests
- File validation and size limits to prevent abuse