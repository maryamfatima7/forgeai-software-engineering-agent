import { useEffect, useMemo, useState } from 'react'
import { unzipSync, strFromU8 } from 'fflate'
import { motion } from 'framer-motion'
import {
  Activity, AlertTriangle, ArrowUpRight, BrainCircuit, CheckCircle2, ChevronDown, CircleDot, Code2,
  FileCode2, FileText, FolderGit2, GitBranch, LayoutDashboard, LoaderCircle, Menu, Network, Play,
  RefreshCw, ScanSearch, Settings2, ShieldCheck, TestTube2, Upload, X,
} from 'lucide-react'
import { getCurrentUser, getHealth, getJson, loginUser, logoutUser, postJson, registerUser } from './api/client.js'

const navigation = [
  ['Overview', LayoutDashboard, 'overview'], ['Repository Intelligence', FolderGit2, 'repository'], ['Code Analyzer', FileCode2, 'code'],
  ['Engineering Copilot', BrainCircuit, 'copilot'], ['Debugging Agent', AlertTriangle, 'debugging'], ['Semantic Search / RAG', ScanSearch, 'semantic'],
  ['Security Reviewer', ShieldCheck, 'security'], ['Test Engineer', TestTube2, 'tests'], ['Architecture Analyzer', Network, 'architecture'],
  ['Documentation Agent', FileText, 'documentation'], ['Project Health', Activity, 'health'], ['Implementation Planner', Play, 'planner'],
]

const views = {
  code: { title: 'Code analysis', endpoint: '/api/v1/code/analyze', action: 'Analyze code' },
  security: { title: 'Security review', endpoint: '/api/v1/security/review', action: 'Run security review' },
  tests: { title: 'Testing analysis', endpoint: '/api/v1/tests/analyze', action: 'Find testing gaps' },
  architecture: { title: 'Architecture', endpoint: '/api/v1/architecture/analyze', action: 'Analyze architecture' },
  documentation: { title: 'Documentation', endpoint: '/api/v1/documentation/generate', action: 'Generate suggestions' },
  health: { title: 'Project health', endpoint: '/api/v1/project/health', action: 'Refresh project health', method: 'get' },
  planner: { title: 'Implementation planner', endpoint: '/api/v1/implementation/plan', action: 'Create implementation plan' },
}

function App() {
  const [user, setUser] = useState(null)
  const [authLoading, setAuthLoading] = useState(true)
  const [authMode, setAuthMode] = useState(window.location.pathname === '/register' ? 'register' : 'login')

  useEffect(() => {
    const syncRoute = () => setAuthMode(window.location.pathname === '/register' ? 'register' : 'login')
    const handleUnauthorized = () => {
      const mode = window.location.pathname === '/register' ? 'register' : 'login'
      window.history.replaceState({}, '', `/${mode}`)
      setAuthMode(mode)
      setUser(null)
    }
    window.addEventListener('popstate', syncRoute)
    window.addEventListener('forgeai:unauthorized', handleUnauthorized)
    getCurrentUser().then((response) => {
      if (window.location.pathname === '/login' || window.location.pathname === '/register' || window.location.pathname === '/') window.history.replaceState({}, '', '/dashboard')
      setUser(response.user)
    }).catch(() => {
      if (window.location.pathname !== '/login' && window.location.pathname !== '/register') window.history.replaceState({}, '', '/login')
      setUser(null)
    }).finally(() => setAuthLoading(false))
    return () => { window.removeEventListener('popstate', syncRoute); window.removeEventListener('forgeai:unauthorized', handleUnauthorized) }
  }, [])

  function showAuth(mode) {
    window.history.pushState({}, '', `/${mode}`)
    setAuthMode(mode)
  }

  function handleAuthenticated(nextUser) {
    window.history.pushState({}, '', '/dashboard')
    setUser(nextUser)
  }

  async function handleLogout() {
    await logoutUser().catch(() => undefined)
    window.history.pushState({}, '', '/login')
    setUser(null)
    setAuthMode('login')
  }

  if (authLoading) return <AuthLoading />
  if (!user) return <AuthScreen mode={authMode} onModeChange={showAuth} onAuthenticated={handleAuthenticated} />
  return <Dashboard user={user} onLogout={handleLogout} />
}

function AuthLoading() { return <div className="auth-shell"><div className="auth-loading"><LoaderCircle className="spin" size={21} /> Restoring your ForgeAI session...</div></div> }

function AuthScreen({ mode, onModeChange, onAuthenticated }) {
  const isRegister = mode === 'register'
  const [form, setForm] = useState({ full_name: '', email: '', password: '', confirm_password: '' })
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  function updateField(event) { setForm((current) => ({ ...current, [event.target.name]: event.target.value })) }

  async function submit(event) {
    event.preventDefault(); setError('')
    if (isRegister && form.password !== form.confirm_password) { setError('Passwords do not match.'); return }
    setBusy(true)
    try {
      const response = await (isRegister ? registerUser(form) : loginUser({ email: form.email, password: form.password }))
      onAuthenticated(response.user)
    } catch (requestError) { setError(requestError.message) } finally { setBusy(false) }
  }

  return <main className="auth-shell"><section className="auth-panel"><div className="auth-brand"><div className="brand-mark"><GitBranch size={19} strokeWidth={2.6} /></div><div><strong>ForgeAI</strong><span>Engineering intelligence</span></div></div><div className="auth-copy"><div className="eyebrow"><span className="eyebrow-line" />{isRegister ? 'CREATE ACCOUNT' : 'WELCOME BACK'}</div><h1>{isRegister ? 'Build with better context.' : 'Return to your workspace.'}</h1><p>{isRegister ? 'Create a secure ForgeAI workspace for repository-aware engineering.' : 'Sign in to continue with your repository intelligence workspace.'}</p></div><form className="auth-form" onSubmit={submit}>{isRegister && <label>Full name<input name="full_name" value={form.full_name} onChange={updateField} autoComplete="name" required placeholder="Ada Lovelace" /></label>}<label>Email<input name="email" type="email" value={form.email} onChange={updateField} autoComplete="email" required placeholder="you@company.com" /></label><label>Password<input name="password" type="password" value={form.password} onChange={updateField} autoComplete={isRegister ? 'new-password' : 'current-password'} required placeholder="At least 8 characters" /></label>{isRegister && <label>Confirm password<input name="confirm_password" type="password" value={form.confirm_password} onChange={updateField} autoComplete="new-password" required placeholder="Repeat your password" /></label>}{error && <ErrorBanner message={error} />}<button className="primary-button auth-submit" type="submit" disabled={busy}>{busy && <LoaderCircle className="spin" size={17} />}{busy ? 'Working...' : isRegister ? 'Create account' : 'Log in'}</button></form><p className="auth-switch">{isRegister ? 'Already have an account?' : 'New to ForgeAI?'} <button type="button" onClick={() => onModeChange(isRegister ? 'login' : 'register')}>{isRegister ? 'Log in' : 'Create an account'}</button></p></section><aside className="auth-aside"><div className="auth-aside-mark"><BrainCircuit size={26} /></div><strong>Engineering work, grounded in your code.</strong><span>Analyze repositories, trace behavior, review risk, and plan implementation with one secure workspace.</span></aside></main> }

function Dashboard({ user, onLogout }) {
  const [activeView, setActiveView] = useState('overview')
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [repoFiles, setRepoFiles] = useState([])
  const [scan, setScan] = useState(null)
  const [result, setResult] = useState(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [health, setHealth] = useState({ status: 'loading', message: 'Checking API connection...' })

  useEffect(() => { getHealth().then((data) => setHealth({ status: 'connected', message: `API online · v${data.version}` })).catch(() => setHealth({ status: 'offline', message: 'API unavailable' })) }, [])
  const payload = useMemo(() => ({ files: repoFiles }), [repoFiles])

  async function uploadFiles(fileList) {
    setError(''); setScan(null); setResult(null)
    try {
      const files = await readProjectFiles(Array.from(fileList))
      if (!files.length) throw new Error('No readable text files were found in that selection.')
      setRepoFiles(files)
      setScan(await postJson('/api/v1/repository/scan', { files }))
      setActiveView('repository')
    } catch (uploadError) { setError(uploadError.message) }
  }

  async function run(endpoint, request = payload) {
    setBusy(true); setError(''); setResult(null)
    try {
      const response = await postJson(endpoint, request)
      setResult(response)
      return response
    } catch (requestError) { setError(requestError.message); return null } finally { setBusy(false) }
  }

  async function runGet(endpoint) {
    setBusy(true); setError(''); setResult(null)
    try {
      const response = await getJson(endpoint)
      setResult(response)
      return response
    } catch (requestError) { setError(requestError.message); return null } finally { setBusy(false) }
  }

  function selectView(view) { setActiveView(view); setSidebarOpen(false); setError(''); if (view === 'overview') setResult(null) }

  return <div className="app-shell">
    <aside className={`sidebar ${sidebarOpen ? 'sidebar-open' : ''}`}>
      <div className="brand-row"><div className="brand-mark"><GitBranch size={19} strokeWidth={2.6} /></div><div><div className="brand-name">ForgeAI</div><div className="brand-subtitle">Engineering intelligence</div></div><button className="icon-button mobile-close" aria-label="Close navigation" onClick={() => setSidebarOpen(false)}><X size={18} /></button></div>
      <div className="workspace-switcher"><div className="workspace-icon">F</div><div className="workspace-copy"><span>Workspace</span><strong>ForgeAI Platform</strong></div><ChevronDown size={15} /></div>
      <nav className="nav-list" aria-label="Primary navigation"><span className="nav-label">Workspace</span>{navigation.map(([label, Icon, key]) => <button className={`nav-item ${activeView === key ? 'active' : ''}`} key={key} onClick={() => selectView(key)}><Icon size={17} /><span>{label}</span>{key === 'copilot' && <span className="nav-dot" />}</button>)}</nav>
      <div className="sidebar-footer"><button className="nav-item"><Settings2 size={17} /><span>Settings</span></button><div className="profile-row"><div className="avatar">{user.full_name.slice(0, 2).toUpperCase()}</div><div><strong>{user.full_name}</strong><span>{repoFiles.length ? `${repoFiles.length} files loaded` : user.email}</span></div><span className="more-icon">•••</span></div></div>
    </aside>
    {sidebarOpen && <button className="sidebar-backdrop" aria-label="Close navigation" onClick={() => setSidebarOpen(false)} />}
    <main className="main-content">
      <header className="topbar"><button className="icon-button mobile-menu" aria-label="Open navigation" onClick={() => setSidebarOpen(true)}><Menu size={20} /></button><div className="breadcrumbs"><span>Workspace</span><span>/</span><strong>{navigation.find(([, , key]) => key === activeView)?.[0] || 'Overview'}</strong></div><div className="topbar-actions"><div className={`connection-status ${health.status}`}><span className="status-pip" />{health.message}</div><button className="icon-button" aria-label="Refresh API" onClick={() => getHealth().then((data) => setHealth({ status: 'connected', message: `API online · v${data.version}` })).catch(() => setHealth({ status: 'offline', message: 'API unavailable' }))}><RefreshCw size={17} /></button><div className="account-area"><div className="top-avatar" aria-hidden="true">{user.full_name.slice(0, 2).toUpperCase()}</div><div className="account-copy"><strong>{user.full_name}</strong><span>{user.email}</span></div><button className="logout-button" onClick={onLogout}>Log out</button></div></div></header>
      <div className="content-wrap"><motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} key={activeView}>
        {activeView === 'overview' && <Overview repoFiles={repoFiles} scan={scan} onNavigate={selectView} onUpload={uploadFiles} />}
        {activeView === 'repository' && <RepositoryView repoFiles={repoFiles} scan={scan} onUpload={uploadFiles} onRun={() => run('/api/v1/repository/analyze')} busy={busy} />}
        {['copilot', 'debugging', 'semantic', 'planner'].includes(activeView) && <CopilotView payload={payload} onRun={run} busy={busy} result={result} error={error} mode={activeView} />}
        {views[activeView] && activeView !== 'planner' && <AnalysisView config={views[activeView]} result={result} error={error} repoFiles={repoFiles} onRun={() => views[activeView].method === 'get' ? runGet(views[activeView].endpoint) : run(views[activeView].endpoint)} busy={busy} />}
      </motion.div></div>
    </main>
  </div>
}

function Overview({ repoFiles, scan, onNavigate, onUpload }) { return <>
  <section className="page-intro"><div><div className="eyebrow"><span className="eyebrow-line" />PROJECT OVERVIEW</div><h1>Good morning, <em>engineer.</em></h1><p>{repoFiles.length ? 'Your repository is loaded and ready for engineering analysis.' : 'Your repository intelligence workspace is ready when you are.'}</p></div><UploadButton onUpload={onUpload} label={repoFiles.length ? 'Replace repository' : 'Upload repository'} /></section>
  <section className="health-banner"><div className="health-symbol"><ShieldCheck size={21} /></div><div className="health-copy"><strong>Project health</strong><span>{repoFiles.length ? `${scan?.file_count || repoFiles.length} supported files loaded. Run an analysis to collect project signals.` : 'Connect a repository to begin analysis.'}</span></div><span className="empty-badge">{repoFiles.length ? 'Ready to analyze' : 'Awaiting repository'}</span></section>
  <div className="section-heading"><div><h2>Workspace status</h2><span>Core systems and project signals</span></div><button className="text-button" onClick={() => onNavigate('repository')}>Open repository <ArrowUpRight size={15} /></button></div>
  <div className="status-grid"><StatusCard icon={FolderGit2} label="Repository" title={repoFiles.length ? `${repoFiles.length} files loaded` : 'Not connected'} detail={repoFiles.length ? 'Request-scoped project snapshot' : 'Upload files or a project folder'} action="Open repository" onClick={() => onNavigate('repository')} /><StatusCard icon={Code2} label="Code intelligence" title={repoFiles.length ? 'Ready' : 'Standing by'} detail="AST and lightweight source analysis" action="Analyze code" onClick={() => onNavigate('code')} /><StatusCard icon={ShieldCheck} label="Security" title={repoFiles.length ? 'Ready' : 'Not assessed'} detail="Static heuristic review only" action="Open security" onClick={() => onNavigate('security')} /></div>
  <section className="copilot-spotlight"><div><div className="eyebrow"><span className="eyebrow-line" />AI ENGINEERING AGENT</div><h2>ForgeAI Engineering Copilot</h2><p>Ask grounded questions about your repository, debug behavior, search code context, and plan implementation work.</p></div><button className="primary-button" onClick={() => onNavigate('copilot')}><BrainCircuit size={17} />Open Copilot</button></section>
  <div className="lower-grid"><section className="panel"><div className="panel-heading"><div><h2>Recent activity</h2><span>Repository events and analysis work</span></div><Activity size={17} /></div><EmptyState icon={Activity} title={repoFiles.length ? 'No analysis runs yet' : 'No activity yet'} detail={repoFiles.length ? 'Choose an analysis view to generate the first result.' : 'Upload a repository to begin.'} /></section><section className="panel"><div className="panel-heading"><div><h2>Quick actions</h2><span>Start with a focused workflow</span></div><Play size={17} /></div><div className="quick-actions"><QuickAction icon={FolderGit2} title="Upload repository" detail="Add project files to ForgeAI" onClick={() => document.getElementById('repo-upload').click()} /><QuickAction icon={FileCode2} title="Analyze code" detail="Find code issues and symbols" disabled={!repoFiles.length} onClick={() => onNavigate('code')} /><QuickAction icon={BrainCircuit} title="Ask the copilot" detail="Question your repository" disabled={!repoFiles.length} onClick={() => onNavigate('copilot')} /></div></section></div>
</> }

function RepositoryView({ repoFiles, scan, onUpload, onRun, busy }) { return <><PageHeading eyebrow="REPOSITORY" title="Repository workspace" detail="Load a project snapshot for request-scoped analysis. Uploaded code is never executed." /><div className="repository-layout"><section className="panel upload-panel"><UploadButton onUpload={onUpload} label="Choose files or folder" large /><p className="muted-copy">Text files and ZIP archives are supported. Environment files, binaries, generated directories, unsafe paths, and oversized files are rejected or skipped.</p>{scan && <div className="repo-stats"><Stat label="Supported files" value={scan.file_count} /><Stat label="Total size" value={`${Math.ceil(scan.total_bytes / 1024)} KB`} /><Stat label="Languages" value={Object.keys(scan.languages).length} /></div>}</section><section className="panel file-panel"><div className="panel-heading"><div><h2>Indexed files</h2><span>{repoFiles.length ? 'Redacted, request-scoped content' : 'No repository loaded'}</span></div><ScanSearch size={17} /></div>{repoFiles.length ? <div className="file-list">{repoFiles.slice(0, 80).map((file) => <div className="file-row" key={file.path}><FileCode2 size={15} /><span>{file.path}</span><small>{file.content.split('\n').length} lines</small></div>)}{repoFiles.length > 80 && <span className="muted-copy">Showing 80 of {repoFiles.length} files.</span>}</div> : <EmptyState icon={FolderGit2} title="No repository loaded" detail="Choose a folder or a set of source files to inspect its structure." />}</section></div>{repoFiles.length > 0 && <button className="primary-button action-button" onClick={onRun} disabled={busy}>{busy ? <LoaderCircle className="spin" size={17} /> : <ScanSearch size={17} />}{busy ? 'Analyzing...' : 'Analyze repository'}</button>}</> }

function CopilotView({ payload, onRun, busy, result, error, mode = 'copilot' }) {
  const [question, setQuestion] = useState('')
  const [messages, setMessages] = useState([])
  const prompts = {
    copilot: { eyebrow: 'AI ENGINEERING AGENT', title: 'ForgeAI Engineering Copilot', detail: 'Ask grounded questions about the loaded repository and get file references with every answer.', placeholder: 'Where is authentication handled? What should I test first?' },
    debugging: { eyebrow: 'DEBUGGING AGENT', title: 'Debugging Agent', detail: 'Describe a failure and the agent will reason from the loaded source context.', placeholder: 'Why could this request return a 500? Trace the likely failure path.' },
    semantic: { eyebrow: 'SEMANTIC CODE SEARCH / RAG', title: 'Semantic Code Search', detail: 'Search the request-scoped repository context using an engineering question.', placeholder: 'Find the modules responsible for repository ingestion and redaction.' },
    planner: { eyebrow: 'IMPLEMENTATION PLANNER', title: 'Implementation Planner', detail: 'Turn repository evidence and a goal into a structured implementation plan.', placeholder: 'Plan adding authentication while preserving the current API boundaries.' },
  }[mode]
  async function submit(event) {
    event?.preventDefault()
    const userRequest = question.trim()
    if (!userRequest || !payload.files.length || busy) return
    setMessages((current) => [...current, userRequest])
    setQuestion('')
    await onRun(mode === 'planner' ? '/api/v1/implementation/plan' : '/api/v1/copilot/chat', { ...payload, user_request: userRequest })
  }
  return <><PageHeading eyebrow={prompts.eyebrow} title={prompts.title} detail={prompts.detail} /><section className="panel copilot-panel"><div className="copilot-intro"><BrainCircuit size={24} /><div><strong>Repository-aware engineering assistant</strong><span>Gemini is used only when configured. Upload a repository to ground the response in real project files.</span></div></div><div className="message-list" aria-live="polite">{messages.length === 0 && <div className="message-empty">Your engineering conversation will appear here.</div>}{messages.map((message, index) => <div className="message user-message" key={`${message}-${index}`}><span className="message-label">You</span><p>{message}</p></div>)}{busy && <div className="message assistant-message"><span className="message-label">ForgeAI Agent</span><p><LoaderCircle className="spin" size={15} /> Reviewing repository context...</p></div>}</div><form onSubmit={submit}><textarea className="copilot-input" value={question} onChange={(event) => setQuestion(event.target.value)} placeholder={prompts.placeholder} aria-label="Engineering agent request" /><div className="copilot-actions"><span className="context-status">{payload.files.length ? `${payload.files.length} repository files in context` : 'Upload a repository to enable grounded answers'}</span><button className="primary-button" type="submit" disabled={!question.trim() || !payload.files.length || busy}>{busy ? <LoaderCircle className="spin" size={17} /> : <BrainCircuit size={17} />}{busy ? 'Thinking...' : mode === 'planner' ? 'Create plan' : 'Send to agent'}</button></div></form></section>{error && <ErrorBanner message={error} />}{result && <section className="panel assistant-result"><div className="panel-heading"><div><h2>Agent response</h2><span>{mode === 'planner' ? 'Structured implementation guidance' : 'Grounded in retrieved repository files'}</span></div><CheckCircle2 size={17} /></div><p className="assistant-answer">{result.answer}</p>{result.sources?.length > 0 && <div className="source-list"><strong>Referenced files</strong>{result.sources.map((source) => <span key={source}>{source}</span>)}</div>}{mode === 'planner' && result.implementation_steps?.length > 0 && <div className="source-list"><strong>Implementation steps</strong>{result.implementation_steps.map((step) => <span key={step}>{step}</span>)}</div>}</section>}</>
}

function AnalysisView({ config, result, error, repoFiles, onRun, busy }) {
  const repositoryRequired = config.method !== 'get'
  return <><PageHeading eyebrow="ENGINEERING WORKFLOW" title={config.title} detail="Results are computed from the currently loaded repository snapshot." /><section className="panel analysis-toolbar"><div><strong>{repoFiles.length ? `${repoFiles.length} files available` : repositoryRequired ? 'Repository required' : 'Workspace health available'}</strong><span>{repoFiles.length ? 'Run this focused workflow when ready.' : repositoryRequired ? 'Open Repository and upload project files first.' : 'Check the current API and workspace health status.'}</span></div><button className="primary-button" disabled={(repositoryRequired && !repoFiles.length) || busy} onClick={onRun}>{busy ? <LoaderCircle className="spin" size={17} /> : <ScanSearch size={17} />}{busy ? 'Working...' : config.action}</button></section>{error && <ErrorBanner message={error} />}{result && <ResultPanel result={result} />}{!result && !error && <EmptyState icon={CircleDot} title="No result yet" detail="Run the workflow to inspect actual repository evidence." />}</>
}

function ResultPanel({ result }) {
  const entries = [result.findings, result.suggestions, result.coverage_gaps, result.components, result.module_explanations, result.symbols, result.recommendations].find((items) => Array.isArray(items) && items.length) || []
  const architectureSummary = typeof result.architecture_summary === 'string' ? result.architecture_summary : result.architecture_summary?.architecture_summary
  return <section className="panel result-panel"><div className="panel-heading"><div><h2>Analysis result</h2><span>Structured output from the current repository snapshot</span></div><CheckCircle2 size={17} /></div>{result.review_type && <div className="result-note">{result.review_type}</div>}{architectureSummary && <p className="result-summary">{architectureSummary}</p>}{result.repository_overview && <div className="repo-stats"><Stat label="Files" value={result.repository_overview.file_count ?? 0} /><Stat label="Bytes" value={result.repository_overview.total_bytes ?? 0} /></div>}<div className="result-list">{entries.length ? entries.slice(0, 30).map((entry, index) => <div className="result-item" key={index}><span className={`severity-dot ${(entry.severity || 'info').toLowerCase()}`} /><div><strong>{entry.description || entry.area || entry.name || entry}</strong><small>{entry.file ? `${entry.file}${entry.line ? `:${entry.line}` : ''}` : entry.rationale || entry.reason || ''}</small></div></div>) : <EmptyState icon={CheckCircle2} title="No findings returned" detail="The workflow did not identify items in the supplied snapshot." />}</div></section>
}

function UploadButton({ onUpload, label, large }) { return <label className={`primary-button upload-button ${large ? 'large-upload' : ''}`}><Upload size={17} />{label}<input id="repo-upload" type="file" multiple webkitdirectory="true" onChange={(event) => onUpload(event.target.files)} /></label> }
function PageHeading({ eyebrow, title, detail }) { return <section className="page-intro"><div><div className="eyebrow"><span className="eyebrow-line" />{eyebrow}</div><h1>{title}</h1><p>{detail}</p></div></section> }
function StatusCard({ icon: Icon, label, title, detail, action, onClick }) { return <article className="status-card"><div className="card-icon"><Icon size={18} /></div><span className="card-label">{label}</span><h3>{title}</h3><p>{detail}</p><button className="card-action" onClick={onClick}>{action}<ArrowUpRight size={14} /></button></article> }
function QuickAction({ icon: Icon, title, detail, disabled, onClick }) { return <button className={`quick-action ${disabled ? 'disabled' : ''}`} disabled={disabled} onClick={onClick}><span className="quick-icon"><Icon size={17} /></span><span><strong>{title}</strong><small>{detail}</small></span><ArrowUpRight size={15} /></button> }
function EmptyState({ icon: Icon, title, detail }) { return <div className="empty-state"><div className="empty-icon"><Icon size={20} /></div><strong>{title}</strong><span>{detail}</span></div> }
function ErrorBanner({ message }) { return <div className="error-banner"><AlertTriangle size={17} /><span>{message}</span></div> }
function Stat({ label, value }) { return <div className="stat"><span>{label}</span><strong>{value}</strong></div> }

async function readProjectFiles(fileList) {
  const files = []
  for (const file of fileList) {
    const relativePath = file.webkitRelativePath || file.name
    if (/\.(zip)$/i.test(file.name)) {
      const archive = unzipSync(new Uint8Array(await file.arrayBuffer()))
      for (const [path, bytes] of Object.entries(archive)) if (!path.endsWith('/') && !bytes.includes(0)) files.push({ path, content: strFromU8(bytes) })
      continue
    }
    const bytes = new Uint8Array(await file.arrayBuffer())
    if (bytes.includes(0)) continue
    files.push({ path: relativePath, content: new TextDecoder().decode(bytes) })
  }
  return files
}

export default App
