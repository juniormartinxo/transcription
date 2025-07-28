# Video to Audio Extraction & Automatic Transcription Feature

## Overview

This document describes the implementation of the video-to-audio extraction feature with automatic transcription generation in the FastAPI-based transcription service. The feature allows users to upload video files, extract audio, and automatically generate 4 different types of transcriptions.

## Implementation Summary

### Core Components

1. **VideoAudioExtractor Service** (`src/services/video_extractor.py`)
   - Handles video-to-audio conversion using FFmpeg
   - Supports multiple video formats: mp4, avi, mov, mkv, wmv, flv, webm, m4v, 3gp, mpg, mpeg
   - Extracts audio as WAV format (16kHz, mono, PCM 16-bit) - optimized for transcription
   - Includes video format validation and file size limits

2. **API Endpoint** (`src/api/routes/transcribe.py`)
   - New endpoint: `POST /transcribe/extract-audio`
   - Accepts video file uploads up to 500MB
   - Stores extracted audio in `public/audios/` directory
   - Automatically triggers 4 parallel transcription tasks

3. **Automatic Transcription Generation**
   - Generates 4 transcription variants for each video:
     - **Limpa**: Clean text only (`timestamps=false, diarization=false`)
     - **Timestamps**: Text with time markers (`timestamps=true, diarization=false`)
     - **Diarization**: Text with speaker separation (`timestamps=false, diarization=true`)
     - **Completa**: Full transcription with timestamps and speakers (`timestamps=true, diarization=true`)

### Technical Implementation Details

#### VideoAudioExtractor Class

```python
class VideoAudioExtractor:
    def __init__(self):
        self.supported_video_formats = {
            '.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', 
            '.webm', '.m4v', '.3gp', '.mpg', '.mpeg'
        }
    
    def extract_audio(self, video_path: str, output_path: str) -> bool:
        # Uses FFmpeg with specific parameters:
        # -vn: no video
        # -acodec pcm_s16le: WAV codec
        # -ar 16000: 16kHz sample rate
        # -ac 1: mono channel
```

#### API Endpoint Flow

1. **File Validation**
   - Check if file is a supported video format
   - Validate file size (max 500MB)
   - Store uploaded video temporarily

2. **Audio Extraction**
   - Use VideoAudioExtractor to convert video to WAV
   - Store audio in `public/audios/` with unique filename pattern: `{timestamp}_{random_hex}_{original_name}.wav`
   - Clean up temporary video file

3. **Automatic Transcription Generation**
   - Create 4 transcription tasks with different configurations
   - Each task gets unique ID with suffix: `{base_id}_{type}`
   - Tasks run in parallel using FastAPI BackgroundTasks

#### Response Format

```json
{
  "message": "Áudio extraído com sucesso e transcrições iniciadas",
  "audio_filename": "20250728_204147_57dfb096_video.wav",
  "audio_path": "public/audios/20250728_204147_57dfb096_video.wav",
  "file_size_bytes": 160574,
  "original_video": "video.mp4",
  "transcription_tasks": [
    {
      "task_id": "20250728_204147_57dfb096_limpa",
      "type": "limpa",
      "timestamps": false,
      "diarization": false,
      "status": "pending"
    },
    // ... 3 more tasks
  ],
  "total_transcriptions": 4
}
```

### File Organization

```
public/
├── audios/                    # Extracted audio files
│   └── {timestamp}_{hex}_{name}.wav
├── transcriptions/            # Generated transcription files
│   ├── {task_id}_transcricao_{timestamp}.txt (limpa)
│   ├── {task_id}_transcricao_{timestamp}.txt (timestamps)
│   ├── {task_id}_transcricao_{timestamp}.txt (diarization)
│   └── {task_id}_transcricao_{timestamp}.txt (completa)
└── videos/                    # Temporary video storage (cleaned up)
```

### Dependencies

- **FFmpeg**: Required for video-to-audio conversion
- **python-multipart**: For file upload handling
- **FastAPI BackgroundTasks**: For parallel transcription processing
- **Existing transcription stack**: WhisperX + PyAnnote.Audio

### Error Handling

1. **Video Format Validation**: Returns 400 with supported formats list
2. **File Size Validation**: Returns 400 if exceeds 500MB limit
3. **FFmpeg Errors**: Returns 500 with extraction failure message
4. **Transcription Errors**: Individual tasks can fail without affecting others
5. **Cleanup**: Temporary files are removed even on errors

## Usage Examples

### Basic Usage

```bash
curl -X POST "http://localhost:8000/transcribe/extract-audio" \
  -F "file=@video.mp4" \
  -H "Accept: application/json"
```

### Monitor Transcription Progress

```bash
# Check individual transcription status
curl "http://localhost:8000/transcribe/{task_id}"

# Download completed transcription
curl "http://localhost:8000/transcribe/{task_id}/download"
```

## Testing

A comprehensive test script was implemented (`test_multiple_transcriptions.py`) that:
- Creates synthetic test videos using FFmpeg
- Tests the complete workflow
- Monitors transcription progress
- Validates all 4 transcription types are generated
- Cleans up test files

### Test Results Example

- Input: 5-second test video with synthetic audio
- Output: 4 transcription files with different configurations
- Processing time: ~15 seconds for all transcriptions
- File sizes: 5-50 bytes (depending on content and format)

## Performance Considerations

1. **Parallel Processing**: All 4 transcriptions run simultaneously
2. **Memory Usage**: Each transcription loads models independently
3. **Storage**: Videos are temporarily stored, audio is permanent
4. **Processing Time**: Depends on video length and hardware (GPU/CPU)

## Future Improvements

### Short-term Enhancements

1. **Batch Processing**
   - Support multiple video uploads in single request
   - Queue management for large files

2. **Progress Tracking**
   - WebSocket connections for real-time progress updates
   - Percentage completion for each transcription type

3. **Output Formats**
   - Support for JSON, SRT, VTT transcription formats
   - Configurable output format per transcription type

4. **Quality Improvements**
   - Audio preprocessing (noise reduction, normalization)
   - Better speaker diarization accuracy
   - Language detection and multi-language support

### Medium-term Features

1. **Advanced Configuration**
   - Custom transcription parameters per request
   - Model switching (different Whisper model sizes)
   - Custom speaker diarization settings

2. **Integration Features**
   - Direct cloud storage upload (S3, GCS)
   - Webhook notifications when transcriptions complete
   - API key authentication for production use

3. **Analytics & Monitoring**
   - Processing time metrics
   - Success/failure rates
   - Resource usage monitoring

### Long-term Vision

1. **AI-Powered Features**
   - Automatic content summarization
   - Key topic extraction
   - Sentiment analysis
   - Translation to multiple languages

2. **Enterprise Features**
   - Multi-tenant support
   - Role-based access control
   - Audit logging
   - SLA guarantees

3. **Scalability**
   - Horizontal scaling with worker nodes
   - Load balancing for transcription tasks
   - Distributed processing across multiple GPUs

## Architecture Decisions

### Why 4 Transcription Types?

The decision to generate 4 automatic transcriptions addresses different use cases:
- **Limpa**: Clean text for content analysis, SEO, etc.
- **Timestamps**: For video editing, subtitle generation
- **Diarization**: For meeting notes, interview analysis
- **Completa**: For comprehensive video documentation

### Why Parallel Processing?

Parallel processing was chosen over sequential to:
- Reduce total processing time
- Better utilize available resources
- Provide faster user experience
- Allow independent failure handling

### Storage Strategy

- **Temporary videos**: Deleted after audio extraction to save space
- **Permanent audio**: Kept for potential re-transcription with different settings
- **Transcriptions**: Stored permanently for user access

## Known Issues & Limitations

1. **Video Format Support**: Limited to formats supported by FFmpeg
2. **File Size Limits**: 500MB limit may be restrictive for long videos
3. **No Progress Indication**: Users must poll for transcription status
4. **Single Language**: Currently optimized for Portuguese/English
5. **Resource Usage**: High memory usage during parallel processing

## Monitoring & Troubleshooting

### Log Locations
- Application logs: `logs/app.log` or `public/logs/app.log`
- Server logs: Check uvicorn output

### Common Issues
1. **FFmpeg not found**: Ensure FFmpeg is installed and in PATH
2. **CUDA issues**: Check GPU availability and drivers
3. **Disk space**: Monitor `public/` directory size
4. **Memory errors**: Reduce parallel transcription load

### Debug Commands
```bash
# Check FFmpeg installation
ffmpeg -version

# Check GPU availability
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"

# Monitor disk usage
df -h public/

# Check running transcriptions
curl "http://localhost:8000/transcribe/" | jq '.tasks[] | select(.status == "processing")'
```

---

*Last updated: 2025-07-28*
*Implementation completed during chat session focusing on video-to-audio extraction with automatic transcription generation.*