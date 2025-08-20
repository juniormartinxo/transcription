'use client';

import React, { useCallback, useState } from 'react';
import { Upload, FileAudio, Video, Image, X, CheckCircle, AlertCircle } from 'lucide-react';
import { TranscriptionAPI, formatFileSize } from '@/lib/api';
import { TranscriptionTask, TranscriptionRequest, UploadProgress, VideoExtractionResponse, FrameExtractionResponse } from '@/lib/types';

interface FileUploaderProps {
  onUploadComplete?: (result: unknown) => void;
  onTaskCreated?: (task: TranscriptionTask) => void;
}

type UploadMode = 'audio' | 'video' | 'frames';

const FileUploader: React.FC<FileUploaderProps> = ({ onUploadComplete, onTaskCreated }) => {
  const [dragActive, setDragActive] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<UploadProgress>({ loaded: 0, total: 0, percentage: 0 });
  const [uploadMode, setUploadMode] = useState<UploadMode>('audio');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadResult, setUploadResult] = useState<TranscriptionTask | VideoExtractionResponse | FrameExtractionResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [autoModeMessage, setAutoModeMessage] = useState<string | null>(null);

  // Configurações para transcrição de áudio
  const [audioOptions, setAudioOptions] = useState<TranscriptionRequest>({
    include_timestamps: true,
    include_speaker_diarization: true,
    output_format: 'txt',
    version_model: 'turbo',
    force_cpu: false,
  });

  // Configurações para extração de frames
  const [frameOptions, setFrameOptions] = useState({
    fps: 1.0,
    interval_seconds: undefined as number | undefined,
    extract_keyframes: false,
    format: 'jpg',
    quality: 2,
  });

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      
      // Auto-detecta o modo baseado no tipo de arquivo
      const isVideoFile = file.type.startsWith('video/') || 
                         ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.wmv', '.flv', '.3gp', '.m4v']
                           .some(ext => file.name.toLowerCase().endsWith(ext));
      
      const isAudioFile = file.type.startsWith('audio/') ||
                         ['.wav', '.mp3', '.ogg', '.m4a', '.flac', '.aac']
                           .some(ext => file.name.toLowerCase().endsWith(ext));
      
      // Auto-seleciona o modo apropriado
      if (isVideoFile && uploadMode === 'audio') {
        setUploadMode('video');
        setAutoModeMessage('Arquivo de vídeo detectado! Modo alterado automaticamente para "Transcrever Vídeo".');
      } else if (isAudioFile && (uploadMode === 'video' || uploadMode === 'frames')) {
        setUploadMode('audio');
        setAutoModeMessage('Arquivo de áudio detectado! Modo alterado automaticamente para "Transcrever Áudio".');
      } else {
        setAutoModeMessage(null);
      }
      
      setSelectedFile(file);
      setError(null);
      setUploadResult(null);
    }
  }, [uploadMode]);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      
      // Auto-detecta o modo baseado no tipo de arquivo
      const isVideoFile = file.type.startsWith('video/') || 
                         ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.wmv', '.flv', '.3gp', '.m4v']
                           .some(ext => file.name.toLowerCase().endsWith(ext));
      
      const isAudioFile = file.type.startsWith('audio/') ||
                         ['.wav', '.mp3', '.ogg', '.m4a', '.flac', '.aac']
                           .some(ext => file.name.toLowerCase().endsWith(ext));
      
      // Auto-seleciona o modo apropriado
      if (isVideoFile && uploadMode === 'audio') {
        setUploadMode('video');
        setAutoModeMessage('Arquivo de vídeo detectado! Modo alterado automaticamente para "Transcrever Vídeo".');
      } else if (isAudioFile && (uploadMode === 'video' || uploadMode === 'frames')) {
        setUploadMode('audio');
        setAutoModeMessage('Arquivo de áudio detectado! Modo alterado automaticamente para "Transcrever Áudio".');
      } else {
        setAutoModeMessage(null);
      }
      
      setSelectedFile(file);
      setError(null);
      setUploadResult(null);
    }
  };

  const resetUpload = () => {
    setSelectedFile(null);
    setUploadResult(null);
    setError(null);
    setAutoModeMessage(null);
    setUploadProgress({ loaded: 0, total: 0, percentage: 0 });
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setUploading(true);
    setError(null);

    try {
      const onProgress = (progress: UploadProgress) => {
        setUploadProgress(progress);
      };

      let result;

      // Detecta automaticamente se é vídeo baseado no tipo de arquivo
      const isVideoFile = selectedFile.type.startsWith('video/') || 
                         ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.wmv', '.flv', '.3gp', '.m4v']
                           .some(ext => selectedFile.name.toLowerCase().endsWith(ext));

      // Força o modo correto baseado no tipo do arquivo
      if (uploadMode === 'audio' && isVideoFile) {
        setError('Arquivo de vídeo detectado! Use o modo "Transcrever Vídeo" para arquivos de vídeo.');
        return;
      }

      if ((uploadMode === 'video' || uploadMode === 'frames') && !isVideoFile) {
        setError('Arquivo de áudio detectado! Use o modo "Transcrever Áudio" para arquivos de áudio.');
        return;
      }

      switch (uploadMode) {
        case 'audio':
          result = await TranscriptionAPI.uploadAudio(selectedFile, audioOptions, onProgress);
          if (onTaskCreated) onTaskCreated(result);
          break;
        
        case 'video':
          result = await TranscriptionAPI.uploadVideo(selectedFile, onProgress);
          break;
        
        case 'frames':
          result = await TranscriptionAPI.extractFrames(selectedFile, frameOptions, onProgress);
          break;
      }

      setUploadResult(result);
      if (onUploadComplete) onUploadComplete(result);

    } catch (err: unknown) {
      console.error('Erro no upload:', err);
      const errorMessage = err instanceof Error 
        ? err.message 
        : (err as { response?: { data?: { detail?: string } }; message?: string })?.response?.data?.detail || 
          (err as { message?: string })?.message || 
          'Erro no upload';
      setError(errorMessage);
    } finally {
      setUploading(false);
    }
  };

  const getAcceptedFileTypes = () => {
    switch (uploadMode) {
      case 'audio':
        return '.wav,.mp3,.ogg,.m4a,.flac,.aac';
      case 'video':
      case 'frames':
        return '.mp4,.avi,.mov,.mkv,.webm,.wmv,.flv,.3gp,.m4v';
      default:
        return '';
    }
  };

  const getFileIcon = (file: File) => {
    if (file.type.startsWith('audio/')) return <FileAudio className="w-8 h-8 text-blue-500" />;
    if (file.type.startsWith('video/')) return <Video className="w-8 h-8 text-green-500" />;
    return <Upload className="w-8 h-8 text-gray-500" />;
  };

  return (
    <div className="max-w-4xl mx-auto p-6 bg-white rounded-lg shadow-lg">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Upload de Arquivos</h2>
        
        {/* Selector de modo */}
        <div className="flex space-x-4 mb-4">
          <button
            onClick={() => setUploadMode('audio')}
            className={`px-4 py-2 rounded-lg font-medium ${
              uploadMode === 'audio'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            <FileAudio className="w-4 h-4 inline mr-2" />
            Transcrever Áudio
          </button>
          <button
            onClick={() => setUploadMode('video')}
            className={`px-4 py-2 rounded-lg font-medium ${
              uploadMode === 'video'
                ? 'bg-green-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            <Video className="w-4 h-4 inline mr-2" />
            Transcrever Vídeo
          </button>
          <button
            onClick={() => setUploadMode('frames')}
            className={`px-4 py-2 rounded-lg font-medium ${
              uploadMode === 'frames'
                ? 'bg-purple-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            <Image className="w-4 h-4 inline mr-2" />
            Extrair Frames
          </button>
        </div>
      </div>

      {/* Área de upload */}
      <div
        className={`relative border-2 border-dashed rounded-lg p-8 text-center ${
          dragActive
            ? 'border-blue-400 bg-blue-50'
            : selectedFile
            ? 'border-green-400 bg-green-50'
            : 'border-gray-300 bg-gray-50'
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        {selectedFile ? (
          <div className="space-y-4">
            <div className="flex items-center justify-center space-x-3">
              {getFileIcon(selectedFile)}
              <div>
                <p className="font-medium text-gray-900">{selectedFile.name}</p>
                <p className="text-sm text-gray-500">{formatFileSize(selectedFile.size)}</p>
              </div>
              <button
                onClick={resetUpload}
                className="p-1 text-gray-400 hover:text-gray-600"
                disabled={uploading}
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {uploading && (
              <div className="space-y-2">
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${uploadProgress.percentage}%` }}
                  ></div>
                </div>
                <p className="text-sm text-gray-600">
                  {uploadProgress.percentage}% - {formatFileSize(uploadProgress.loaded)} / {formatFileSize(uploadProgress.total)}
                </p>
              </div>
            )}
          </div>
        ) : (
          <div className="space-y-4">
            <Upload className="w-12 h-12 text-gray-400 mx-auto" />
            <div>
              <p className="text-lg font-medium text-gray-900 mb-2">
                {uploadMode === 'audio' && 'Selecione um arquivo de áudio'}
                {uploadMode === 'video' && 'Selecione um arquivo de vídeo para transcrever'}
                {uploadMode === 'frames' && 'Selecione um arquivo de vídeo para extrair frames'}
              </p>
              <p className="text-gray-600">
                Arraste e solte aqui ou clique para selecionar
              </p>
            </div>
          </div>
        )}

        <input
          type="file"
          accept={getAcceptedFileTypes()}
          onChange={handleFileSelect}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          disabled={uploading}
        />
      </div>

      {/* Mensagem de auto-detecção */}
      {autoModeMessage && (
        <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
            <p className="text-sm text-blue-800">{autoModeMessage}</p>
          </div>
        </div>
      )}

      {/* Configurações específicas por modo */}
      {selectedFile && !uploading && uploadResult === null ? (
        <div className="mt-6 p-4 bg-gray-50 rounded-lg">
          <h3 className="font-medium text-gray-900 mb-4">Configurações</h3>
          
          {uploadMode === 'audio' && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={audioOptions.include_timestamps || false}
                  onChange={(e) => setAudioOptions({ ...audioOptions, include_timestamps: e.target.checked })}
                  className="rounded"
                />
                <span className="text-sm">Incluir timestamps</span>
              </label>
              
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={audioOptions.include_speaker_diarization || false}
                  onChange={(e) => setAudioOptions({ ...audioOptions, include_speaker_diarization: e.target.checked })}
                  className="rounded"
                />
                <span className="text-sm">Identificação de falantes</span>
              </label>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Modelo</label>
                <select
                  value={audioOptions.version_model || 'turbo'}
                  onChange={(e) => setAudioOptions({ ...audioOptions, version_model: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                >
                  <option value="turbo">Turbo (rápido)</option>
                  <option value="base">Base</option>
                  <option value="small">Small</option>
                  <option value="medium">Medium</option>
                  <option value="large">Large</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Formato</label>
                <select
                  value={audioOptions.output_format || 'txt'}
                  onChange={(e) => setAudioOptions({ ...audioOptions, output_format: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                >
                  <option value="txt">Texto (TXT)</option>
                  <option value="json">JSON</option>
                  <option value="srt">Legendas (SRT)</option>
                </select>
              </div>
            </div>
          )}

          {uploadMode === 'frames' && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">FPS</label>
                <input
                  type="number"
                  min="0.1"
                  max="30"
                  step="0.1"
                  value={frameOptions.fps}
                  onChange={(e) => setFrameOptions({ ...frameOptions, fps: parseFloat(e.target.value) })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Formato</label>
                <select
                  value={frameOptions.format}
                  onChange={(e) => setFrameOptions({ ...frameOptions, format: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                >
                  <option value="jpg">JPG</option>
                  <option value="png">PNG</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Qualidade</label>
                <input
                  type="number"
                  min="1"
                  max="31"
                  value={frameOptions.quality}
                  onChange={(e) => setFrameOptions({ ...frameOptions, quality: parseInt(e.target.value) })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                />
              </div>
            </div>
          )}
        </div>
      ) : null}

      {/* Botão de upload */}
      {selectedFile && uploadResult === null && (
        <div className="mt-6">
          <button
            onClick={handleUpload}
            disabled={uploading}
            className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            {uploading ? 'Processando...' : `Iniciar ${uploadMode === 'audio' ? 'Transcrição' : uploadMode === 'video' ? 'Extração e Transcrição' : 'Extração de Frames'}`}
          </button>
        </div>
      )}

      {/* Resultados */}
      {uploadResult && (
        <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg">
          <div className="flex items-center space-x-2 mb-3">
            <CheckCircle className="w-5 h-5 text-green-600" />
            <h3 className="font-medium text-green-900">Upload Concluído!</h3>
          </div>
          
          {uploadMode === 'audio' && uploadResult && 'task_id' in uploadResult && (
            <p className="text-sm text-green-800">
              Transcrição iniciada. Task ID: <code className="bg-green-100 px-2 py-1 rounded">{uploadResult.task_id}</code>
            </p>
          )}
          
          {uploadMode === 'video' && uploadResult && 'summary' in uploadResult && (
            <div className="text-sm text-green-800">
              <p>Áudio extraído e {(uploadResult as VideoExtractionResponse).summary?.total} transcrições iniciadas:</p>
              <ul className="list-disc list-inside mt-2">
                {(uploadResult as VideoExtractionResponse).summary?.types?.map((type: string) => (
                  <li key={type}>{type}</li>
                ))}
              </ul>
            </div>
          )}
          
          {uploadMode === 'frames' && uploadResult && 'extraction' in uploadResult && (
            <p className="text-sm text-green-800">
              {(uploadResult as FrameExtractionResponse).extraction?.frame_count} frames extraídos para: {(uploadResult as FrameExtractionResponse).extraction?.output_dir}
            </p>
          )}
        </div>
      )}

      {/* Erro */}
      {error && (
        <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-center space-x-2">
            <AlertCircle className="w-5 h-5 text-red-600" />
            <h3 className="font-medium text-red-900">Erro no Upload</h3>
          </div>
          <p className="text-sm text-red-800 mt-2">{error}</p>
        </div>
      )}
    </div>
  );
};

export default FileUploader;