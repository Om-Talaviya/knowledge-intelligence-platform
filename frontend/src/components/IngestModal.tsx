import React, { useState } from 'react'
import axios, { AxiosError } from 'axios'
import { Github, Folder, Loader2, CheckCircle2, AlertCircle, X } from 'lucide-react'

interface IngestModalProps {
  isOpen: boolean
  onClose: () => void
  onSuccess: () => void
}

interface IngestResult {
  job_id: string
  total_files?: number
  processed_files?: number
  total_chunks?: number
  status: string
}

export function IngestModal({ isOpen, onClose, onSuccess }: IngestModalProps) {
  const [activeTab, setActiveTab] = useState<'github' | 'local'>('github')
  const [githubUrl, setGithubUrl] = useState('')
  const [branch, setBranch] = useState('main')
  const [token, setToken] = useState('')
  const [folderPath, setFolderPath] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<IngestResult | null>(null)

  if (!isOpen) return null

  const handleGithubSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!githubUrl.trim()) return
    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const resp = await axios.post<IngestResult>('/api/github/ingest', {
        repo_url: githubUrl.trim(),
        branch: branch.trim() || 'main',
        auth_token: token.trim() || undefined,
      })
      setResult(resp.data)
      onSuccess()
    } catch (err) {
      const axiosErr = err as AxiosError<{ detail?: string }>
      setError(axiosErr.response?.data?.detail || axiosErr.message || 'Failed to ingest repository')
    } finally {
      setLoading(false)
    }
  }

  const handleLocalSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!folderPath.trim()) return
    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const resp = await axios.post<IngestResult>('/api/ingest/local', {
        folder_path: folderPath.trim(),
      })
      setResult(resp.data)
      onSuccess()
    } catch (err) {
      const axiosErr = err as AxiosError<{ detail?: string }>
      setError(axiosErr.response?.data?.detail || axiosErr.message || 'Failed to ingest local folder')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-xs p-4">
      <div className="bg-white rounded-2xl shadow-2xl border border-slate-200 max-w-lg w-full overflow-hidden animate-in fade-in zoom-in-95 duration-150">
        <div className="flex items-center justify-between p-5 border-b border-slate-100">
          <div>
            <h3 className="text-base font-semibold text-slate-900">Ingest Repository or Codebase</h3>
            <p className="text-xs text-slate-500 mt-0.5">Index GitHub repositories or local folders for deep research</p>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600 p-1.5 rounded-lg hover:bg-slate-100">
            <X size={18} />
          </button>
        </div>

        {/* Tab Selector */}
        <div className="flex border-b border-slate-100 bg-slate-50/70 p-1 gap-1">
          <button
            type="button"
            onClick={() => { setActiveTab('github'); setError(null); setResult(null); }}
            className={`flex-1 py-2 text-xs font-medium rounded-lg flex items-center justify-center gap-2 transition-all ${
              activeTab === 'github' ? 'bg-white text-indigo-600 shadow-xs' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <Github size={15} />
            <span>GitHub Repository</span>
          </button>
          <button
            type="button"
            onClick={() => { setActiveTab('local'); setError(null); setResult(null); }}
            className={`flex-1 py-2 text-xs font-medium rounded-lg flex items-center justify-center gap-2 transition-all ${
              activeTab === 'local' ? 'bg-white text-indigo-600 shadow-xs' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <Folder size={15} />
            <span>Local Folder</span>
          </button>
        </div>

        <div className="p-6">
          {activeTab === 'github' ? (
            <form onSubmit={handleGithubSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1.5">GitHub Repository URL</label>
                <input
                  type="text"
                  value={githubUrl}
                  onChange={(e) => setGithubUrl(e.target.value)}
                  placeholder="https://github.com/owner/repository"
                  className="w-full text-xs px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-hidden focus:border-indigo-500"
                  required
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1.5">Branch</label>
                  <input
                    type="text"
                    value={branch}
                    onChange={(e) => setBranch(e.target.value)}
                    placeholder="main"
                    className="w-full text-xs px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-hidden focus:border-indigo-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1.5">Token (Optional)</label>
                  <input
                    type="password"
                    value={token}
                    onChange={(e) => setToken(e.target.value)}
                    placeholder="ghp_..."
                    className="w-full text-xs px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-hidden focus:border-indigo-500"
                  />
                </div>
              </div>
              <button
                type="submit"
                disabled={loading || !githubUrl.trim()}
                className="w-full btn btn-primary text-xs py-2.5 rounded-xl flex items-center justify-center gap-2"
              >
                {loading ? <Loader2 size={16} className="animate-spin" /> : <Github size={16} />}
                <span>{loading ? 'Cloning & Indexing Repository...' : 'Clone & Ingest Repository'}</span>
              </button>
            </form>
          ) : (
            <form onSubmit={handleLocalSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1.5">Local Directory Path</label>
                <input
                  type="text"
                  value={folderPath}
                  onChange={(e) => setFolderPath(e.target.value)}
                  placeholder="C:\Projects\my-codebase or ./src"
                  className="w-full text-xs px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-hidden focus:border-indigo-500"
                  required
                />
              </div>
              <button
                type="submit"
                disabled={loading || !folderPath.trim()}
                className="w-full btn btn-primary text-xs py-2.5 rounded-xl flex items-center justify-center gap-2"
              >
                {loading ? <Loader2 size={16} className="animate-spin" /> : <Folder size={16} />}
                <span>{loading ? 'Scanning & Indexing Folder...' : 'Scan & Ingest Local Folder'}</span>
              </button>
            </form>
          )}

          {error && (
            <div className="mt-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-xl text-xs flex items-start gap-2">
              <AlertCircle size={16} className="shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          {result && (
            <div className="mt-4 p-3.5 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-xl text-xs flex items-start gap-2.5">
              <CheckCircle2 size={18} className="text-emerald-600 shrink-0 mt-0.5" />
              <div>
                <p className="font-semibold">Ingestion completed successfully!</p>
                <p className="text-[11px] text-emerald-700 mt-0.5">
                  Processed {result.processed_files || result.total_files || 0} files ({result.total_chunks || 0} code & document chunks indexed).
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
