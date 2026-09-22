import React, { useState, useEffect, useRef } from 'react'
import axios, { AxiosError } from 'axios'
import {
  UploadCloud,
  FileText,
  Trash2,
  AlertCircle,
  CheckCircle2,
  Loader2,
  Clock,
  Layers,
  BookOpen,
  MessageSquare,
  Github,
} from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import clsx from 'clsx'
import { IngestModal } from '../components/IngestModal'

interface Document {
  id: string
  filename: string
  title: string | null
  mime_type: string
  size_bytes: number
  status: string
  chunk_count: number
  page_count: number | null
  created_at: string
}

export function Documents() {
  const [documents, setDocuments] = useState<Document[]>([])
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [dragActive, setDragActive] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  const [isIngestModalOpen, setIsIngestModalOpen] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const navigate = useNavigate()

  const fetchDocuments = async () => {
    try {
      const response = await axios.get('/api/documents')
      setDocuments(response.data.items || [])
    } catch {
      setError('Failed to load documents')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchDocuments()
  }, [])

  const handleFile = async (file: File) => {
    if (!file) return

    setUploading(true)
    setError(null)
    setSuccess(null)

    const formData = new FormData()
    formData.append('file', file)

    try {
      await axios.post('/api/documents/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      setSuccess(`"${file.name}" uploaded and indexed successfully!`)
      fetchDocuments()
    } catch (err) {
      const axiosErr = err as AxiosError<{ detail?: string }>
      setError(axiosErr.response?.data?.detail || 'Failed to upload document')
    } finally {
      setUploading(false)
    }
  }

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0])
    }
  }

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this document and its embeddings?')) return
    try {
      await axios.delete(`/api/documents/${id}`)
      setDocuments(documents.filter((d) => d.id !== id))
    } catch {
      setError('Failed to delete document')
    }
  }

  const formatSize = (bytes: number) => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`
  }

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString(undefined, {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  const getFileBadge = (filename: string) => {
    const ext = filename.split('.').pop()?.toLowerCase()
    switch (ext) {
      case 'pdf':
        return { label: 'PDF', bg: 'bg-red-50 text-red-700 border-red-200' }
      case 'docx':
        return { label: 'DOCX', bg: 'bg-blue-50 text-blue-700 border-blue-200' }
      case 'md':
        return { label: 'MD', bg: 'bg-purple-50 text-purple-700 border-purple-200' }
      case 'py':
      case 'ts':
      case 'js':
        return { label: ext.toUpperCase(), bg: 'bg-indigo-50 text-indigo-700 border-indigo-200' }
      default:
        return { label: ext?.toUpperCase() || 'TXT', bg: 'bg-slate-50 text-slate-700 border-slate-200' }
    }
  }

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">Knowledge & Codebase Assets</h1>
          <p className="text-xs text-[var(--color-text-muted)] mt-1">
            Manage your document collections, GitHub repositories, and codebase vector indices.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setIsIngestModalOpen(true)}
            className="btn bg-slate-900 hover:bg-slate-800 text-white text-xs py-2 px-3.5 rounded-xl flex items-center gap-2 shadow-xs cursor-pointer"
          >
            <Github size={15} />
            <span>Ingest Repo / Folder</span>
          </button>
        </div>
      </div>

      {/* Upload Zone */}
      <div className="card p-6 bg-white shadow-card border border-[var(--color-border)]">
        <div
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          className={clsx(
            'border-2 border-dashed rounded-xl p-8 text-center transition-all duration-200',
            dragActive
              ? 'border-[var(--color-primary)] bg-indigo-50/40'
              : 'border-slate-200 hover:border-indigo-300 bg-slate-50/40'
          )}
        >
          <input
            ref={fileInputRef}
            type="file"
            id="file-upload"
            className="hidden"
            accept=".pdf,.docx,.txt,.md"
            onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
            disabled={uploading}
          />

          {uploading ? (
            <div className="flex flex-col items-center justify-center py-4">
              <Loader2 size={36} className="text-[var(--color-primary)] animate-spin mb-3" />
              <p className="text-sm font-semibold text-slate-800">Processing & Indexing File...</p>
              <p className="text-xs text-[var(--color-text-muted)] mt-1">Extracting text, chunking, and computing vector embeddings</p>
            </div>
          ) : (
            <>
              <div className="w-12 h-12 rounded-2xl bg-indigo-50 border border-indigo-100 flex items-center justify-center mx-auto mb-3 text-[var(--color-primary)]">
                <UploadCloud size={24} />
              </div>
              <h3 className="text-sm font-semibold text-slate-800 mb-1">
                Drag and drop your document here, or{' '}
                <label
                  htmlFor="file-upload"
                  className="text-[var(--color-primary)] hover:underline cursor-pointer font-medium"
                >
                  browse files
                </label>
              </h3>
              <p className="text-xs text-[var(--color-text-muted)] max-w-sm mx-auto mb-4">
                Supported formats: PDF, DOCX, TXT, and Markdown (up to 50MB)
              </p>
              <div className="flex items-center justify-center gap-2">
                <span className="badge badge-neutral text-[10px]">PDF</span>
                <span className="badge badge-neutral text-[10px]">DOCX</span>
                <span className="badge badge-neutral text-[10px]">TXT</span>
                <span className="badge badge-neutral text-[10px]">Markdown</span>
              </div>
            </>
          )}

          {error && (
            <div className="mt-4 flex items-start gap-2.5 p-3.5 bg-red-50 border border-red-200 text-red-700 rounded-lg text-xs text-left">
              <AlertCircle size={16} className="shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}
          {success && (
            <div className="mt-4 flex items-start gap-2.5 p-3.5 bg-emerald-50 border border-emerald-200 text-emerald-700 rounded-lg text-xs text-left">
              <CheckCircle2 size={16} className="shrink-0 mt-0.5" />
              <span>{success}</span>
            </div>
          )}
        </div>
      </div>

      {/* Documents Table or Empty State */}
      {loading ? (
        <div className="card p-12 text-center">
          <Loader2 size={32} className="mx-auto animate-spin text-[var(--color-primary)]" />
          <p className="mt-3 text-sm text-[var(--color-text-muted)]">Loading document index...</p>
        </div>
      ) : documents.length === 0 ? (
        <div className="card p-12 text-center">
          <div className="w-14 h-14 rounded-2xl bg-slate-100 flex items-center justify-center mx-auto mb-3 text-slate-400">
            <FileText size={28} />
          </div>
          <h3 className="text-base font-semibold text-slate-900 mb-1">No documents indexed yet</h3>
          <p className="text-xs text-[var(--color-text-muted)] max-w-sm mx-auto mb-4">
            Upload your technical documentation or import a GitHub repo to enable grounded AI Q&A.
          </p>
          <div className="flex items-center justify-center gap-3">
            <label htmlFor="file-upload" className="btn btn-primary text-xs cursor-pointer">
              <UploadCloud size={15} />
              <span>Upload Document</span>
            </label>
            <button
              onClick={() => setIsIngestModalOpen(true)}
              className="btn btn-secondary text-xs cursor-pointer"
            >
              <Github size={15} />
              <span>Ingest GitHub / Folder</span>
            </button>
          </div>
        </div>
      ) : (
        <div className="card overflow-hidden shadow-card border border-[var(--color-border)]">
          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead>
                <tr className="border-b border-[var(--color-border)] bg-slate-50/80 text-xs font-semibold text-slate-600">
                  <th className="px-5 py-3.5">Document</th>
                  <th className="px-4 py-3.5">Format</th>
                  <th className="px-4 py-3.5">Pages</th>
                  <th className="px-4 py-3.5">Chunks</th>
                  <th className="px-4 py-3.5">Size</th>
                  <th className="px-4 py-3.5">Status</th>
                  <th className="px-4 py-3.5">Indexed At</th>
                  <th className="px-5 py-3.5 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[var(--color-border)] text-xs">
                {documents.map((doc) => {
                  const badge = getFileBadge(doc.filename)
                  return (
                    <tr key={doc.id} className="hover:bg-slate-50/60 transition-colors">
                      <td className="px-5 py-3.5">
                        <div className="flex items-center gap-3">
                          <div className="w-8 h-8 rounded-lg bg-slate-100 border border-slate-200 flex items-center justify-center shrink-0 text-slate-600">
                            <FileText size={16} />
                          </div>
                          <div className="min-w-0">
                            <p className="font-semibold text-slate-900 truncate max-w-xs">{doc.filename}</p>
                            {doc.title && (
                              <p className="text-[11px] text-[var(--color-text-muted)] truncate max-w-xs">{doc.title}</p>
                            )}
                          </div>
                        </div>
                      </td>
                      <td className="px-4 py-3.5">
                        <span className={clsx('badge text-[10px] font-mono border', badge.bg)}>
                          {badge.label}
                        </span>
                      </td>
                      <td className="px-4 py-3.5 text-slate-700 font-medium">
                        <div className="flex items-center gap-1">
                          <BookOpen size={13} className="text-slate-400" />
                          <span>{doc.page_count || 1}</span>
                        </div>
                      </td>
                      <td className="px-4 py-3.5 text-slate-700 font-medium">
                        <div className="flex items-center gap-1">
                          <Layers size={13} className="text-slate-400" />
                          <span>{doc.chunk_count || 0}</span>
                        </div>
                      </td>
                      <td className="px-4 py-3.5 text-[var(--color-text-muted)] font-mono text-[11px]">
                        {formatSize(doc.size_bytes)}
                      </td>
                      <td className="px-4 py-3.5">
                        {doc.status === 'ready' && (
                          <span className="badge badge-success text-[10px]">
                            <span className="status-dot bg-emerald-500 mr-0.5" /> Ready
                          </span>
                        )}
                        {doc.status === 'processing' && (
                          <span className="badge badge-info text-[10px]">
                            <Loader2 size={11} className="animate-spin mr-0.5" /> Processing
                          </span>
                        )}
                        {doc.status === 'pending' && (
                          <span className="badge badge-warning text-[10px]">
                            <span className="status-dot bg-amber-500 mr-0.5" /> Pending
                          </span>
                        )}
                        {doc.status === 'failed' && (
                          <span className="badge badge-error text-[10px]">
                            <span className="status-dot bg-red-500 mr-0.5" /> Failed
                          </span>
                        )}
                        {!['ready', 'processing', 'pending', 'failed'].includes(doc.status) && (
                          <span className="badge badge-neutral text-[10px]">
                            {doc.status}
                          </span>
                        )}
                      </td>
                      <td className="px-4 py-3.5 text-[var(--color-text-muted)]">
                        <div className="flex items-center gap-1 text-[11px]">
                          <Clock size={12} className="text-slate-400" />
                          <span>{formatDate(doc.created_at)}</span>
                        </div>
                      </td>
                      <td className="px-5 py-3.5 text-right">
                        <div className="flex items-center justify-end gap-1">
                          <button
                            onClick={() => navigate(`/chat?doc=${doc.id}`)}
                            className="p-1.5 text-slate-500 hover:text-indigo-600 hover:bg-indigo-50 rounded-md transition-colors"
                            title="Chat with this document"
                            aria-label="Chat with document"
                          >
                            <MessageSquare size={16} />
                          </button>
                          <button
                            onClick={() => handleDelete(doc.id)}
                            className="p-1.5 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-md transition-colors"
                            title="Delete document"
                            aria-label="Delete document"
                          >
                            <Trash2 size={16} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Ingestion Modal */}
      <IngestModal
        isOpen={isIngestModalOpen}
        onClose={() => setIsIngestModalOpen(false)}
        onSuccess={() => {
          fetchDocuments()
        }}
      />
    </div>
  )
}
