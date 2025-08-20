'use client';

import { useState } from 'react';
import FileUploader from '@/components/FileUploader';
import TranscriptionDashboard from '@/components/TranscriptionDashboard';
import { TranscriptionTask } from '@/lib/types';
import { Mic, Home, List } from 'lucide-react';

export default function HomePage() {
  const [activeTab, setActiveTab] = useState<'upload' | 'dashboard'>('upload');
  const [newTask, setNewTask] = useState<TranscriptionTask | undefined>(undefined);

  const handleTaskCreated = (task: TranscriptionTask) => {
    setNewTask(task);
    // Auto-switch para o dashboard quando uma nova tarefa é criada
    setActiveTab('dashboard');
  };

  const handleUploadComplete = (result: unknown) => {
    // Se for upload de vídeo, pode ter múltiplas tarefas
    if (result && typeof result === 'object' && 'transcriptions' in result) {
      const videoResult = result as { transcriptions?: unknown[] };
      if (videoResult.transcriptions && videoResult.transcriptions.length > 0) {
        setActiveTab('dashboard');
      }
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-6xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="bg-blue-600 p-2 rounded-lg">
                <Mic className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">Transcrição de Áudio</h1>
                <p className="text-sm text-gray-600">Converta áudio e vídeo em texto</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-1 bg-gray-100 rounded-lg p-1">
              <button
                onClick={() => setActiveTab('upload')}
                className={`flex items-center space-x-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  activeTab === 'upload'
                    ? 'bg-white text-blue-600 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                <Home className="w-4 h-4" />
                <span>Upload</span>
              </button>
              <button
                onClick={() => setActiveTab('dashboard')}
                className={`flex items-center space-x-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  activeTab === 'dashboard'
                    ? 'bg-white text-blue-600 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                <List className="w-4 h-4" />
                <span>Transcrições</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="py-8">
        {activeTab === 'upload' && (
          <FileUploader 
            onTaskCreated={handleTaskCreated}
            onUploadComplete={handleUploadComplete}
          />
        )}
        
        {activeTab === 'dashboard' && (
          <TranscriptionDashboard newTask={newTask} />
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t mt-16">
        <div className="max-w-6xl mx-auto px-6 py-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div>
              <h3 className="text-sm font-semibold text-gray-900 mb-4">Funcionalidades</h3>
              <ul className="space-y-2 text-sm text-gray-600">
                <li>• Transcrição de áudio com WhisperX</li>
                <li>• Identificação de falantes</li>
                <li>• Extração de áudio de vídeos</li>
                <li>• Múltiplos formatos de saída</li>
              </ul>
            </div>
            
            <div>
              <h3 className="text-sm font-semibold text-gray-900 mb-4">Formatos Suportados</h3>
              <ul className="space-y-2 text-sm text-gray-600">
                <li><strong>Áudio:</strong> WAV, MP3, OGG, M4A, FLAC, AAC</li>
                <li><strong>Vídeo:</strong> MP4, AVI, MOV, MKV, WEBM</li>
                <li><strong>Saída:</strong> TXT, JSON, SRT</li>
              </ul>
            </div>
            
            <div>
              <h3 className="text-sm font-semibold text-gray-900 mb-4">Modelos WhisperX</h3>
              <ul className="space-y-2 text-sm text-gray-600">
                <li><strong>Turbo:</strong> Mais rápido, boa qualidade</li>
                <li><strong>Base/Small:</strong> Equilibrio velocidade/precisão</li>
                <li><strong>Medium/Large:</strong> Máxima precisão</li>
              </ul>
            </div>
          </div>
          
          <div className="mt-8 pt-8 border-t border-gray-200 text-center">
            <p className="text-sm text-gray-600">
              Sistema de Transcrição de Áudio - Powered by WhisperX & PyAnnote
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
