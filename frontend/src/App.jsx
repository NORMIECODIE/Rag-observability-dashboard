import { useCallback, useEffect, useId, useMemo, useState } from 'react'
import './App.css'
import { ENDPOINTS, avg, days, defaultBase, demo, dm, getEvaluation, getLatency, getOverview, getTraces, hm, ms, pct, request } from './api.js'

/* ================= Charts (inline SVG, no chart library) ================= */

// smooth Catmull-Rom style path through points
export function curve(p) {
  if (p.length < 2) return ''
  let d = `M${p[0]}`
  for (let i = 0; i < p.length - 1; i++) {
    const a = p[i - 1] || p[i], b = p[i], c = p[i + 1], e = p[i + 2] || c
    d += `C${b[0] + (c[0] - a[0]) / 6},${b[1] + (c[1] - a[1]) / 6} ${c[0] - (e[0] - b[0]) / 6},${c[1] - (e[1] - b[1]) / 6} ${c}`
  }
  return d
}

export function Area({ vals, labels = [], color = 'violet', hi = false, unit = '' }) {
  const id = 'g' + useId().replace(/[^a-zA-Z0-9]/g, '')
  const W = 520, H = 190, p = 26
  const max = Math.max(1e-9, ...vals) * 1.15
  const x = i => p + (i * (W - p * 2)) / Math.max(1, vals.length - 1)
  const y = v => H - p - (v / max) * (H - p * 2)
  const pts = vals.map((v, i) => [x(i), y(v)])
  const line = curve(pts)
  const mi = vals.indexOf(Math.max(...vals))
  const step = Math.ceil(labels.length / 6)
  return (
    <svg className="chart" viewBox={`0 0 ${W} ${H}`}>
      <defs>
        <linearGradient id={id} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" style={{ stopColor: `var(--${color})`, stopOpacity: 0.4 }} />
          <stop offset="1" style={{ stopColor: `var(--${color})`, stopOpacity: 0 }} />
        </linearGradient>
      </defs>
      {[0, 0.5, 1].map(t => <line key={t} x1={p} x2={W - p} y1={H - p - t * (H - p * 2)} y2={H - p - t * (H - p * 2)} stroke="var(--line)" />)}
      <path d={`${line}L${x(vals.length - 1)},${H - p}L${p},${H - p}Z`} fill={`url(#${id})`} />
      <path d={line} fill="none" stroke={`var(--${color})`} strokeWidth="2.6" strokeLinecap="round" />
      {hi ? (
        <>
          <circle cx={pts[mi][0]} cy={pts[mi][1]} r="5" fill="var(--coral)" stroke="#fff" strokeWidth="2" />
          <text x={pts[mi][0]} y={pts[mi][1] - 11} textAnchor="middle" style={{ fill: 'var(--coral)', fontWeight: 700 }}>{vals[mi].toFixed(1)}{unit}</text>
        </>
      ) : pts.map((q, i) => (
        <circle key={i} cx={q[0]} cy={q[1]} r="3.4" fill={`var(--${color})`}><title>{`${labels[i] || ''}: ${vals[i]}`}</title></circle>
      ))}
      {labels.map((l, i) => (labels.length > 8 && i % step && i !== labels.length - 1) ? null :
        <text key={i} x={x(i)} y={H - 6} textAnchor="middle">{l}</text>)}
    </svg>
  )
}

export function Spark({ vals, color }) {
  if (vals.length < 2) vals = [0, 0]
  const W = 200, H = 38, max = Math.max(1e-9, ...vals)
  const pts = vals.map((v, i) => [(i * W) / (vals.length - 1), H - 3 - (v / max) * (H - 8)])
  return (
    <svg viewBox={`0 0 ${W} ${H}`} width="100%" height="38" preserveAspectRatio="none">
      <path d={curve(pts)} fill="none" stroke={`var(--${color})`} strokeWidth="2.4" strokeLinecap="round" vectorEffect="non-scaling-stroke" />
    </svg>
  )
}

export function Ring({ v, color, r = 34, w = 9 }) {
  const C = 2 * Math.PI * r
  return (
    <>
      <circle cx="50" cy="50" r={r} fill="none" stroke="var(--line)" strokeWidth={w} />
      <circle cx="50" cy="50" r={r} fill="none" stroke={`var(--${color})`} strokeWidth={w} strokeLinecap="round"
        strokeDasharray={`${(v || 0) * C} ${C}`} transform="rotate(-90 50 50)" />
    </>
  )
}

/* ================= Dashboard ================= */
const NAV = [['overview', 'Overview'], ['traces', 'Traces'], ['evaluations', 'Evaluations'], ['vector', 'Vector Store'],
  ['api', 'API Testing'], ['analytics', 'Analytics'], ['settings', 'Settings']]
const TABS = ['Overview', 'Retrieval', 'LLM Response', 'Evaluation']
const REFRESH_MS = 5000

export default function App() {
  const [base, setBase] = useState(defaultBase)
  const [data, setData] = useState(null)
  const [offline, setOffline] = useState(false)
  const [sel, setSel] = useState(null)
  const [tab, setTab] = useState('Overview')
  const [filter, setFilter] = useState('all')
  const [q, setQ] = useState('')
  const [view, setView] = useState('overview')
  const [last, setLast] = useState(Date.now())
  const [, tick] = useState(0)

  const load = useCallback(async () => {
    try {
      const [overview, latency, evaluation, traces] = await Promise.all([getOverview(base), getLatency(base), getEvaluation(base), getTraces(base, 50, 0)])
      setData({ overview, latency, evaluation, traces: traces.traces || [] })
      setOffline(false)
    } catch {
      setData(d => d || (() => { const x = demo(); return { ...x, traces: x.traces } })())
      setOffline(true)
    }
    setLast(Date.now())
  }, [base])

  useEffect(() => { load(); const t = setInterval(load, REFRESH_MS); return () => clearInterval(t) }, [load])
  useEffect(() => { const t = setInterval(() => tick(n => n + 1), 1000); return () => clearInterval(t) }, [])
  useEffect(() => { if (!sel && data?.traces.length) setSel(data.traces[0]) }, [data, sel])

  const go = id => {
    setView(['traces', 'evaluations'].includes(id) ? 'overview' : id)
    if (['traces', 'evaluations'].includes(id)) setTimeout(() => document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' }), 30)
  }
  const toggleTheme = () => {
    const d = document.documentElement
    const cur = d.dataset.theme || (matchMedia('(prefers-color-scheme:dark)').matches ? 'dark' : 'light')
    d.dataset.theme = cur === 'dark' ? 'light' : 'dark'
  }

  if (!data) return <div className="app"><p className="empty">Loading dashboard…</p></div>
  const ago = Math.max(0, Math.round((Date.now() - last) / 1000))

  return (
    <div className="app">
      <aside className="glass">
        <div className="brand"><div className="logo">◎</div><div><b>RAG Observability</b><small>Monitor, evaluate, improve</small></div></div>
        <nav>{NAV.map(([id, n]) => <button key={id} className={view === id ? 'on' : ''} onClick={() => go(id)}>{n}</button>)}</nav>
        <div className="sys">
          <h4>System status</h4>
          <p><span>Backend</span><b className={offline ? 'warn' : 'good'}>{offline ? 'Demo' : 'Connected'}</b></p>
          <p><span>Frontend</span><b className="good">Online</b></p>
          <p><span>MongoDB</span><b className="warn">Not checked</b></p>
          <p><span>Qdrant</span><b className="warn">Not checked</b></p>
          <small>Last check: {ago}s ago</small>
        </div>
      </aside>

      <main>
        <div className="top">
          <input placeholder="Search traces or questions…" aria-label="Search traces" value={q} onChange={e => setQ(e.target.value.toLowerCase())} />
          <div className="chip"><i className={`dot ${offline ? 'off' : ''}`} />{offline ? 'Demo data' : 'Live monitoring'}</div>
          <button className="tg" aria-label="Toggle light and dark theme" onClick={toggleTheme}>◐</button>
        </div>
        {offline && <div className="banner">Can’t reach the API at <code>{base}</code>, so you’re seeing demo data. Start FastAPI on port 8000, or change the URL in Settings.</div>}
        <div><h1>Welcome <em>Arun</em></h1><p className="sub">Monitor your RAG pipeline, analyze performance, and improve your AI system.</p></div>

        <div className="app-root-col">
          {view === 'overview' && <Overview {...{ data, sel, setSel, tab, setTab, filter, setFilter, q }} />}
          {view === 'api' && <ApiView base={base} data={data} />}
          {view === 'settings' && <Settings base={base} onSave={b => { try { localStorage.setItem('rag_base', b) } catch {} setBase(b) }} />}
          {['vector', 'analytics'].includes(view) && (
            <div className="card glass"><div className="ch"><h3>{NAV.find(n => n[0] === view)[1]}</h3></div>
              <p className="empty">This page isn’t connected to a backend endpoint yet. The metrics and trace endpoints power Overview, Traces and Evaluations.</p></div>
          )}
        </div>
      </main>
    </div>
  )
}

function Overview({ data, sel, setSel, tab, setTab, filter, setFilter, q }) {
  const { overview: o, latency: l, evaluation: e, traces } = data
  const sr = o.total_requests ? o.successful_requests / o.total_requests : null
  const a = avg(e.average_scores)
  const dd = useMemo(() => days(traces), [traces])
  const recent = traces.slice(0, 30).reverse()
  const st = l.stages || {}
  const sc = e.average_scores || {}
  const visible = traces.filter(t => (filter === 'all' || t.status === filter) && (!q || t.question.toLowerCase().includes(q) || t.trace_id.startsWith(q)))

  return (
    <>
      <div className="kpis">
        <Kpi c="violet" title="Total traces" v={o.total_requests} sub={`${o.successful_requests} successful · ${o.failed_requests} failed`}><Spark vals={dd.c} color="violet" /></Kpi>
        <Kpi c="coral" title="Avg. latency" v={ms(o.average_latency_ms)} sub={`min ${ms(l.end_to_end?.minimum_ms)} · max ${ms(l.end_to_end?.maximum_ms)}`}>
          <Spark vals={traces.slice(0, 20).reverse().map(x => x.total_latency_ms)} color="coral" /></Kpi>
        <Kpi c="teal" title="Success rate" v={pct(sr)} sub={`${o.failed_requests} failed requests`}>
          <svg viewBox="0 0 100 100" height="38" style={{ overflow: 'visible' }}><Ring v={sr} color="teal" r={40} w={12} /></svg></Kpi>
        <Kpi c="amber" title="Avg. evaluation score" v={a == null ? 'N/A' : a.toFixed(2)} sub={e.scored_queries ? `${e.scored_queries} scored queries` : 'No scores recorded'}>
          <Spark vals={Object.values(sc).filter(v => v != null)} color="amber" /></Kpi>
      </div>

      <div className="g3">
        <div className="card glass"><div className="ch"><h3>Request volume</h3><span className="s" /><span className="note">Last 7 days</span></div>
          <Area vals={dd.c} labels={dd.k} color="violet" /></div>
        <div className="card glass"><div className="ch"><h3>Latency (seconds)</h3><span className="s" /><span className="note">Recent traces</span></div>
          {recent.length ? <Area vals={recent.map(x => +(x.total_latency_ms / 1000).toFixed(2))} labels={recent.map(x => dm(x.created_at))} color="coral" hi unit="s" /> : <p className="empty">No traces yet.</p>}
          <div className="chips">{['embedding', 'retrieval', 'generation'].map(k => <span key={k} style={{ textTransform: 'capitalize' }}>{k}<b>{ms(st[k]?.average_ms)}</b></span>)}</div></div>
        <div className="card glass" id="evaluations"><div className="ch"><h3>Evaluation score</h3><span className="s" /><span className="note">{e.scored_queries}/{e.dataset_size} scored</span></div>
          <div className="rings">{[['faithfulness', 'violet'], ['relevance', 'teal'], ['completeness', 'coral']].map(([k, c]) => (
            <div key={k}><svg viewBox="0 0 100 100"><Ring v={sc[k]} color={c} /><text className="rv" x="50" y="56" textAnchor="middle">{sc[k] == null ? 'N/A' : sc[k].toFixed(2)}</text></svg><div className="rl">{k}</div></div>))}</div>
          <p className="mut sm">RAG {e.average_latency_seconds?.rag ?? '–'}s · Judge {e.average_latency_seconds?.judge ?? '–'}s · {e.total_cost_usd == null ? 'Cost unavailable' : `Cost $${e.total_cost_usd.toFixed(4)}`}</p>
          {e.total_cost_usd == null && e.cost_status && <p className="mut sm" style={{ marginTop: 4 }}>{e.cost_status}</p>}</div>
      </div>

      <div className="g2" id="traces">
        <div className="card glass">
          <div className="ch"><h3>Recent traces</h3><span className="n">{visible.length}</span><span className="s" />
            <select value={filter} onChange={ev => setFilter(ev.target.value)} aria-label="Status filter">
              <option value="all">All statuses</option><option value="success">Success</option><option value="failure">Failure</option><option value="pending">Pending</option>
            </select></div>
          {visible.length === 0 ? <p className="empty">No traces match. Clear the search or change the status filter.</p> : (
            <ul className="tl">{visible.map(t => (
              <li key={t.trace_id}><button className={sel?.trace_id === t.trace_id ? 'sel' : ''} onClick={() => { setSel(t); setTab('Overview') }}>
                <span className="id mono">{t.trace_id.slice(0, 7)}</span><span className="q">{t.question}</span>
                <span className="ms">{ms(t.total_latency_ms)}</span><span className={`pill ${t.status}`}>{t.status}</span><span className="tm">{hm(t.created_at)}</span>
              </button></li>))}</ul>)}
        </div>
        <div className="card glass">
          <div className="ch"><h3>Trace details</h3><span className="s" /><span className="n">Inspector</span></div>
          <Detail t={sel} tab={tab} setTab={setTab} l={l} e={e} />
        </div>
      </div>
    </>
  )
}

function Kpi({ c, title, v, sub, children }) {
  return <div className="kpi glass" style={{ '--c': `var(--${c})` }}><h3>{title}</h3><div className="big">{v}</div><small>{sub}</small><div className="sp">{children}</div></div>
}

function Detail({ t, tab, setTab, l, e }) {
  if (!t) return <p className="empty">Select a trace to inspect it.</p>
  const note = <p className="mut sm">Pipeline averages: /traces doesn’t return per-trace stage data yet.</p>
  return (
    <>
      <div className="tabs">{TABS.map(x => <button key={x} className={x === tab ? 'on' : ''} onClick={() => setTab(x)}>{x}</button>)}</div>
      {tab === 'Overview' && (
        <dl>
          <dt>Trace ID</dt><dd className="mono">{t.trace_id}</dd>
          <dt>Question</dt><dd className="box">{t.question}</dd>
          <dt>Status</dt><dd><span className={`pill ${t.status}`} style={{ display: 'inline-block' }}>{t.status}</span></dd>
          <dt>Latency</dt><dd>{ms(t.total_latency_ms)}</dd>
          <dt>Created</dt><dd>{new Date(t.created_at).toLocaleString('en-GB')}</dd>
          {t.estimated_cost_usd != null && <><dt>Est. cost</dt><dd>${t.estimated_cost_usd.toFixed(5)}</dd></>}
          <dt>Logs</dt><dd><pre>{JSON.stringify(t, null, 2)}</pre></dd>
        </dl>)}
      {tab === 'Retrieval' && <><dl><dt>Embedding</dt><dd>{ms(l.stages?.embedding?.average_ms)} avg</dd><dt>Retrieval</dt><dd>{ms(l.stages?.retrieval?.average_ms)} avg</dd></dl>{note}</>}
      {tab === 'LLM Response' && <><dl><dt>Generation</dt><dd>{ms(l.stages?.generation?.average_ms)} avg</dd><dt>RAG latency</dt><dd>{e.average_latency_seconds?.rag ?? '–'}s avg</dd></dl>{note}</>}
      {tab === 'Evaluation' && (
        <>{['faithfulness', 'relevance', 'completeness'].map(k => { const v = e.average_scores?.[k]; return (
          <div className="meter" key={k}><span>{k}</span><div className="trk"><i style={{ width: `${(v || 0) * 100}%` }} /></div><b>{v == null ? 'N/A' : v.toFixed(2)}</b></div>) })}
          <p className="mut sm">Judge latency {e.average_latency_seconds?.judge ?? '–'}s avg · dataset averages.</p></>)}
    </>
  )
}

function ApiView({ base, data }) {
  const [path, setPath] = useState(ENDPOINTS[0])
  const [out, setOut] = useState('')
  const [src, setSrc] = useState('')
  const send = async () => {
    try { setOut(JSON.stringify(await request(base, path), null, 2)); setSrc(`Live response from ${base}`) }
    catch {
      const k = path.startsWith('/traces') ? { traces: data.traces.slice(0, 10) } : data[path.split('/').pop() === 'overview' ? 'overview' : path.split('/').pop()]
      setOut(JSON.stringify(k, null, 2)); setSrc('Demo response (backend unreachable)')
    }
  }
  return (
    <div className="card glass"><div className="ch"><h3>API testing</h3></div>
      <div className="row"><select value={path} onChange={e => setPath(e.target.value)}>{ENDPOINTS.map(p => <option key={p}>{p}</option>)}</select>
        <button className="btn" onClick={send}>Send request</button><span className="mut sm" style={{ margin: 0 }}>{src}</span></div>
      <pre>{out || 'Choose an endpoint and send a request.'}</pre></div>
  )
}

function Settings({ base, onSave }) {
  const [v, setV] = useState(base)
  return (
    <div className="card glass"><div className="ch"><h3>Settings</h3></div>
      <p className="mut sm" style={{ margin: '0 0 12px' }}>API base URL. Default <code>/api</code> uses the Vite dev proxy to FastAPI on port 8000. A full URL needs CORS enabled on the backend. Data refreshes every {REFRESH_MS / 1000} seconds.</p>
      <div className="row"><input className="inp" value={v} onChange={e => setV(e.target.value)} aria-label="API base URL" />
        <button className="btn" onClick={() => onSave(v.trim().replace(/\/$/, ''))}>Save and reconnect</button></div></div>
  )
}
