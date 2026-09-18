import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import {
  Activity,
  ArrowUpRight,
  Box,
  BrainCircuit,
  Bug,
  CheckCircle2,
  ChevronDown,
  FileCode2,
  FolderGit2,
  GitBranch,
  LayoutDashboard,
  LockKeyhole,
  Menu,
  Network,
  Play,
  Settings2,
  ShieldCheck,
  TestTube2,
  X,
} from 'lucide-react'
import { getHealth } from './api/client.js'

const navigation = [
  { label: 'Overview', icon: LayoutDashboard },
  { label: 'Repository', icon: FolderGit2 },
  { label: 'Code Analysis', icon: FileCode2 },
  { label: 'AI Copilot', icon: BrainCircuit },
  { label: 'Security', icon: ShieldCheck },
  { label: 'Tests', icon: TestTube2 },
  { label: 'Architecture', icon: Network },
  { label: 'Documentation', icon: Box },
]

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [health, setHealth] = useState({ status: 'loading', message: 'Checking API connection...' })

  useEffect(() => {
    getHealth()
      .then((data) => setHealth({ status: 'connected', message: `API online · v${data.version}` }))
      .catch(() => setHealth({ status: 'offline', message: 'API unavailable · start the backend to connect' }))
  }, [])

  return (
    <div className="app-shell">
      <aside className={`sidebar ${sidebarOpen ? 'sidebar-open' : ''}`}>
        <div className="brand-row">
          <div className="brand-mark"><GitBranch size={19} strokeWidth={2.6} /></div>
          <div><div className="brand-name">ForgeAI</div><div className="brand-subtitle">Engineering intelligence</div></div>
          <button className="icon-button mobile-close" aria-label="Close navigation" onClick={() => setSidebarOpen(false)}><X size={18} /></button>
        </div>
        <div className="workspace-switcher"><div className="workspace-icon">F</div><div className="workspace-copy"><span>Workspace</span><strong>ForgeAI Platform</strong></div><ChevronDown size={15} /></div>
        <nav className="nav-list" aria-label="Primary navigation">
          <span className="nav-label">Workspace</span>
          {navigation.map(({ label, icon: Icon }, index) => <button className={`nav-item ${index === 0 ? 'active' : ''}`} key={label} onClick={() => setSidebarOpen(false)}><Icon size={17} /><span>{label}</span>{label === 'AI Copilot' && <span className="nav-dot" />}</button>)}
        </nav>
        <div className="sidebar-footer"><button className="nav-item"><Settings2 size={17} /><span>Settings</span></button><div className="profile-row"><div className="avatar">FA</div><div><strong>ForgeAI Admin</strong><span>Local workspace</span></div><MoreIcon /></div></div>
      </aside>
      {sidebarOpen && <button className="sidebar-backdrop" aria-label="Close navigation" onClick={() => setSidebarOpen(false)} />}
      <main className="main-content">
        <header className="topbar"><button className="icon-button mobile-menu" aria-label="Open navigation" onClick={() => setSidebarOpen(true)}><Menu size={20} /></button><div className="breadcrumbs"><span>Workspace</span><span>/</span><strong>Overview</strong></div><div className="topbar-actions"><div className={`connection-status ${health.status}`}><span className="status-pip" />{health.message}</div><button className="icon-button" aria-label="Activity"><Activity size={18} /></button><button className="top-avatar" aria-label="Account">FA</button></div></header>
        <div className="content-wrap">
          <motion.section className="page-intro" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: .35 }}><div><div className="eyebrow"><span className="eyebrow-line" />PROJECT OVERVIEW</div><h1>Good morning, <em>engineer.</em></h1><p>Your repository intelligence workspace is ready when you are.</p></div><button className="primary-button"><FolderGit2 size={17} />Connect repository</button></motion.section>
          <section className="health-banner"><div className="health-symbol"><ShieldCheck size={21} /></div><div className="health-copy"><strong>Project health</strong><span>No repository connected yet. Connect a repository to begin analysis.</span></div><span className="empty-badge">Awaiting repository</span></section>
          <div className="section-heading"><div><h2>Workspace status</h2><span>Core systems and project signals</span></div><button className="text-button">View details <ArrowUpRight size={15} /></button></div>
          <div className="status-grid"><StatusCard icon={FolderGit2} label="Repository" title="Not connected" detail="Connect a Git repository to begin" action="Connect repository" /><StatusCard icon={BrainCircuit} label="Agent system" title="Standing by" detail="Agents activate after repository setup" action="View agents" /><StatusCard icon={LockKeyhole} label="Security" title="Not assessed" detail="Security review needs repository context" action="Open security" /></div>
          <div className="lower-grid"><section className="panel activity-panel"><div className="panel-heading"><div><h2>Recent activity</h2><span>Repository events and agent work</span></div><Activity size={17} /></div><EmptyState icon={Activity} title="No activity yet" detail="Your repository events will appear here once a project is connected." /></section><section className="panel quick-panel"><div className="panel-heading"><div><h2>Quick actions</h2><span>Start with a focused workflow</span></div><Play size={17} /></div><div className="quick-actions"><QuickAction icon={FolderGit2} title="Connect repository" detail="Add a project to ForgeAI" /><QuickAction icon={FileCode2} title="Explore code" detail="Understand a codebase" disabled /><QuickAction icon={Bug} title="Investigate issue" detail="Trace a bug with context" disabled /></div></section></div>
        </div>
      </main>
    </div>
  )
}

function StatusCard({ icon: Icon, label, title, detail, action }) { return <article className="status-card"><div className="card-icon"><Icon size={18} /></div><span className="card-label">{label}</span><h3>{title}</h3><p>{detail}</p><button className="card-action">{action}<ArrowUpRight size={14} /></button></article> }
function QuickAction({ icon: Icon, title, detail, disabled }) { return <button className={`quick-action ${disabled ? 'disabled' : ''}`} disabled={disabled}><span className="quick-icon"><Icon size={17} /></span><span><strong>{title}</strong><small>{detail}</small></span><ArrowUpRight size={15} /></button> }
function EmptyState({ icon: Icon, title, detail }) { return <div className="empty-state"><div className="empty-icon"><Icon size={20} /></div><strong>{title}</strong><span>{detail}</span></div> }
function MoreIcon() { return <span className="more-icon">•••</span> }

export default App
