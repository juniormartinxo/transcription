'use client';

import React, { useEffect, useState, useCallback } from 'react';
import { 
  Clock, 
  CheckCircle, 
  XCircle, 
  Loader2, 
  Download, 
  Calendar, 
  FileText, 
  RefreshCw,
  Search,
  Filter,
  StopCircle,
  Trash2,
  AlertTriangle
} from 'lucide-react';
import { TranscriptionAPI, formatDuration } from '@/lib/api';
import { TranscriptionTask, TranscriptionStatus } from '@/lib/types';

interface TranscriptionDashboardProps {
  newTask?: TranscriptionTask;
}

const TranscriptionDashboard: React.FC<TranscriptionDashboardProps> = ({ newTask }) => {
  const [tasks, setTasks] = useState<TranscriptionTask[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<TranscriptionStatus | 'all'>('all');
  const [sortBy, setSortBy] = useState<'created_at' | 'status' | 'filename'>('created_at');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  
  // Estados para modal de confirmação
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [taskToDelete, setTaskToDelete] = useState<TranscriptionTask | null>(null);
  const [deleteWithFiles, setDeleteWithFiles] = useState(true);

  // Polling para atualizar status das tarefas
  const [pollingTasks, setPollingTasks] = useState<Set<string>>(new Set());
  
  // Sistema de polling em lote mais eficiente
  useEffect(() => {
    if (pollingTasks.size === 0) return;

    const interval = setInterval(async () => {
      if (pollingTasks.size === 0) return;

      try {
        // Carrega todas as tarefas de uma vez
        const response = await TranscriptionAPI.listTasks();
        const currentTasks = response.tasks;
        
        // Atualiza apenas as tarefas que estão em polling
        setTasks(prev => {
          let hasChanges = false;
          const newTasks = prev.map(prevTask => {
            if (!pollingTasks.has(prevTask.task_id)) return prevTask;
            
            const updatedTask = currentTasks.find(t => t.task_id === prevTask.task_id);
            if (updatedTask && (
              updatedTask.status !== prevTask.status || 
              updatedTask.completed_at !== prevTask.completed_at
            )) {
              hasChanges = true;
              return updatedTask;
            }
            return prevTask;
          });
          
          return hasChanges ? newTasks : prev;
        });
        
        // Remove tarefas completadas do polling
        setPollingTasks(prev => {
          const newSet = new Set(prev);
          let hasChanges = false;
          
          for (const taskId of prev) {
            const task = currentTasks.find(t => t.task_id === taskId);
            if (task && (task.status === 'completed' || task.status === 'failed')) {
              newSet.delete(taskId);
              hasChanges = true;
            }
          }
          
          return hasChanges ? newSet : prev;
        });
        
      } catch (error) {
        console.error('Erro no polling em lote:', error);
      }
    }, pollingTasks.size > 5 ? 10000 : 5000); // Polling mais lento quando há muitas tarefas ativas

    return () => clearInterval(interval);
  }, [pollingTasks]);

  const loadTasks = async () => {
    try {
      setError(null);
      const response = await TranscriptionAPI.listTasks();
      setTasks(response.tasks);
    } catch (err: unknown) {
      console.error('Erro ao carregar tarefas:', err);
      const errorMessage = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Erro ao carregar tarefas';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  // Adiciona nova tarefa quando recebida via props
  useEffect(() => {
    if (newTask) {
      setTasks(prev => {
        const exists = prev.find(t => t.task_id === newTask.task_id);
        if (exists) return prev;
        return [newTask, ...prev];
      });
      
      // Inicia polling para a nova tarefa se ela estiver pendente ou processando
      if (newTask.status === 'pending' || newTask.status === 'processing') {
        startPollingTask(newTask.task_id);
      }
    }
  }, []);

  useEffect(() => {
    loadTasks();
  }, []);

  const startPollingTask = useCallback((taskId: string) => {
    if (pollingTasks.has(taskId)) return;

    // Simplesmente adiciona a tarefa ao conjunto de polling
    // O sistema de polling em lote vai gerenciar as atualizações
    setPollingTasks(prev => new Set(prev).add(taskId));
  }, [pollingTasks]);

  const handleDownload = async (task: TranscriptionTask) => {
    try {
      const blob = await TranscriptionAPI.downloadTranscription(task.task_id);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${task.filename}_transcricao.txt`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Erro no download:', error);
    }
  };

  const handleCancelTask = async (task: TranscriptionTask) => {
    try {
      await TranscriptionAPI.cancelTask(task.task_id);
      
      // Atualiza o estado local
      setTasks(prevTasks => 
        prevTasks.map(t => 
          t.task_id === task.task_id 
            ? { ...t, status: 'failed' as TranscriptionStatus, error: 'Tarefa cancelada pelo usuário' }
            : t
        )
      );
      
      // Remove do polling
      setPollingTasks(prev => {
        const newSet = new Set(prev);
        newSet.delete(task.task_id);
        return newSet;
      });
      
    } catch (error) {
      console.error('Erro ao cancelar tarefa:', error);
      setError('Erro ao cancelar tarefa');
    }
  };

  const handleDeleteTask = async () => {
    if (!taskToDelete) return;
    
    try {
      await TranscriptionAPI.deleteTask(taskToDelete.task_id, deleteWithFiles);
      
      // Remove a tarefa da lista
      setTasks(prevTasks => 
        prevTasks.filter(t => t.task_id !== taskToDelete.task_id)
      );
      
      // Remove do polling se estiver ativo
      setPollingTasks(prev => {
        const newSet = new Set(prev);
        newSet.delete(taskToDelete.task_id);
        return newSet;
      });
      
      setShowDeleteModal(false);
      setTaskToDelete(null);
      
    } catch (error) {
      console.error('Erro ao excluir tarefa:', error);
      setError('Erro ao excluir tarefa');
    }
  };

  const openDeleteModal = (task: TranscriptionTask) => {
    setTaskToDelete(task);
    setShowDeleteModal(true);
  };

  const closeDeleteModal = () => {
    setShowDeleteModal(false);
    setTaskToDelete(null);
    setDeleteWithFiles(true);
  };

  const getStatusIcon = (status: TranscriptionStatus) => {
    switch (status) {
      case 'pending':
        return <Clock className="w-4 h-4 text-yellow-500" />;
      case 'processing':
        return <Loader2 className="w-4 h-4 text-blue-500 animate-spin" />;
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'failed':
        return <XCircle className="w-4 h-4 text-red-500" />;
    }
  };

  const getStatusText = (status: TranscriptionStatus) => {
    const statusMap = {
      pending: 'Pendente',
      processing: 'Processando',
      completed: 'Concluída',
      failed: 'Falhou'
    };
    return statusMap[status];
  };

  const getStatusColor = (status: TranscriptionStatus) => {
    switch (status) {
      case 'pending':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'processing':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'completed':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'failed':
        return 'bg-red-100 text-red-800 border-red-200';
    }
  };

  // Identifica se uma tarefa é parte de um lote
  const isBatchTask = (taskId: string) => {
    return taskId.includes('batch_');
  };

  // Extrai o ID do lote
  const getBatchId = (taskId: string) => {
    const match = taskId.match(/^(batch_[^_]+_\d{8}_\d{6}_[a-f0-9]{8})/);
    return match ? match[1] : null;
  };


  // Filtros e ordenação
  const filteredAndSortedTasks = tasks
    .filter(task => {
      const matchesSearch = task.filename.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           task.task_id.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesStatus = statusFilter === 'all' || task.status === statusFilter;
      return matchesSearch && matchesStatus;
    })
    .sort((a, b) => {
      let aValue, bValue;
      
      switch (sortBy) {
        case 'created_at':
          aValue = new Date(a.created_at).getTime();
          bValue = new Date(b.created_at).getTime();
          break;
        case 'status':
          aValue = a.status;
          bValue = b.status;
          break;
        case 'filename':
          aValue = a.filename.toLowerCase();
          bValue = b.filename.toLowerCase();
          break;
      }
      
      if (sortOrder === 'asc') {
        return aValue < bValue ? -1 : aValue > bValue ? 1 : 0;
      } else {
        return aValue > bValue ? -1 : aValue < bValue ? 1 : 0;
      }
    });

  const handleSort = (field: typeof sortBy) => {
    if (sortBy === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(field);
      setSortOrder('desc');
    }
  };

  if (loading) {
    return (
      <div className="max-w-6xl mx-auto p-6">
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
          <span className="ml-3 text-lg">Carregando transcrições...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-lg">
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-2xl font-bold text-gray-900">Dashboard de Transcrições</h2>
            <button
              onClick={loadTasks}
              className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              <RefreshCw className="w-4 h-4" />
              <span>Atualizar</span>
            </button>
          </div>

          {/* Filtros e busca */}
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Buscar por nome do arquivo ou ID da tarefa..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div className="flex items-center space-x-2">
              <Filter className="w-4 h-4 text-gray-500" />
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value as TranscriptionStatus | 'all')}
                className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">Todos os status</option>
                <option value="pending">Pendente</option>
                <option value="processing">Processando</option>
                <option value="completed">Concluída</option>
                <option value="failed">Falhou</option>
              </select>
            </div>
          </div>
        </div>

        {error && (
          <div className="p-4 bg-red-50 border-l-4 border-red-400">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        {/* Lista de tarefas */}
        <div className="divide-y divide-gray-200">
          {filteredAndSortedTasks.length === 0 ? (
            <div className="p-12 text-center">
              <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                {tasks.length === 0 ? 'Nenhuma transcrição encontrada' : 'Nenhuma transcrição corresponde aos filtros'}
              </h3>
              <p className="text-gray-600">
                {tasks.length === 0 
                  ? 'Faça upload de um arquivo para começar.' 
                  : 'Tente ajustar os filtros de busca.'}
              </p>
            </div>
          ) : (
            <>
              {/* Cabeçalho da tabela */}
              <div className="bg-gray-50 px-6 py-3">
                <div className="grid grid-cols-1 md:grid-cols-12 gap-4 items-center text-sm font-medium text-gray-700">
                  <div 
                    className="md:col-span-3 cursor-pointer hover:text-gray-900 flex items-center space-x-1"
                    onClick={() => handleSort('filename')}
                  >
                    <span>Arquivo</span>
                    {sortBy === 'filename' && (
                      <span className="text-blue-600">{sortOrder === 'asc' ? '↑' : '↓'}</span>
                    )}
                  </div>
                  <div 
                    className="md:col-span-2 cursor-pointer hover:text-gray-900 flex items-center space-x-1"
                    onClick={() => handleSort('status')}
                  >
                    <span>Status</span>
                    {sortBy === 'status' && (
                      <span className="text-blue-600">{sortOrder === 'asc' ? '↑' : '↓'}</span>
                    )}
                  </div>
                  <div 
                    className="md:col-span-2 cursor-pointer hover:text-gray-900 flex items-center space-x-1"
                    onClick={() => handleSort('created_at')}
                  >
                    <span>Criado</span>
                    {sortBy === 'created_at' && (
                      <span className="text-blue-600">{sortOrder === 'asc' ? '↑' : '↓'}</span>
                    )}
                  </div>
                  <div className="md:col-span-2">Duração</div>
                  <div className="md:col-span-1">Tipo</div>
                  <div className="md:col-span-2">Ações</div>
                </div>
              </div>

              {/* Lista de tarefas */}
              {filteredAndSortedTasks.map((task) => {
                const isTaskInBatch = isBatchTask(task.task_id);
                const batchId = getBatchId(task.task_id);
                
                return (
                  <div key={task.task_id} className={`px-6 py-4 hover:bg-gray-50 ${isTaskInBatch ? 'border-l-4 border-blue-300 bg-blue-50' : ''}`}>
                    <div className="grid grid-cols-1 md:grid-cols-12 gap-4 items-center">
                      <div className="md:col-span-3">
                        <div className="flex flex-col">
                          {isTaskInBatch && (
                            <span className="text-xs text-blue-600 font-mono mb-1">
                              Lote: {batchId}
                            </span>
                          )}
                          <span className="font-medium text-gray-900 truncate" title={task.filename}>
                            {task.filename}
                          </span>
                          <span className="text-xs text-gray-500 font-mono">
                            {task.task_id}
                          </span>
                        </div>
                      </div>

                      <div className="md:col-span-2">
                        <span className={`inline-flex items-center space-x-2 px-3 py-1 rounded-full text-xs font-medium border ${getStatusColor(task.status)}`}>
                          {getStatusIcon(task.status)}
                          <span>{getStatusText(task.status)}</span>
                        </span>
                      </div>

                      <div className="md:col-span-2 text-sm text-gray-600">
                        <div className="flex items-center space-x-1">
                          <Calendar className="w-4 h-4" />
                          <span>{new Date(task.created_at).toLocaleDateString('pt-BR')}</span>
                        </div>
                        <div className="text-xs text-gray-500">
                          {new Date(task.created_at).toLocaleTimeString('pt-BR')}
                        </div>
                      </div>

                      <div className="md:col-span-2 text-sm text-gray-600">
                        {task.completed_at ? (
                          <div className="flex items-center space-x-1">
                            <Clock className="w-4 h-4" />
                            <span>{formatDuration(task.created_at, task.completed_at)}</span>
                          </div>
                        ) : task.status === 'processing' ? (
                          <div className="flex items-center space-x-1">
                            <Clock className="w-4 h-4" />
                            <span>{formatDuration(task.created_at)}</span>
                          </div>
                        ) : (
                          <span className="text-gray-400">-</span>
                        )}
                      </div>

                      <div className="md:col-span-1">
                        <span className="inline-block px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded">
                          {(task as TranscriptionTask & { type?: string }).type || (isTaskInBatch ? 'lote' : 'padrão')}
                        </span>
                      </div>

                      <div className="md:col-span-2 flex items-center space-x-2">
                        {task.status === 'completed' && (
                          <button
                            onClick={() => handleDownload(task)}
                            className="flex items-center space-x-1 px-3 py-1 bg-green-600 text-white text-sm rounded hover:bg-green-700"
                            title="Download da transcrição"
                          >
                            <Download className="w-3 h-3" />
                            <span className="hidden sm:inline">Download</span>
                          </button>
                        )}

                        {(task.status === 'pending' || task.status === 'processing') && (
                          <>
                            <button
                              onClick={() => handleCancelTask(task)}
                              className="flex items-center space-x-1 px-3 py-1 bg-orange-600 text-white text-sm rounded hover:bg-orange-700"
                              title="Cancelar transcrição"
                            >
                              <StopCircle className="w-3 h-3" />
                              <span className="hidden sm:inline">Cancelar</span>
                            </button>
                            <div className="text-xs text-gray-500 flex items-center space-x-1">
                              <Loader2 className="w-3 h-3 animate-spin" />
                              <span className="hidden sm:inline">Processando...</span>
                            </div>
                          </>
                        )}

                        {task.status === 'failed' && task.error && (
                          <div 
                            className="px-3 py-1 bg-red-100 text-red-800 text-xs rounded cursor-help"
                            title={task.error}
                          >
                            Ver erro
                          </div>
                        )}

                        <button
                          onClick={() => openDeleteModal(task)}
                          className="flex items-center space-x-1 px-3 py-1 bg-red-600 text-white text-sm rounded hover:bg-red-700"
                          title="Excluir tarefa"
                        >
                          <Trash2 className="w-3 h-3" />
                          <span className="hidden sm:inline">Excluir</span>
                        </button>
                      </div>
                    </div>

                    {task.status === 'failed' && task.error && (
                      <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded">
                        <p className="text-sm text-red-800">
                          <strong>Erro:</strong> {task.error}
                        </p>
                      </div>
                    )}
                  </div>
                );
              })}
            </>
          )}
        </div>

        {/* Estatísticas */}
        {tasks.length > 0 && (
          <div className="px-6 py-4 bg-gray-50 border-t border-gray-200">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
              <div>
                <div className="text-2xl font-bold text-gray-900">
                  {tasks.filter(t => t.status === 'completed').length}
                </div>
                <div className="text-sm text-gray-600">Concluídas</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-blue-600">
                  {tasks.filter(t => t.status === 'processing').length}
                </div>
                <div className="text-sm text-gray-600">Processando</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-yellow-600">
                  {tasks.filter(t => t.status === 'pending').length}
                </div>
                <div className="text-sm text-gray-600">Pendentes</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-red-600">
                  {tasks.filter(t => t.status === 'failed').length}
                </div>
                <div className="text-sm text-gray-600">Falharam</div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Modal de Confirmação de Exclusão */}
      {showDeleteModal && taskToDelete && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-mx mx-4">
            <div className="flex items-center space-x-3 mb-4">
              <AlertTriangle className="w-6 h-6 text-red-600" />
              <h3 className="text-lg font-semibold text-gray-900">Confirmar Exclusão</h3>
            </div>
            
            <p className="text-gray-600 mb-4">
              Tem certeza que deseja excluir a tarefa <strong>{taskToDelete.filename}</strong>?
            </p>
            
            <div className="mb-4">
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={deleteWithFiles}
                  onChange={(e) => setDeleteWithFiles(e.target.checked)}
                  className="rounded"
                />
                <span className="text-sm text-gray-700">
                  Excluir também os arquivos de áudio e transcrição
                </span>
              </label>
            </div>
            
            <div className="flex space-x-3 justify-end">
              <button
                onClick={closeDeleteModal}
                className="px-4 py-2 bg-gray-300 text-gray-700 rounded hover:bg-gray-400"
              >
                Cancelar
              </button>
              <button
                onClick={handleDeleteTask}
                className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
              >
                Excluir
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TranscriptionDashboard;