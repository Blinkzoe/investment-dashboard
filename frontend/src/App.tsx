import { useEffect, useState } from "react";
import "./App.css";

type PortfolioSummary = {
  snapshot_at: string | null;
  total_value: string | null;
  contributed_capital: string | null;
  gain: string | null;
  return_percentage: string | null;
  currency: string | null;
  source: string | null;
};

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

function App() {
  const [summary, setSummary] = useState<PortfolioSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch(`${API_URL}/api/v1/portfolio-summary`)
      .then((response) => {
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }
        return response.json();
      })
      .then(setSummary)
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  const money = (value: string | null, currency: string | null) => {
    if (value === null || currency === null) return "—";

    return new Intl.NumberFormat("es-MX", {
      style: "currency",
      currency,
      maximumFractionDigits: 2,
    }).format(Number(value));
  };

  return (
    <main className="dashboard">
      <header className="dashboard-header">
        <div>
          <p className="eyebrow">Investment Dashboard</p>
          <h1>Portfolio Overview</h1>
          <p className="subtitle">
            Resumen consolidado de tu portafolio.
          </p>
        </div>
      </header>

      {loading && <p className="status">Cargando...</p>}

      {error && (
        <div className="error">
          No se pudo conectar con el backend: {error}
        </div>
      )}

      {!loading && !error && summary && (
        <>
          <section className="summary-grid">
            <article className="card primary">
              <span>Valor total</span>
              <strong>{money(summary.total_value, summary.currency)}</strong>
            </article>

            <article className="card">
              <span>Capital aportado</span>
              <strong>
                {money(summary.contributed_capital, summary.currency)}
              </strong>
            </article>

            <article className="card">
              <span>Ganancia</span>
              <strong>
                {money(summary.gain, summary.currency)}
              </strong>
            </article>

            <article className="card">
              <span>Rendimiento</span>
              <strong>
                {summary.return_percentage === null
                  ? "—"
                  : `${summary.return_percentage}%`}
              </strong>
            </article>
          </section>

          <section className="details">
            <div>
              <span>Fuente</span>
              <strong>{summary.source ?? "—"}</strong>
            </div>
            <div>
              <span>Último snapshot</span>
              <strong>
                {summary.snapshot_at
                  ? new Date(summary.snapshot_at).toLocaleString("es-MX")
                  : "—"}
              </strong>
            </div>
          </section>
        </>
      )}
    </main>
  );
}

export default App;
