
import "./App.css";
import { useEffect, useMemo, useState } from "react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  LineChart,
  Line,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from "recharts";

const API_URL = "/observability";

const navItems = [
  ["⌂", "Overview"],
  ["⌁", "Traces"],
  ["♧", "Evaluations"],
  ["▤", "Documents"],
  ["⬡", "Vector Store"],
  ["⚒", "API Testing"],
  ["▥", "Analytics"],
  ["⚙", "Settings"],
];

const formatMs = (value) =>
  `${Number(value || 0).toLocaleString()} ms`;

const formatDate = (value) => {
  if (!value) return "—";
  const date = new Date(value);
  return Number.isNaN(date.getTime())
    ? String(value)
    : date.toLocaleString();
};

const shortId = (value) => String(value || "unknown").slice(0, 8);

const traceStatus = (trace) => {
  const status = String(trace?.status || "").toLowerCase();

  if (["ok", "success", "completed"].includes(status)) {
    return "Success";
  }

  if (["error", "failed", "failure"].includes(status)) {
    return "Error";
  }

  return trace?.status || "Unknown";
};

function App() {
  const [traces, setTraces] = useState([]);
  const [historicalMetrics, setHistoricalMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [selectedTraceId, setSelectedTraceId] = useState(null);
  const [activeNav, setActiveNav] = useState("Overview");
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("All statuses");
  const [range, setRange] = useState("Last 7 days");
  const [activePage, setActivePage] = useState("Traces");

  // Load live data from the existing FastAPI endpoints.
  useEffect(() => {
    let isMounted = true;

    const fetchDashboardData = async () => {
      try {
        const [tracesResponse, metricsResponse] =
          await Promise.all([
            fetch(`${API_URL}/traces`),
            fetch(`${API_URL}/metrics/summary`),
          ]);

        if (!tracesResponse.ok || !metricsResponse.ok) {
          throw new Error(
            "The observability API returned an error."
          );
        }

        const [tracesData, metricsData] = await Promise.all([
          tracesResponse.json(),
          metricsResponse.json(),
        ]);

        if (isMounted) {
          const nextTraces = tracesData.traces ?? [];

          setTraces(nextTraces);
          setHistoricalMetrics(metricsData);

          setSelectedTraceId((current) =>
            current &&
            nextTraces.some((item) => item.trace_id === current)
              ? current
              : nextTraces[0]?.trace_id ?? null
          );

          setError("");
          setLoading(false);
        }
      } catch (err) {
        if (isMounted) {
          setError(
            err.message || "Unable to connect to the backend."
          );
          setLoading(false);
        }
      }
    };

    fetchDashboardData();

    const intervalId = setInterval(fetchDashboardData, 5000);

    return () => {
      isMounted = false;
      clearInterval(intervalId);
    };
  }, []);

  const historical = historicalMetrics ?? {};

  const successfulTraces = traces.filter(
    (trace) => traceStatus(trace) === "Success"
  ).length;

  const successRate = traces.length
    ? (successfulTraces / traces.length) * 100
    : 0;

  const averageDuration = traces.length
    ? traces.reduce(
        (sum, trace) => sum + (trace.total_duration_ms || 0),
        0
      ) / traces.length
    : 0;

  const evaluationValues = traces
    .map((trace) =>
      Number(
        trace.evaluation_score ??
        trace.evaluation?.score ??
        trace.score
      )
    )
    .filter(Number.isFinite);

  const averageScore = evaluationValues.length
    ? evaluationValues.reduce((sum, score) => sum + score, 0) /
      evaluationValues.length
    : null;

  // Search and filter trace rows.
  const filteredTraces = useMemo(
    () =>
      traces.filter((trace) => {
        const searchableText =
          `${trace.query || ""} ${trace.trace_id || ""}`.toLowerCase();

        const matchesSearch = searchableText.includes(
          search.toLowerCase()
        );

        const matchesStatus =
          statusFilter === "All statuses" ||
          traceStatus(trace) === statusFilter;

        return matchesSearch && matchesStatus;
      }),
    [traces, search, statusFilter]
  );

  const selectedTrace =
    traces.find(
      (trace) => trace.trace_id === selectedTraceId
    ) ??
    filteredTraces[0] ??
    traces[0] ??
    null;

  // Chart data is derived from real traces.
  const chartData = useMemo(
    () =>
      [...traces].reverse().map((trace, index) => ({
        label: trace.created_at
          ? new Date(trace.created_at).toLocaleDateString(
              undefined,
              { month: "short", day: "numeric" }
            )
          : `Trace ${index + 1}`,
        requests: 1,
        latency: Number(trace.total_duration_ms || 0) / 1000,
        score: Number(
          trace.evaluation_score ??
          trace.evaluation?.score ??
          trace.score ??
          0
        ),
      })),
    [traces]
  );

  const usage = selectedTrace?.usage ?? {};
  const selectedSpans = selectedTrace?.spans ?? [];

  const maxDuration = Math.max(
    ...selectedSpans.map((span) =>
      Number(span.duration_ms || 0)
    ),
    1
  );

  return (
    <div className="app-shell">
      {/* LEFT NAVIGATION */}
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">⬡</div>
          <div>
            <strong>RAG OBSERVABILITY</strong>
            <span>Monitor · Evaluate · Improve</span>
          </div>
        </div>

        <nav className="main-nav" aria-label="Main navigation">
          {navItems.map(([icon, label]) => (
            <button
              className={`nav-item ${
                activeNav === label ? "active" : ""
              }`}
              key={label}
              onClick={() => {
               setActiveNav(label);
                setActivePage(label);
              }}  
              type="button"
            >
              <span className="nav-icon">{icon}</span>
              <span>{label}</span>
            </button>
          ))}
        </nav>

        {/* SYSTEM STATUS */}
        <section className="system-card">
          <div className="system-heading">
            <span
              className={`pulse-dot ${error ? "offline" : ""}`}
            />
            System Status
          </div>

          <div className="system-row">
            <span>▤ Backend</span>
            <strong className={error ? "status-down" : "status-up"}>
              {error ? "Offline" : "Connected"}
            </strong>
          </div>

          <div className="system-row">
            <span>▱ Frontend</span>
            <strong className="status-up">Online</strong>
          </div>

          <div className="system-row">
            <span>◉ MongoDB</span>
            <strong className="status-neutral">Not checked</strong>
          </div>

          <div className="system-row">
            <span>⬡ Qdrant</span>
            <strong className="status-neutral">Not checked</strong>
          </div>

          <p className="system-note">
            MongoDB and Qdrant require dedicated health checks.
          </p>
        </section>

        <div className="sidebar-footer">
          <span className="live-dot" />
          Live refresh · 5 sec
        </div>
      </aside>

      {/* MAIN DASHBOARD */}
      <main className="main-content">
        <header className="topbar">
          <label className="global-search">
            <span>⌕</span>
            <input
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="Search traces or questions..."
            />
            <kbd>⌘ K</kbd>
          </label>

          <div className="topbar-actions">
            <select
              aria-label="Date range"
              value={range}
              onChange={(event) => setRange(event.target.value)}
            >
              <option>Last 7 days</option>
              <option>Last 24 hours</option>
              <option>Last 30 days</option>
              <option>All time</option>
            </select>

            <div className="avatar">D</div>
            <strong className="profile-name">Deepak</strong>
          </div>
        </header>

        <section className="welcome-row">
          <div>
            <p className="eyebrow">
              OVERVIEW / {activeNav.toUpperCase()}
            </p>

            <h1>
              Welcome back, <span>Deepak</span>
            </h1>

            <p className="welcome-subtitle">
              Monitor your RAG pipeline, analyze performance,
              and improve your AI system.
            </p>
          </div>

          <div className="live-pill">
            <span className="live-dot" />
            {error ? "Connection issue" : "Live monitoring"}
          </div>
        </section>

        {error && (
          <div className="error-banner">
            <strong>Connection error:</strong> {error}
            <span> Retrying automatically every 5 seconds.</span>
          </div>
        )}
        {activePage !== "Overview" && (
  <section className="panel" style={{ padding: "24px", marginBottom: "20px" }}>
    <h2>{activePage}</h2>
    <p>Welcome to the {activePage} page.</p>
  </section>
)}

        {/* KPI CARDS */}
        <section className="kpi-grid">
          <article className="kpi-card green-card">
            <div className="kpi-icon">▤</div>
            <div className="kpi-copy">
              <span>Total Traces</span>
              <strong>
                {Number(
                  historical.total_traces ?? traces.length
                ).toLocaleString()}
              </strong>
              <small>Stored observations</small>
            </div>
          </article>

          <article className="kpi-card amber-card">
            <div className="kpi-icon">ϟ</div>
            <div className="kpi-copy">
              <span>Avg. Latency</span>
              <strong>{(averageDuration / 1000).toFixed(2)}s</strong>
              <small>Across loaded traces</small>
            </div>
          </article>

          <article className="kpi-card blue-card">
            <div className="kpi-icon">♢</div>
            <div className="kpi-copy">
              <span>Success Rate</span>
              <strong>{successRate.toFixed(1)}%</strong>
              <small>{successfulTraces} successful traces</small>
            </div>
          </article>

          <article className="kpi-card pink-card">
            <div className="kpi-icon">▥</div>
            <div className="kpi-copy">
              <span>Avg. Evaluation Score</span>
              <strong>
                {averageScore === null
                  ? "N/A"
                  : averageScore.toFixed(2)}
              </strong>
              <small>
                {evaluationValues.length
                  ? "From recorded scores"
                  : "No scores recorded"}
              </small>
            </div>
          </article>
        </section>

        {/* THREE CHARTS */}
        <section className="chart-grid">
          <article className="panel chart-panel">
            <div className="panel-heading">
              <div>
                <span className="chart-symbol green-text">▥</span>
                <h2>Request Volume</h2>
              </div>
              <span className="panel-caption">{range}</span>
            </div>

            <div className="chart-area">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData}>
                  <CartesianGrid
                    stroke="#1b3532"
                    strokeDasharray="3 3"
                    vertical={false}
                  />
                  <XAxis dataKey="label" />
                  <YAxis allowDecimals={false} />
                  <Tooltip />
                  <Bar
                    dataKey="requests"
                    name="Trace"
                    fill="#25e6ad"
                    radius={[3, 3, 0, 0]}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </article>

          <article className="panel chart-panel">
            <div className="panel-heading">
              <div>
                <span className="chart-symbol amber-text">◷</span>
                <h2>Latency (seconds)</h2>
              </div>
              <span className="panel-caption">{range}</span>
            </div>

            <div className="chart-area">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData}>
                  <CartesianGrid
                    stroke="#1b3532"
                    strokeDasharray="3 3"
                    vertical={false}
                  />
                  <XAxis dataKey="label" />
                  <YAxis />
                  <Tooltip />
                  <Line
                    type="monotone"
                    dataKey="latency"
                    name="Latency (s)"
                    stroke="#ffbd45"
                    strokeWidth={2.5}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </article>

          <article className="panel chart-panel">
            <div className="panel-heading">
              <div>
                <span className="chart-symbol pink-text">▥</span>
                <h2>Evaluation Score</h2>
              </div>
              <span className="panel-caption">{range}</span>
            </div>

            <div className="chart-area">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={chartData}>
                  <CartesianGrid
                    stroke="#1b3532"
                    strokeDasharray="3 3"
                    vertical={false}
                  />
                  <XAxis dataKey="label" />
                  <YAxis domain={[0, 1]} />
                  <Tooltip />
                  <Area
                    type="monotone"
                    dataKey="score"
                    name="Score"
                    stroke="#ff668b"
                    fill="#ff668b33"
                    strokeWidth={2.5}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </article>
        </section>

        {/* COMPACT TRACES LEFT + INSPECTOR RIGHT */}
        <section className="bottom-grid">
          <article className="panel traces-panel">
            <div className="panel-heading trace-heading">
              <div>
                <span className="chart-symbol green-text">▤</span>
                <h2>Recent Traces</h2>
                <span className="count-chip">
                  {filteredTraces.length}
                </span>
              </div>

              <div className="trace-controls">
                <select
                  aria-label="Filter trace status"
                  value={statusFilter}
                  onChange={(event) =>
                    setStatusFilter(event.target.value)
                  }
                >
                  <option>All statuses</option>
                  <option>Success</option>
                  <option>Error</option>
                </select>
              </div>
            </div>

            {loading ? (
              <div className="empty-state">Loading traces…</div>
            ) : filteredTraces.length === 0 ? (
              <div className="empty-state">
                <strong>No traces found</strong>
                <span>Try another search or run a RAG query.</span>
              </div>
            ) : (
              <div className="trace-list">
                {filteredTraces.slice(0, 30).map((trace) => {
                  const status = traceStatus(trace);
                  const isSelected =
                    selectedTrace?.trace_id === trace.trace_id;

                  const score =
                    trace.evaluation_score ??
                    trace.evaluation?.score ??
                    trace.score;

                  return (
                    <button
                      type="button"
                      className={`trace-row ${
                        isSelected ? "selected" : ""
                      }`}
                      key={trace.trace_id}
                      onClick={() =>
                        setSelectedTraceId(trace.trace_id)
                      }
                    >
                      <code className="trace-id">
                        {shortId(trace.trace_id)}
                      </code>

                      <span
                        className="trace-question"
                        title={trace.query || "Untitled query"}
                      >
                        {trace.query || "Untitled query"}
                      </span>

                      <span className="trace-latency">
                        {formatMs(trace.total_duration_ms)}
                      </span>

                      <span
                        className={`trace-status ${
                          status === "Success"
                            ? "success"
                            : status === "Error"
                              ? "failure"
                              : "unknown"
                        }`}
                      >
                        <i />
                        {status}
                      </span>

                      <span
                        className={`score-pill ${
                          score == null
                            ? "no-score"
                            : Number(score) >= 0.8
                              ? "good-score"
                              : "mid-score"
                        }`}
                      >
                        {score == null
                          ? "—"
                          : Number(score).toFixed(2)}
                      </span>

                      <span className="trace-date">
                        {trace.created_at
                          ? new Date(
                              trace.created_at
                            ).toLocaleTimeString([], {
                              hour: "2-digit",
                              minute: "2-digit",
                            })
                          : "—"}
                      </span>

                      <span className="row-arrow">›</span>
                    </button>
                  );
                })}
              </div>
            )}

            <div className="trace-footer">
              Showing {Math.min(filteredTraces.length, 30)} of{" "}
              {filteredTraces.length} matching traces
            </div>
          </article>

          {/* RIGHT-SIDE TRACE DETAILS */}
          <aside className="panel inspector-panel">
            <div className="panel-heading inspector-heading">
              <div>
                <span className="chart-symbol green-text">↗</span>
                <h2>Trace Details</h2>
              </div>
              <span className="inspector-label">Inspector</span>
            </div>

            {!selectedTrace ? (
              <div className="empty-state">
                <strong>Select a trace</strong>
                <span>Choose a row to inspect its details.</span>
              </div>
            ) : (
              <div className="inspector-content">
                <div className="inspector-tabs">
                  <span className="tab-active">Overview</span>
                  <span>Retrieval</span>
                  <span>LLM Response</span>
                  <span>Evaluation</span>
                </div>

                <div className="detail-line">
                  <span>Trace ID</span>
                  <code>{selectedTrace.trace_id || "—"}</code>
                </div>

                <div className="detail-block">
                  <span>Question</span>
                  <p>
                    {selectedTrace.query || "No query recorded."}
                  </p>
                </div>

                <div className="detail-line">
                  <span>Status</span>
                  <strong
                    className={`trace-status ${
                      traceStatus(selectedTrace) === "Success"
                        ? "success"
                        : "failure"
                    }`}
                  >
                    <i />
                    {traceStatus(selectedTrace)}
                  </strong>
                </div>

                <div className="detail-line">
                  <span>Latency</span>
                  <strong>
                    {(
                      Number(selectedTrace.total_duration_ms || 0) /
                      1000
                    ).toFixed(2)}{" "}
                    seconds
                  </strong>
                </div>

                <div className="detail-line">
                  <span>Evaluation Score</span>
                  <strong className="green-text">
                    {(
                      selectedTrace.evaluation_score ??
                      selectedTrace.evaluation?.score ??
                      selectedTrace.score
                    ) == null
                      ? "N/A"
                      : Number(
                          selectedTrace.evaluation_score ??
                          selectedTrace.evaluation?.score ??
                          selectedTrace.score
                        ).toFixed(2)}
                  </strong>
                </div>

                <div className="detail-line">
                  <span>Timestamp</span>
                  <strong>
                    {formatDate(selectedTrace.created_at)}
                  </strong>
                </div>

                {selectedTrace.model && (
                  <div className="detail-line">
                    <span>Model</span>
                    <strong>{selectedTrace.model}</strong>
                  </div>
                )}

                <div className="inspector-divider" />
                <h3>Token Usage</h3>

                <div className="token-grid">
                  <div>
                    <span>Input</span>
                    <strong>{usage.prompt_tokens ?? "N/A"}</strong>
                  </div>
                  <div>
                    <span>Output</span>
                    <strong>
                      {usage.completion_tokens ?? "N/A"}
                    </strong>
                  </div>
                  <div>
                    <span>Total</span>
                    <strong>{usage.total_tokens ?? "N/A"}</strong>
                  </div>
                </div>

                <div className="inspector-divider" />
                <h3>Pipeline Spans</h3>

                {selectedSpans.length === 0 ? (
                  <p className="muted-copy">
                    No span details available for this trace.
                  </p>
                ) : (
                  selectedSpans.map((span, index) => (
                    <div
                      className="span-item"
                      key={`${span.name}-${index}`}
                    >
                      <div className="span-title">
                        <strong>{span.name || "Pipeline stage"}</strong>
                        <span>{formatMs(span.duration_ms)}</span>
                      </div>

                      <div className="span-track">
                        <span
                          style={{
                            width: `${
                              Math.min(
                                100,
                                (Number(span.duration_ms || 0) /
                                  maxDuration) *
                                  100
                              )
                            }%`,
                          }}
                        />
                      </div>

                      {span.error && (
                        <p className="span-error">{span.error}</p>
                      )}
                    </div>
                  ))
                )}

                <div className="inspector-cost">
                  <span>Estimated cost</span>
                  <strong>
                    {typeof selectedTrace.estimated_cost_usd ===
                    "number"
                      ? `$${selectedTrace.estimated_cost_usd.toFixed(8)}`
                      : "N/A"}
                  </strong>
                </div>
              </div>
            )}
          </aside>
        </section>

        <footer className="dashboard-footer">
          RAG Observability · FastAPI · React · MongoDB · Qdrant
          <span>Auto-refresh every 5 seconds</span>
        </footer>
      </main>
    </div>
  );
}

export default App;
