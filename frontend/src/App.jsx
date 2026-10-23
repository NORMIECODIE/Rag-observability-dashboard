
import "./App.css";
import { useEffect, useState } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

const API_URL = "/observability";

function App() {
  const [traces, setTraces] = useState([]);
  const [historicalMetrics, setHistoricalMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [expandedTrace, setExpandedTrace] = useState(null);

  useEffect(() => {
    let isMounted = true;

    const fetchDashboardData = async () => {
      try {
        const [tracesResponse, metricsResponse] = await Promise.all([
          fetch(`${API_URL}/traces`),
          fetch(`${API_URL}/metrics/summary`),
        ]);

        if (!tracesResponse.ok || !metricsResponse.ok) {
          throw new Error("Failed to fetch dashboard data");
        }

        const [tracesData, metricsData] = await Promise.all([
          tracesResponse.json(),
          metricsResponse.json(),
        ]);

        if (isMounted) {
          setTraces(tracesData.traces ?? []);
          setHistoricalMetrics(metricsData);
          setError("");
          setLoading(false);
        }
      } catch (err) {
        if (isMounted) {
          setError(
            err.message || "Unable to connect to the backend"
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

  // Metrics calculated from the latest traces returned by the API.
  const successfulTraces = traces.filter(
    (trace) => trace.status === "ok"
  ).length;

  const failedTraces = traces.filter(
    (trace) => trace.status === "error"
  ).length;

  const averageDuration =
    traces.length > 0
      ? (
          traces.reduce(
            (total, trace) =>
              total + (trace.total_duration_ms || 0),
            0
          ) / traces.length
        ).toFixed(1)
      : "0.0";

  const tracesWithCost = traces.filter(
    (trace) =>
      typeof trace.estimated_cost_usd === "number" &&
      Number.isFinite(trace.estimated_cost_usd)
  );

  const recentTotalCost = tracesWithCost.reduce(
    (total, trace) => total + trace.estimated_cost_usd,
    0
  );

  const recentAverageCost =
    tracesWithCost.length > 0
      ? recentTotalCost / tracesWithCost.length
      : null;

  // Average duration for each RAG stage in the loaded traces.
  const stageNames = ["embedding", "retrieval", "generation"];

  const stagePerformance = stageNames.map((stageName) => {
    const durations = traces.flatMap((trace) =>
      (trace.spans ?? [])
        .filter((span) => span.name === stageName)
        .map((span) => span.duration_ms ?? 0)
    );

    const average =
      durations.length > 0
        ? durations.reduce((sum, duration) => sum + duration, 0) /
          durations.length
        : 0;

    return {
      stage:
        stageName.charAt(0).toUpperCase() + stageName.slice(1),
      averageDuration: Number(average.toFixed(1)),
    };
  });

  const historical = historicalMetrics ?? {};

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div>
          <h1>RAG Observability Dashboard</h1>
          <p className="subtitle">
            Monitor RAG performance, token usage, and estimated cost.
          </p>
        </div>

        <div className="refresh-status">
          <span className="live-dot"></span>
          Auto-refresh: 5 seconds
        </div>
      </header>

      {error && (
        <div className="error-message">
          <strong>Connection error:</strong> {error}
          <p>
            Check that FastAPI is running on port 8000.
            The dashboard will retry automatically.
          </p>
        </div>
      )}

      {loading ? (
        <h2 className="loading-message">
          Loading observability data...
        </h2>
      ) : (
        <>
          {/* Historical Metrics: all traces stored in MongoDB */}
          <section className="historical-section">
            <div className="section-header">
              <div>
                <h2>Historical Metrics</h2>
                <p className="subtitle">
                  Aggregated across all stored traces
                </p>
              </div>
            </div>

            <div className="stats historical-stats">
              <div className="stat-card">
                <h3>All-Time Traces</h3>
                <p>{historical.total_traces ?? 0}</p>
              </div>

              <div className="stat-card">
                <h3>Successful</h3>
                <p>{historical.successful_traces ?? 0}</p>
              </div>

              <div className="stat-card">
                <h3>Failed</h3>
                <p>{historical.failed_traces ?? 0}</p>
              </div>

              <div className="stat-card">
                <h3>Average Duration</h3>
                <p>
                  {Number(
                    historical.average_duration_ms ?? 0
                  ).toFixed(1)}{" "}
                  ms
                </p>
              </div>

              <div className="stat-card">
                <h3>Total Recorded Tokens</h3>
                <p>
                  {(
                    historical.total_tokens ?? 0
                  ).toLocaleString()}
                </p>
              </div>

              <div className="stat-card">
                <h3>Total Recorded Cost</h3>
                <p>
                  $
                  {Number(
                    historical.total_estimated_cost_usd ?? 0
                  ).toFixed(6)}
                </p>
                <small>
                  USD · {historical.traces_with_cost ?? 0} traces
                  with recorded cost
                </small>
              </div>
            </div>
          </section>

          {/* Recent Trace Statistics */}
          <section>
            <h2>Recent Trace Statistics</h2>
            <p className="subtitle">
              Calculated from the latest {traces.length} traces
              returned by the API.
            </p>

            <div className="stats">
              <div className="stat-card">
                <h3>Loaded Traces</h3>
                <p>{traces.length}</p>
              </div>

              <div className="stat-card">
                <h3>Successful</h3>
                <p>{successfulTraces}</p>
              </div>

              <div className="stat-card">
                <h3>Failed</h3>
                <p>{failedTraces}</p>
              </div>

              <div className="stat-card">
                <h3>Average Duration</h3>
                <p>{averageDuration} ms</p>
              </div>

              <div className="stat-card">
                <h3>Recent Estimated Cost</h3>
                <p>${recentTotalCost.toFixed(6)}</p>
                <small>
                  {tracesWithCost.length} traces with recorded cost
                </small>
              </div>

              <div className="stat-card">
                <h3>Average Cost per Trace</h3>
                <p>
                  {recentAverageCost === null
                    ? "N/A"
                    : `$${recentAverageCost.toFixed(6)}`}
                </p>
              </div>
            </div>
          </section>

          {/* RAG Stage Performance Chart */}
          <section className="chart-card">
            <h2>RAG Stage Performance</h2>
            <p className="subtitle">
              Average duration for each stage in the loaded traces.
            </p>

            <div className="chart-container">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={stagePerformance}
                  margin={{
                    top: 10,
                    right: 20,
                    left: 10,
                    bottom: 10,
                  }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="stage" />
                  <YAxis
                    tickFormatter={(value) => `${value} ms`}
                    width={85}
                  />
                  <Tooltip
                    formatter={(value) => [
                      `${value} ms`,
                      "Average duration",
                    ]}
                  />
                  <Bar
                    dataKey="averageDuration"
                    name="Average duration"
                    fill="#3b82f6"
                    radius={[6, 6, 0, 0]}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </section>

          {/* Recent Traces */}
          <section className="traces-section">
            <div className="section-header">
              <h2>Recent Traces</h2>
              <span>{traces.length} traces loaded</span>
            </div>

            {traces.length === 0 ? (
              <div className="empty-state">
                <h3>No traces found</h3>
                <p>
                  Run a query through your RAG pipeline to generate
                  your first trace.
                </p>
              </div>
            ) : (
              traces.map((trace) => {
                const isExpanded =
                  expandedTrace === trace.trace_id;

                const spans = trace.spans ?? [];

                const maxDuration = Math.max(
                  ...spans.map(
                    (span) => span.duration_ms ?? 0
                  ),
                  1
                );

                const usage = trace.usage ?? {};

                return (
                  <article className="trace" key={trace.trace_id}>
                    <button
                      type="button"
                      className="trace-toggle"
                      aria-expanded={isExpanded}
                      onClick={() =>
                        setExpandedTrace(
                          isExpanded ? null : trace.trace_id
                        )
                      }
                    >
                      <span className="trace-query">
                        <span className="expand-icon">
                          {isExpanded ? "▼" : "▶"}
                        </span>
                        {trace.query || "Untitled query"}
                      </span>

                      <span
                        className={`status-badge ${
                          trace.status === "ok"
                            ? "status-success"
                            : "status-error"
                        }`}
                      >
                        {trace.status || "unknown"}
                      </span>
                    </button>

                    <div className="trace-details">
                      <div className="trace-detail">
                        <span>Total Duration</span>
                        <strong>
                          {(
                            trace.total_duration_ms ?? 0
                          ).toLocaleString()}{" "}
                          ms
                        </strong>
                      </div>

                      <div className="trace-detail">
                        <span>Trace ID</span>
                        <code>{trace.trace_id}</code>
                      </div>

                      {trace.model && (
                        <div className="trace-detail">
                          <span>Model</span>
                          <strong>{trace.model}</strong>
                        </div>
                      )}

                      {trace.created_at && (
                        <div className="trace-detail">
                          <span>Created At</span>
                          <strong>
                            {new Date(
                              trace.created_at
                            ).toLocaleString()}
                          </strong>
                        </div>
                      )}
                    </div>

                    {isExpanded && (
                      <div className="span-section">
                        <h3>Token Usage and Cost</h3>

                        <div className="usage-grid">
                          <div>
                            <span>Input Tokens</span>
                            <strong>
                              {usage.prompt_tokens ?? "N/A"}
                            </strong>
                          </div>

                          <div>
                            <span>Output Tokens</span>
                            <strong>
                              {usage.completion_tokens ?? "N/A"}
                            </strong>
                          </div>

                          <div>
                            <span>Total Tokens</span>
                            <strong>
                              {usage.total_tokens ?? "N/A"}
                            </strong>
                          </div>

                          <div>
                            <span>Estimated Cost</span>
                            <strong>
                              {typeof trace.estimated_cost_usd ===
                              "number"
                                ? `$${trace.estimated_cost_usd.toFixed(8)}`
                                : "N/A"}
                            </strong>
                          </div>
                        </div>

                        <h3>Trace Spans</h3>

                        {spans.length === 0 ? (
                          <p>No span details available.</p>
                        ) : (
                          spans.map((span, index) => (
                            <div
                              className="span"
                              key={`${span.name}-${index}`}
                            >
                              <div className="span-header">
                                <strong>{span.name}</strong>
                                <span>
                                  {span.duration_ms ?? 0} ms
                                </span>
                              </div>

                              <div className="duration-bar">
                                <div
                                  className="duration-fill"
                                  style={{
                                    width: `${
                                      ((span.duration_ms ?? 0) /
                                        maxDuration) *
                                      100
                                    }%`,
                                  }}
                                ></div>
                              </div>

                              <div className="span-status">
                                Status: {span.status || "unknown"}
                                {span.error && (
                                  <p className="span-error">
                                    Error: {span.error}
                                  </p>
                                )}
                              </div>
                            </div>
                          ))
                        )}
                      </div>
                    )}
                  </article>
                );
              })
            )}
          </section>
        </>
      )}

      <footer className="dashboard-footer">
        RAG Observability Dashboard · FastAPI · React · MongoDB ·
        Qdrant
      </footer>
    </div>
  );
}

export default App;
