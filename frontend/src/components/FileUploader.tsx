'use client';

import React, { useCallback, useState } from 'react';
import { Upload, FileAudio, Video, Image, X, CheckCircle, AlertCircle } from 'lucide-react';
import { TranscriptionAPI, formatFileSize } from '@/lib/api';
import { TranscriptionTask, TranscriptionRequest, UploadProgress, VideoExtractionResponse, FrameExtractionResponse, FileUploadProgress, BatchUploadResult } from '@/lib/types';

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
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [fileProgresses, setFileProgresses] = useState<FileUploadProgress[]>([]);
  const [batchResult, setBatchResult] = useState<BatchUploadResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [autoModeMessage, setAutoModeMessage] = useState<string | null>(null);
  const [isMultipleMode, setIsMultipleMode] = useState(false);

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
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const files = Array.from(e.dataTransfer.files);
      handleFilesSelected(files);
    }
  }, [uploadMode]);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const files = Array.from(e.target.files);
      handleFilesSelected(files);
    }
  };

  const handleFilesSelected = (files: File[]) => {
    if (files.length === 0) return;

    // Auto-detecta o modo baseado no primeiro arquivo
    const firstFile = files[0];
    const isVideoFile = firstFile.type.startsWith('video/') || 
                       ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.wmv', '.flv', '.3gp', '.m4v']
                         .some(ext => firstFile.name.toLowerCase().endsWith(ext));
    
    const isAudioFile = firstFile.type.startsWith('audio/') ||
                       ['.wav', '.mp3', '.ogg', '.m4a', '.flac', '.aac']
                         .some(ext => firstFile.name.toLowerCase().endsWith(ext));
    
    // Auto-seleciona o modo apropriado
    if (isVideoFile && uploadMode === 'audio') {
      setUploadMode('video');
      setAutoModeMessage(`${files.length} arquivo(s) de vídeo detectado(s)! Modo alterado automaticamente para "Transcrever Vídeo".`);
    } else if (isAudioFile && (uploadMode === 'video' || uploadMode === 'frames')) {
      setUploadMode('audio');
      setAutoModeMessage(`${files.length} arquivo(s) de áudio detectado(s)! Modo alterado automaticamente para "Transcrever Áudio".`);
    } else {
      setAutoModeMessage(files.length > 1 ? `${files.length} arquivos selecionados.` : null);
    }
    
    setSelectedFiles(files);
    setIsMultipleMode(files.length > 1);
    setError(null);
    setBatchResult(null);
    
    // Inicializa o progresso dos arquivos
    const initialProgress: FileUploadProgress[] = files.map(file => ({
      file,
      progress: { loaded: 0, total: 0, percentage: 0 },
      status: 'pending' as const
    }));
    setFileProgresses(initialProgress);
  };

  const resetUpload = () => {
    setSelectedFiles([]);
    setFileProgresses([]);
    setBatchResult(null);
    setError(null);
    setAutoModeMessage(null);
    setIsMultipleMode(false);
    setUploadProgress({ loaded: 0, total: 0, percentage: 0 });
  };

  const removeFile = (indexToRemove: number) => {
    const updatedFiles = selectedFiles.filter((_, index) => index !== indexToRemove);
    const updatedProgresses = fileProgresses.filter((_, index) => index !== indexToRemove);
    
    setSelectedFiles(updatedFiles);
    setFileProgresses(updatedProgresses);
    setIsMultipleMode(updatedFiles.length > 1);
    
    if (updatedFiles.length === 0) {
      resetUpload();
    }
  };

  const handleUpload = async () => {
    if (selectedFiles.length === 0) return;

    setUploading(true);
    setError(null);

    try {
      const results: BatchUploadResult = {
        files: [...fileProgresses],
        totalFiles: selectedFiles.length,
        completedFiles: 0,
        errorFiles: 0
      };

      // Callbacks para atualizar o progresso de cada arquivo
      const onFileProgress = (fileIndex: number, progress: UploadProgress) => {
        setFileProgresses(prev => prev.map((fp, index) => 
          index === fileIndex 
            ? { ...fp, progress, status: 'uploading' as const }
            : fp
        ));
      };

      const onFileComplete = (fileIndex: number, result: TranscriptionTask | VideoExtractionResponse | FrameExtractionResponse) => {
        setFileProgresses(prev => prev.map((fp, index) => 
          index === fileIndex 
            ? { ...fp, result, status: 'completed' as const }
            : fp
        ));
        
        results.completedFiles++;
        
        // Notifica sobre tarefas criadas para transcrições individuais
        if ('task_id' in result && 'status' in result && onTaskCreated) {
          onTaskCreated(result as TranscriptionTask);
        }
        // Para vídeos, notifica sobre múltiplas tarefas criadas
        else if ('transcriptions' in result && onTaskCreated) {
          (result as VideoExtractionResponse).transcriptions.forEach(task => onTaskCreated(task));
        }
      };

      const onFileError = (fileIndex: number, error: string) => {
        setFileProgresses(prev => prev.map((fp, index) => 
          index === fileIndex 
            ? { ...fp, error, status: 'error' as const }
            : fp
        ));
        
        results.errorFiles++;
      };

      // Valida tipos de arquivo
      for (const file of selectedFiles) {
        const isVideoFile = file.type.startsWith('video/') || 
                           ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.wmv', '.flv', '.3gp', '.m4v']
                             .some(ext => file.name.toLowerCase().endsWith(ext));

        if (uploadMode === 'audio' && isVideoFile) {
          setError(`Arquivo de vídeo detectado (${file.name})! Use o modo "Transcrever Vídeo" para arquivos de vídeo.`);
          return;
        }

        if ((uploadMode === 'video' || uploadMode === 'frames') && !isVideoFile) {
          setError(`Arquivo de áudio detectado (${file.name})! Use o modo "Transcrever Áudio" para arquivos de áudio.`);
          return;
        }
      }

      // Executa uploads baseado no modo
      switch (uploadMode) {
        case 'audio':
          await TranscriptionAPI.uploadMultipleAudios(
            selectedFiles,
            audioOptions,
            onFileProgress,
            onFileComplete,
            onFileError
          );
          break;
        
        case 'video':
          await TranscriptionAPI.uploadMultipleVideos(
            selectedFiles,
            onFileProgress,
            onFileComplete,
            onFileError
          );
          break;
        
        case 'frames':
          // Para frames, processa um por vez usando a API existente
          for (let i = 0; i < selectedFiles.length; i++) {
            try {
              const result = await TranscriptionAPI.extractFrames(
                selectedFiles[i],
                frameOptions,
                (progress) => onFileProgress(i, progress)
              );
              onFileComplete(i, result);
            } catch (error) {
              const errorMessage = error instanceof Error ? error.message : 'Erro no upload';
              onFileError(i, errorMessage);
            }
          }
          break;
      }

      setBatchResult(results);
      if (onUploadComplete) onUploadComplete(results);

    } catch (err: unknown) {
      console.error('Erro no upload em lote:', err);
      const errorMessage = err instanceof Error 
        ? err.message 
        : (err as { response?: { data?: { detail?: string } }; message?: string })?.response?.data?.detail || 
          (err as { message?: string })?.message || 
          'Erro no upload em lote';
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
            : selectedFiles.length > 0
            ? 'border-green-400 bg-green-50'
            : 'border-gray-300 bg-gray-50'
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        {selectedFiles.length > 0 ? (
          <div className="space-y-4">
            {/* Resumo dos arquivos */}
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <div className="flex -space-x-1">
                  {selectedFiles.slice(0, 3).map((file, index) => (
                    <div key={index} className="w-8 h-8 rounded-full bg-blue-100 border-2 border-white flex items-center justify-center">
                      {getFileIcon(file)}
                    </div>
                  ))}
                  {selectedFiles.length > 3 && (
                    <div className="w-8 h-8 rounded-full bg-gray-100 border-2 border-white flex items-center justify-center">
                      <span className="text-xs font-medium text-gray-600">+{selectedFiles.length - 3}</span>
                    </div>
                  )}
                </div>
                <div>
                  <p className="font-medium text-gray-900">
                    {selectedFiles.length} arquivo{selectedFiles.length > 1 ? 's' : ''} selecionado{selectedFiles.length > 1 ? 's' : ''}
                  </p>
                  <p className="text-sm text-gray-500">
                    Total: {formatFileSize(selectedFiles.reduce((total, file) => total + file.size, 0))}
                  </p>
                </div>
              </div>
              <button
                onClick={resetUpload}
                className="p-1 text-gray-400 hover:text-gray-600"
                disabled={uploading}
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Lista detalhada de arquivos */}
            <div className="max-h-40 overflow-y-auto space-y-2">
              {fileProgresses.map((fileProgress, index) => (
                <div key={index} className="flex items-center space-x-3 p-2 bg-gray-50 rounded-lg">
                  {getFileIcon(fileProgress.file)}
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-sm text-gray-900 truncate">{fileProgress.file.name}</p>
                    <p className="text-xs text-gray-500">{formatFileSize(fileProgress.file.size)}</p>
                  </div>
                  
                  {/* Status do arquivo */}
                  <div className="flex items-center space-x-2">
                    {fileProgress.status === 'uploading' && (
                      <div className="flex items-center space-x-2">
                        <div className="w-8 bg-gray-200 rounded-full h-1">
                          <div
                            className="bg-blue-600 h-1 rounded-full transition-all duration-300"
                            style={{ width: `${fileProgress.progress.percentage}%` }}
                          ></div>
                        </div>
                        <span className="text-xs text-gray-600">{fileProgress.progress.percentage}%</span>
                      </div>
                    )}
                    {fileProgress.status === 'completed' && (
                      <CheckCircle className="w-4 h-4 text-green-600" />
                    )}
                    {fileProgress.status === 'error' && (
                      <AlertCircle className="w-4 h-4 text-red-600" />
                    )}
                    {fileProgress.status === 'pending' && (
                      <div className="w-2 h-2 bg-gray-400 rounded-full"></div>
                    )}
                    
                    {!uploading && (
                      <button
                        onClick={() => removeFile(index)}
                        className="p-1 text-gray-400 hover:text-red-600"
                      >
                        <X className="w-3 h-3" />
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>

            {uploading && (
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Progresso geral:</span>
                  <span>{batchResult?.completedFiles || 0} de {selectedFiles.length} concluídos</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${((batchResult?.completedFiles || 0) / selectedFiles.length) * 100}%` }}
                  ></div>
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="space-y-4">
            <Upload className="w-12 h-12 text-gray-400 mx-auto" />
            <div>
              <p className="text-lg font-medium text-gray-900 mb-2">
                {uploadMode === 'audio' && 'Selecione arquivo(s) de áudio'}
                {uploadMode === 'video' && 'Selecione arquivo(s) de vídeo para transcrever'}
                {uploadMode === 'frames' && 'Selecione arquivo(s) de vídeo para extrair frames'}
              </p>
              <p className="text-gray-600">
                Arraste e solte aqui ou clique para selecionar múltiplos arquivos
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
          multiple
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
      {selectedFiles.length > 0 && !uploading && batchResult === null ? (
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
      {selectedFiles.length > 0 && batchResult === null && (
        <div className="mt-6">
          <button
            onClick={handleUpload}
            disabled={uploading}
            className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            {uploading ? `Processando ${selectedFiles.length} arquivo${selectedFiles.length > 1 ? 's' : ''}...` : `Iniciar ${uploadMode === 'audio' ? 'Transcrições' : uploadMode === 'video' ? 'Extrações e Transcrições' : 'Extrações de Frames'} (${selectedFiles.length} arquivo${selectedFiles.length > 1 ? 's' : ''})`}
          </button>
        </div>
      )}

      {/* Resultados */}
      {batchResult && (
        <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg">
          <div className="flex items-center space-x-2 mb-3">
            <CheckCircle className="w-5 h-5 text-green-600" />
            <h3 className="font-medium text-green-900">
              Upload em Lote Concluído! ({batchResult.completedFiles}/{batchResult.totalFiles} arquivos processados)
            </h3>
          </div>
          
          {batchResult.errorFiles > 0 && (
            <div className="mb-3 p-3 bg-yellow-50 border border-yellow-200 rounded">
              <p className="text-sm text-yellow-800">
                ⚠️ {batchResult.errorFiles} arquivo{batchResult.errorFiles > 1 ? 's' : ''} com erro{batchResult.errorFiles > 1 ? 's' : ''}
              </p>
            </div>
          )}
          
          <div className="space-y-2 max-h-32 overflow-y-auto">
            {fileProgresses.map((fileProgress, index) => (
              <div key={index} className="flex items-center justify-between p-2 bg-white rounded border">
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-4">
                    {fileProgress.status === 'completed' && <CheckCircle className="w-4 h-4 text-green-600" />}
                    {fileProgress.status === 'error' && <AlertCircle className="w-4 h-4 text-red-600" />}
                  </div>
                  <span className="text-sm font-medium truncate max-w-48">{fileProgress.file.name}</span>
                </div>
                
                <div className="text-xs text-gray-600">
                  {fileProgress.status === 'completed' && (
                    <span className="text-green-600">
                      {uploadMode === 'audio' && 'task_id' in fileProgress.result! && 'Transcrição iniciada'}
                      {uploadMode === 'video' && 'transcriptions' in fileProgress.result! && `${(fileProgress.result as VideoExtractionResponse).summary?.total} transcrições`}
                      {uploadMode === 'frames' && 'extraction' in fileProgress.result! && `${(fileProgress.result as FrameExtractionResponse).extraction?.frame_count} frames`}
                    </span>
                  )}
                  {fileProgress.status === 'error' && (
                    <span className="text-red-600 truncate max-w-32" title={fileProgress.error}>
                      {fileProgress.error}
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
          
          {uploadMode === 'video' && batchResult.completedFiles > 0 && (
            <div className="mt-3 text-sm text-green-800">
              <p>
                Total de transcrições iniciadas: {' '}
                {fileProgresses
                  .filter(fp => fp.status === 'completed' && fp.result && 'transcriptions' in fp.result)
                  .reduce((total, fp) => total + ((fp.result as VideoExtractionResponse).summary?.total || 0), 0)}
              </p>
            </div>
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