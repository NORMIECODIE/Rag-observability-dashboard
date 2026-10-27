
// Base URL: Settings page > VITE_API_URL > Vite proxy (/api -> FastAPI :8000)
export const defaultBase = () => {
    try { const b = localStorage.getItem('rag_base'); if (b) return b } catch { }
    return import.meta.env.VITE_API_URL || '/api'
}

async function get(base, path) {
    const res = await fetch(`${base}${path}`)
    if (!res.ok) throw new Error(`${path} -> ${res.status}`)
    return res.json()
}

export const getOverview = base => get(base, '/metrics/overview')
export const getLatency = base => get(base, '/metrics/latency')
export const getEvaluation = base => get(base, '/metrics/evaluation')
export const getTraces = (base, limit = 50, skip = 0) => get(base, `/traces?limit=${limit}&skip=${skip}`)
export const request = get

export const ENDPOINTS = ['/metrics/overview', '/metrics/latency', '/metrics/evaluation', '/traces?limit=10&skip=0']

// Demo data: exactly the shapes in the API spec. Used only while the backend is unreachable.
export function demo() {
    const Q = ['Where is the nucleus located in an atom?', 'What did Rutherford propose about the atom?', 'What is the return policy?',
        'How does retrieval chunking work?', 'Who discovered the electron?', 'Summarise the onboarding guide', 'What is the refund window?', 'Explain vector similarity search']
    let seed = 7
    const rnd = () => (seed = (seed * 9301 + 49297) % 233280) / 233280
    const now = Date.now()
    const traces = Array.from({ length: 30 }, (_, i) => ({
        trace_id: Array.from({ length: 32 }, () => '0123456789abcdef'[Math.floor(rnd() * 16)]).join(''),
        question: Q[i % Q.length],
        status: i === 4 ? 'failure' : i === 1 ? 'pending' : 'success',
        total_latency_ms: i === 11 ? 5200 : Math.round(900 + rnd() * 1400),
        created_at: new Date(now - i * 5.2 * 3600e3).toISOString(),
    }))
    return {
        overview: { total_requests: 150, successful_requests: 142, failed_requests: 8, average_latency_ms: 342.5 },
        latency: {
            end_to_end: { count: 150, average_ms: 342.5, minimum_ms: 120, maximum_ms: 1250 },
            stages: { embedding: { average_ms: 45.2 }, retrieval: { average_ms: 110.5 }, generation: { average_ms: 186.8 } }
        },
        evaluation: {
            average_scores: { faithfulness: 0.85, relevance: 0.9, completeness: 0.78 }, scored_queries: 28, dataset_size: 40,
            queries_without_scores: 12, average_latency_seconds: { rag: 1.45, judge: 0.82 }, total_cost_usd: null,
            cost_status: 'Unavailable: verified cost data is not available for every query'
        },
        traces,
    }
}

// ---------- helpers ----------
export const ms = v => (v == null ? '–' : v >= 1000 ? (v / 1000).toFixed(2) + 's' : Math.round(v) + 'ms')
export const pct = v => (v == null ? 'N/A' : (v * 100).toFixed(1) + '%')
export const hm = i => new Date(i).toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' })
export const dm = i => new Date(i).toLocaleDateString('en-GB', { day: '2-digit', month: 'short' })
export const avg = o => {
    const v = Object.values(o || {}).filter(x => x != null)
    return v.length ? v.reduce((a, b) => a + b, 0) / v.length : null
}
// Request counts for the last 7 days, derived from trace created_at
export function days(traces) {
    const k = []
    for (let i = 6; i >= 0; i--) k.push(dm(Date.now() - i * 864e5))
    return { k, c: k.map(x => traces.filter(t => dm(t.created_at) === x).length) }
}