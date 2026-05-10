import { useMemo, useRef, useState } from 'react'
import {
  Activity,
  AlertTriangle,
  ArrowUpRight,
  BarChart3,
  Bell,
  Bot,
  Calendar,
  Database,
  FileUp,
  Gauge,
  HelpCircle,
  Home,
  Mail,
  MessageSquareText,
  Plane,
  Plus,
  Search,
  Send,
  Settings,
  ShieldCheck,
  SlidersHorizontal,
  Timer,
  UploadCloud,
  Wrench,
} from 'lucide-react'
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import './App.css'

const API_BASE = 'http://localhost:8001'

const fallbackDashboard = {
  files: [],
  summary: { rows: 0, columns: 0, engines: 100, maxCycle: 206, missingPct: 0 },
  kpis: [
    { label: 'Engines Monitored', value: '100', note: 'Demo FD001 fleet', accent: true },
    { label: 'Healthy Engines', value: '68', note: 'Normal operating profile' },
    { label: 'Warning States', value: '21', note: 'Threshold drift detected' },
    { label: 'Critical Alerts', value: '11', note: 'Maintenance review needed' },
  ],
  trend: [
    { cycle: '0', value: 62 },
    { cycle: '40', value: 66 },
    { cycle: '80', value: 74 },
    { cycle: '120', value: 81 },
    { cycle: '160', value: 93 },
    { cycle: '200', value: 108 },
  ],
  stages: [
    { stage: 'Healthy', count: 44 },
    { stage: 'Early', count: 21 },
    { stage: 'Moderate', count: 17 },
    { stage: 'Critical', count: 11 },
  ],
  sensorSummary: [
    { name: 'sensor_2', mean: 642.3, max: 644.9 },
    { name: 'sensor_3', mean: 1590.1, max: 1616.9 },
    { name: 'sensor_4', mean: 1408.9, max: 1441.4 },
  ],
  maintenance: [],
}

const sensorMix = [
  { name: 'Stable', value: 68, color: '#16824b' },
  { name: 'Drifting', value: 21, color: '#0d5132' },
  { name: 'Critical', value: 11, color: '#93a096' },
]

function cn(...classes) {
  return classes.filter(Boolean).join(' ')
}

function Button({ children, variant = 'default', className = '', ...props }) {
  return (
    <button className={cn('btn', variant === 'outline' && 'btn-outline', className)} {...props}>
      {children}
    </button>
  )
}

function Card({ children, className = '' }) {
  return <section className={cn('card', className)}>{children}</section>
}

function SidebarItem({ icon: Icon, label, active, badge, onClick }) {
  return (
    <button className={cn('nav-item', active && 'active')} onClick={onClick}>
      <Icon size={20} />
      <span>{label}</span>
      {badge && <small>{badge}</small>}
    </button>
  )
}

function KpiCard({ item }) {
  return (
    <Card className={cn('kpi-card', item.accent && 'kpi-accent')}>
      <div className="kpi-header">
        <p>{item.label}</p>
        <span>
          <ArrowUpRight size={18} />
        </span>
      </div>
      <strong>{item.value}</strong>
      <small>{item.note}</small>
    </Card>
  )
}

function App() {
  const [activeView, setActiveView] = useState('Dashboard')
  const [dashboard, setDashboard] = useState(fallbackDashboard)
  const [isUploading, setIsUploading] = useState(false)
  const [uploadError, setUploadError] = useState('')
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'Upload a C-MAPSS folder, then ask questions like “which engines are critical?” or “show sensor_2 trend”.',
    },
  ])
  const [question, setQuestion] = useState('')
  const fileInputRef = useRef(null)

  const stablePercent = useMemo(() => {
    const healthy = Number(dashboard.kpis?.[1]?.value ?? 0)
    const total = Number(dashboard.kpis?.[0]?.value ?? 1)
    return Math.round((healthy / Math.max(total, 1)) * 100)
  }, [dashboard])

  async function uploadFiles(files) {
    const selected = Array.from(files || []).filter((file) => /\.(csv|txt|tsv)$/i.test(file.name))
    if (!selected.length) {
      setUploadError('Choose a folder containing CSV, TXT, or TSV files.')
      return
    }

    const form = new FormData()
    selected.forEach((file) => form.append('files', file, file.webkitRelativePath || file.name))

    setIsUploading(true)
    setUploadError('')
    try {
      const response = await fetch(`${API_BASE}/upload`, { method: 'POST', body: form })
      if (!response.ok) throw new Error(await response.text())
      const payload = await response.json()
      setDashboard(payload)
      setMessages([
        {
          role: 'assistant',
          content: `Loaded ${payload.files.length} files with ${payload.summary.rows.toLocaleString()} rows. Ask me anything about the uploaded engine data.`,
        },
      ])
    } catch (error) {
      setUploadError('Backend upload failed. Start FastAPI on port 8001, then try again.')
    } finally {
      setIsUploading(false)
    }
  }

  async function askQuestion(event) {
    event.preventDefault()
    const text = question.trim()
    if (!text) return

    const nextMessages = [...messages, { role: 'user', content: text }]
    setMessages(nextMessages)
    setQuestion('')

    try {
      const response = await fetch(`${API_BASE}/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: text,
          history: nextMessages.map((m) => `${m.role}: ${m.content}`).join('\n'),
        }),
      })
      if (!response.ok) throw new Error(await response.text())
      const payload = await response.json()
      setMessages((current) => [
        ...current,
        {
          role: 'assistant',
          content: payload.answer.insight || 'I analyzed the uploaded dataset.',
          sql: payload.answer.sql,
          rows: payload.rows,
        },
      ])
    } catch {
      setMessages((current) => [
        ...current,
        { role: 'assistant', content: 'I could not reach the Python backend. Make sure FastAPI is running on port 8001.' },
      ])
    }
  }

  const maintenanceItems = dashboard.stages.map((stage) => ({
    title: `${stage.stage} engines`,
    date: `${stage.count} engines in latest cycle`,
    tone: stage.stage === 'Critical' ? 'critical' : stage.stage === 'Healthy' ? 'healthy' : 'warning',
    icon: stage.stage === 'Critical' ? AlertTriangle : stage.stage === 'Healthy' ? ShieldCheck : Gauge,
  }))

  return (
    <main className="page">
      <div className="app-shell">
        <aside className="sidebar">
          <div className="brand">
            <div className="brand-mark">
              <Plane size={24} />
            </div>
            <div>
              <h1>Jive Analytics</h1>
              <p>Jairamm Reddi workspace</p>
            </div>
          </div>

          <nav>
            <p className="nav-label">Menu</p>
            {[
              [Home, 'Dashboard'],
              [Activity, 'Engine Health'],
              [BarChart3, 'Analytics'],
              [MessageSquareText, 'Talk to Data'],
            ].map(([Icon, label]) => (
              <SidebarItem
                key={label}
                icon={Icon}
                label={label}
                active={activeView === label}
                badge={label === 'Talk to Data' ? 'AI' : null}
                onClick={() => setActiveView(label)}
              />
            ))}
          </nav>

          <nav>
            <p className="nav-label">General</p>
            <SidebarItem icon={Settings} label="Settings" />
            <SidebarItem icon={HelpCircle} label="Help" />
          </nav>

          <div className="download-card">
            <Bot size={20} />
            <h2>AI Data Assistant</h2>
            <p>Upload a folder of engine files and ask Gemini for SQL-backed answers.</p>
            <Button className="download-btn" onClick={() => setActiveView('Talk to Data')}>
              Open Assistant
            </Button>
          </div>
        </aside>

        <section className="workspace">
          <header className="topbar">
            <div className="search">
              <Search size={20} />
              <span>Search engine, sensor, or anomaly</span>
              <kbd>Ctrl F</kbd>
            </div>
            <div className="top-actions">
              <button aria-label="Mail">
                <Mail size={20} />
              </button>
              <button aria-label="Notifications">
                <Bell size={20} />
              </button>
              <div className="profile">
                <div className="avatar">JR</div>
                <div>
                  <strong>Jairamm Reddi</strong>
                  <span>Aircraft BI Lead</span>
                </div>
              </div>
            </div>
          </header>

          <div className="dashboard-head">
            <div>
              <h2>{activeView === 'Talk to Data' ? 'Talk to Data' : 'Aircraft Engine Dashboard'}</h2>
              <p>
                {dashboard.files.length
                  ? `${dashboard.files.length} files loaded. ${dashboard.summary.rows.toLocaleString()} rows ready for analysis.`
                  : 'Upload a C-MAPSS folder to generate the dashboard from Python.'}
              </p>
            </div>
            <div className="head-actions">
              <input
                ref={fileInputRef}
                className="hidden-input"
                type="file"
                multiple
                webkitdirectory=""
                directory=""
                onChange={(event) => uploadFiles(event.target.files)}
              />
              <Button onClick={() => fileInputRef.current?.click()} disabled={isUploading}>
                <UploadCloud size={18} />
                {isUploading ? 'Uploading...' : 'Upload Folder'}
              </Button>
              <Button variant="outline" onClick={() => setActiveView('Talk to Data')}>
                <FileUp size={18} />
                Ask Data
              </Button>
            </div>
          </div>

          {uploadError && <div className="error-banner">{uploadError}</div>}

          {activeView === 'Talk to Data' ? (
            <Card className="chat-card">
              <div className="card-title">
                <h3>AI Assistant</h3>
                <Bot size={20} />
              </div>
              <div className="chat-log">
                {messages.map((message, index) => (
                  <div className={cn('message', message.role)} key={`${message.role}-${index}`}>
                    <p>{message.content}</p>
                    {message.sql && message.sql !== 'ERROR' && <code>{message.sql}</code>}
                    {message.rows?.length ? <small>{message.rows.length} preview rows returned</small> : null}
                  </div>
                ))}
              </div>
              <form className="chat-form" onSubmit={askQuestion}>
                <input
                  value={question}
                  onChange={(event) => setQuestion(event.target.value)}
                  placeholder="Ask: show critical engines, summarize sensor_2, compare health stages..."
                />
                <Button>
                  <Send size={18} />
                  Send
                </Button>
              </form>
            </Card>
          ) : (
            <>
              <section className="kpi-grid">
                {dashboard.kpis.map((item) => (
                  <KpiCard item={item} key={item.label} />
                ))}
              </section>

              <section className="content-grid">
                <Card className="analytics-card">
                  <div className="card-title">
                    <h3>Sensor Trend Analytics</h3>
                    <SlidersHorizontal size={20} />
                  </div>
                  <ResponsiveContainer width="100%" height={260}>
                    <AreaChart data={dashboard.trend}>
                      <defs>
                        <linearGradient id="tempFill" x1="0" x2="0" y1="0" y2="1">
                          <stop offset="5%" stopColor="#16824b" stopOpacity={0.35} />
                          <stop offset="95%" stopColor="#16824b" stopOpacity={0.03} />
                        </linearGradient>
                      </defs>
                      <CartesianGrid stroke="#e5e8e1" vertical={false} />
                      <XAxis dataKey="cycle" axisLine={false} tickLine={false} />
                      <YAxis axisLine={false} tickLine={false} />
                      <Tooltip contentStyle={{ borderRadius: 14, border: '0', boxShadow: '0 12px 30px #0001' }} />
                      <Area dataKey="value" name="Sensor Index" stroke="#16824b" fill="url(#tempFill)" strokeWidth={3} />
                    </AreaChart>
                  </ResponsiveContainer>
                </Card>

                <Card className="reminder-card">
                  <h3>Maintenance Focus</h3>
                  <h4>{dashboard.kpis[3]?.value || 0} critical alerts</h4>
                  <p>Generated from the uploaded folder using Python telemetry profiling.</p>
                  <Button onClick={() => setActiveView('Talk to Data')}>
                    <Timer size={18} />
                    Ask Why
                  </Button>
                </Card>

                <Card className="project-card">
                  <div className="card-title">
                    <h3>Health Stages</h3>
                    <Button variant="outline" className="tiny-btn">
                      Live
                    </Button>
                  </div>
                  <div className="maintenance-list">
                    {maintenanceItems.map((item) => {
                      const Icon = item.icon
                      return (
                        <div className="maintenance-item" key={item.title}>
                          <span className={cn('item-icon', item.tone)}>
                            <Icon size={18} />
                          </span>
                          <div>
                            <strong>{item.title}</strong>
                            <p>{item.date}</p>
                          </div>
                        </div>
                      )
                    })}
                  </div>
                </Card>

                <Card className="bar-card">
                  <h3>Lifecycle Distribution</h3>
                  <ResponsiveContainer width="100%" height={230}>
                    <BarChart data={dashboard.stages}>
                      <CartesianGrid stroke="#e5e8e1" vertical={false} />
                      <XAxis dataKey="stage" axisLine={false} tickLine={false} />
                      <YAxis axisLine={false} tickLine={false} />
                      <Tooltip cursor={{ fill: '#edf4ee' }} contentStyle={{ borderRadius: 14, border: '0' }} />
                      <Bar dataKey="count" radius={[18, 18, 18, 18]}>
                        {dashboard.stages.map((entry, index) => (
                          <Cell key={entry.stage} fill={index === 0 ? '#16824b' : index === 3 ? '#0d5132' : '#8fc8a7'} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </Card>

                <Card className="collab-card">
                  <div className="card-title">
                    <h3>Sensor Summary</h3>
                    <Button variant="outline" className="tiny-btn">
                      Python
                    </Button>
                  </div>
                  <div className="queue-list">
                    {dashboard.sensorSummary.map((row) => (
                      <div className="queue-row" key={row.name}>
                        <div className="mini-avatar">{row.name.replace('sensor_', 'S')}</div>
                        <div>
                          <strong>{row.name}</strong>
                          <p>Mean {row.mean} · Max {row.max}</p>
                        </div>
                        <span className="status healthy">Ready</span>
                      </div>
                    ))}
                  </div>
                </Card>

                <Card className="progress-card">
                  <h3>Fleet Health Progress</h3>
                  <ResponsiveContainer width="100%" height={220}>
                    <PieChart>
                      <Pie data={sensorMix} dataKey="value" innerRadius={68} outerRadius={96} startAngle={210} endAngle={-30} paddingAngle={5}>
                        {sensorMix.map((entry) => (
                          <Cell key={entry.name} fill={entry.color} />
                        ))}
                      </Pie>
                    </PieChart>
                  </ResponsiveContainer>
                  <div className="progress-center">
                    <strong>{stablePercent}%</strong>
                    <span>Stable fleet</span>
                  </div>
                  <div className="legend">
                    {sensorMix.map((item) => (
                      <span key={item.name}>
                        <i style={{ background: item.color }} />
                        {item.name}
                      </span>
                    ))}
                  </div>
                </Card>

                <Card className="time-card">
                  <h3>Data Pipeline</h3>
                  <strong>{dashboard.files.length ? 'Live' : 'Demo'}</strong>
                  <p>{dashboard.files.length ? 'Folder dataset connected' : 'Waiting for folder upload'}</p>
                  <div className="pipeline-actions">
                    <Database size={22} />
                    <Calendar size={22} />
                  </div>
                </Card>
              </section>
            </>
          )}
        </section>
      </div>
    </main>
  )
}

export default App
