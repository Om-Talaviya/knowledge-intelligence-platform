import React, { useState } from 'react'
import axios, { AxiosError } from 'axios'
import {
  Search,
  Sparkles,
  Bot,
  Layers,
  FileCode,
  Loader2,
  AlertCircle,
} from 'lucide-react'
import ReactMarkdown from 'react-markdown'

interface ResearchGoal {
  goal_id: string
  description: string
  target_domains: string[]
  status: string
}

interface ResearchCitation {
  citation_id: string
  source_path: string
  lines: string | null
  summary: string
}

interface ResearchResponse {
  query: string
  executive_summary: string
  markdown_body: string
  goals: ResearchGoal[]
  citations: ResearchCitation[]
  steps_executed: number
}

const SAMPLE_QUERIES = [
  'How does document chunking and token budgeting work in KIP?',
  'Explain JWT authentication, password hashing, and token validation flow.',
  'How does hybrid search combine BM25 and vector embeddings using RRF?',
  'What security guardrails and path traversal protections exist for file uploads?',
]

export function Research() {
  const [query, setQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [researchData, setResearchData] = useState<ResearchResponse | null>(null)

  const handleResearch = async (searchQuery: string) => {
    const q = searchQuery.trim()
    if (!q || loading) return

    setLoading(true)
    setError(null)
    setResearchData(null)

    try {
      const resp = await axios.post<ResearchResponse>('/api/agent/research', {
        query: q,
      })
      setResearchData(resp.data)
    } catch (err) {
      const axiosErr = err as AxiosError<{ detail?: string }>
      setError(axiosErr.response?.data?.detail || axiosErr.message || 'Failed to execute deep research agent')
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    handleResearch(query)
  }

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="badge bg-indigo-50 text-indigo-700 border-indigo-200 text-xs font-semibold py-0.5 px-2.5 flex items-center gap-1.5">
              <Bot size={13} /> Autonomous Agent v2
            </span>
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">Deep Codebase Research Agent</h1>
          <p className="text-xs text-[var(--color-text-muted)] mt-1">
            Autonomous multi-hop investigation across codebase AST symbols, documentation, and architecture figures.
          </p>
        </div>
      </div>

      {/* Query Search Card */}
      <div className="card p-6 bg-white shadow-card border border-[var(--color-border)]">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="relative">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ask complex technical questions about code flow, architecture, or schemas..."
              className="w-full text-sm pl-11 pr-32 py-3.5 bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-hidden focus:border-indigo-500 shadow-2xs font-normal"
              disabled={loading}
            />
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
            <button
              type="submit"
              disabled={loading || !query.trim()}
              className="absolute right-2 top-1/2 -translate-y-1/2 btn btn-primary text-xs py-2 px-4 rounded-lg flex items-center gap-1.5 cursor-pointer shadow-xs"
            >
              {loading ? <Loader2 size={14} className="animate-spin" /> : <Sparkles size={14} />}
              <span>{loading ? 'Investigating...' : 'Research'}</span>
            </button>
          </div>

          {/* Quick Suggestions */}
          <div>
            <p className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 mb-2">
              Recommended Investigation Prompts
            </p>
            <div className="flex flex-wrap gap-2">
              {SAMPLE_QUERIES.map((sample) => (
                <button
                  key={sample}
                  type="button"
                  onClick={() => {
                    setQuery(sample)
                    handleResearch(sample)
                  }}
                  className="text-xs px-3 py-1.5 bg-slate-50 hover:bg-indigo-50/70 border border-slate-200 hover:border-indigo-300 rounded-lg text-slate-700 transition-colors text-left cursor-pointer"
                >
                  {sample}
                </button>
              ))}
            </div>
          </div>
        </form>

        {error && (
          <div className="mt-4 p-3.5 bg-red-50 border border-red-200 text-red-700 rounded-xl text-xs flex items-start gap-2.5">
            <AlertCircle size={16} className="shrink-0 mt-0.5" />
            <span>{error}</span>
          </div>
        )}
      </div>

      {/* Loading State with Progress Steps */}
      {loading && (
        <div className="card p-10 text-center bg-white border border-[var(--color-border)] animate-pulse">
          <Loader2 size={36} className="mx-auto text-[var(--color-primary)] animate-spin mb-3" />
          <h3 className="text-sm font-semibold text-slate-900">Autonomous Agent is Researching Codebase...</h3>
          <p className="text-xs text-[var(--color-text-muted)] mt-1 max-w-md mx-auto">
            Decomposing research plan &rarr; inspecting symbols &rarr; extracting source slices &rarr; synthesizing grounded report.
          </p>
        </div>
      )}

      {/* Research Output View */}
      {researchData && !loading && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Markdown Report */}
          <div className="lg:col-span-2 space-y-6">
            <div className="card p-8 bg-white border border-[var(--color-border)] shadow-card">
              <div className="prose prose-slate max-w-none text-xs leading-relaxed">
                <ReactMarkdown>{researchData.markdown_body}</ReactMarkdown>
              </div>
            </div>
          </div>

          {/* Right Sidebar: Plan Breakdown & Verified Citations */}
          <div className="space-y-6">
            {/* Research Goals Card */}
            <div className="card p-5 bg-white border border-[var(--color-border)] shadow-card">
              <div className="flex items-center gap-2 pb-3 border-b border-slate-100">
                <Layers size={16} className="text-indigo-600" />
                <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider">Research Plan</h3>
              </div>
              <div className="mt-4 space-y-3">
                {researchData.goals.map((g, idx) => (
                  <div key={g.goal_id} className="p-3 bg-slate-50 border border-slate-200/80 rounded-xl text-xs space-y-1.5">
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-slate-800">Step {idx + 1}</span>
                      <span className="badge badge-success text-[10px] py-0.5">Verified</span>
                    </div>
                    <p className="text-[11px] text-slate-600 leading-snug">{g.description}</p>
                    <div className="flex flex-wrap gap-1 pt-1">
                      {g.target_domains.map((dom) => (
                        <span key={dom} className="badge badge-neutral text-[9px] py-0">
                          {dom}
                        </span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Citations Card */}
            <div className="card p-5 bg-white border border-[var(--color-border)] shadow-card">
              <div className="flex items-center gap-2 pb-3 border-b border-slate-100">
                <FileCode size={16} className="text-indigo-600" />
                <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider">Verified Citations</h3>
              </div>
              <div className="mt-4 space-y-2.5">
                {researchData.citations.length === 0 ? (
                  <p className="text-xs text-slate-500 italic">No direct file slices referenced.</p>
                ) : (
                  researchData.citations.map((c) => (
                    <div key={c.citation_id} className="p-2.5 bg-slate-50 border border-slate-200/80 rounded-lg text-xs">
                      <div className="flex items-center justify-between font-mono text-[11px] text-indigo-700">
                        <span className="font-semibold">{c.citation_id}</span>
                        <span>{c.lines || 'Full File'}</span>
                      </div>
                      <p className="text-[11px] text-slate-800 font-semibold truncate mt-1">{c.source_path}</p>
                      <p className="text-[10px] text-slate-500 mt-0.5">{c.summary}</p>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
