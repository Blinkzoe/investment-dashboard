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

type Account = {
  id: number;
  institution: string;
  name: string;
  account_type: string;
  base_currency: string;
  external_id: string | null;
};

type AccountSnapshot = {
  id: number;
  account_id: number;
  snapshot_at: string;
  total_value: string;
  cash_value: string | null;
  currency: string;
  source: string;
  notes: string | null;
  created_at: string;
};

type MonthlySummary = {
  month: string;
  total_value: string;
  interest_value: string;
  contribution_value: string;
  withdrawal_value: string;
  account_count: number;
};

type Transaction = {
  id: number;
  account_id: number;
  asset_id: number;
  transaction_type: string;
  status: string;
  quantity: string | null;
  unit_price: string | null;
  gross_amount: string | null;
  commission: string;
  taxes: string;
  other_fees: string;
  total_amount: string | null;
  currency: string;
  trade_date: string | null;
  source: string;
};

const API_URL = import.meta.env.VITE_API_URL ?? "";

function money(value: string | null, currency: string | null) {
  if (value === null || currency === null) return "—";
  return new Intl.NumberFormat("es-MX", {
    style: "currency",
    currency,
    maximumFractionDigits: 2,
  }).format(Number(value));
}

function number(value: string | null) {
  if (value === null) return "—";
  return new Intl.NumberFormat("es-MX", {
    maximumFractionDigits: 4,
  }).format(Number(value));
}

function App() {
  const [summary, setSummary] = useState<PortfolioSummary | null>(null);
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [accountSnapshots, setAccountSnapshots] = useState<AccountSnapshot[]>([]);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [monthlySummary, setMonthlySummary] = useState<MonthlySummary[]>([]);
  const [activeTab, setActiveTab] = useState<"all" | "fixed" | "variable">("all");
  const [accountFilter, setAccountFilter] = useState("all");
  const [typeFilter, setTypeFilter] = useState("all");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [authChecked, setAuthChecked] = useState(false);
  const [authenticated, setAuthenticated] = useState(false);
  const [username, setUsername] = useState<string | null>(null);
  const [loginUsername, setLoginUsername] = useState("admin");
  const [loginPassword, setLoginPassword] = useState("");
  const [loginError, setLoginError] = useState<string | null>(null);
  const [loginLoading, setLoginLoading] = useState(false);

  useEffect(() => {
    fetch(`${API_URL}/api/v1/auth/me`, { credentials: "include" })
      .then((response) => {
        if (!response.ok) throw new Error("not authenticated");
        return response.json() as Promise<{ authenticated: boolean; username: string | null }>;
      })
      .then((data) => {
        setAuthenticated(data.authenticated);
        setUsername(data.username);
      })
      .catch(() => {
        setAuthenticated(false);
        setUsername(null);
      })
      .finally(() => setAuthChecked(true));
  }, []);

  useEffect(() => {
    if (!authenticated) return;

    Promise.all([
      fetch(`${API_URL}/api/v1/portfolio-summary`, { credentials: "include" }),
      fetch(`${API_URL}/api/v1/accounts`, { credentials: "include" }),
      fetch(`${API_URL}/api/v1/snapshots/accounts`, { credentials: "include" }),
      fetch(`${API_URL}/api/v1/transactions`, { credentials: "include" }),
      fetch(
        `${API_URL}/api/v1/snapshots/accounts/monthly-summary?source=FIXED_INCOME_HISTORY`,
        { credentials: "include" },
      ),
    ])
      .then(async (responses) => {
        const [
          summaryResponse,
          accountsResponse,
          snapshotsResponse,
          transactionsResponse,
          monthlySummaryResponse,
        ] = responses;

        if (!summaryResponse.ok) throw new Error(`Portfolio API HTTP ${summaryResponse.status}`);
        if (!accountsResponse.ok) throw new Error(`Accounts API HTTP ${accountsResponse.status}`);
        if (!snapshotsResponse.ok) throw new Error(`Snapshots API HTTP ${snapshotsResponse.status}`);
        if (!transactionsResponse.ok) throw new Error(`Transactions API HTTP ${transactionsResponse.status}`);
        if (!monthlySummaryResponse.ok) {
          throw new Error(`Monthly summary API HTTP ${monthlySummaryResponse.status}`);
        }

        return Promise.all([
          summaryResponse.json() as Promise<PortfolioSummary>,
          accountsResponse.json() as Promise<Account[]>,
          snapshotsResponse.json() as Promise<AccountSnapshot[]>,
          transactionsResponse.json() as Promise<Transaction[]>,
          monthlySummaryResponse.json() as Promise<MonthlySummary[]>,
        ]);
      })
      .then(([portfolioSummary, accountList, snapshotList, transactionList, monthlyList]) => {
        setSummary(portfolioSummary);
        setAccounts(accountList.filter((account) => !account.institution.startsWith("TEST-")));
        setAccountSnapshots(snapshotList.filter((snapshot) => snapshot.source !== "TEST"));
        setTransactions(transactionList.filter((transaction) => transaction.source !== "TEST"));
        setMonthlySummary(monthlyList);
      })
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false));
  }, [authenticated]);

  async function handleLogin(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoginLoading(true);
    setLoginError(null);

    try {
      const response = await fetch(`${API_URL}/api/v1/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({
          username: loginUsername,
          password: loginPassword,
        }),
      });

      if (!response.ok) {
        setLoginError("Usuario o contraseña incorrectos.");
        return;
      }

      const data = (await response.json()) as {
        authenticated: boolean;
        username: string | null;
      };

      setAuthenticated(data.authenticated);
      setUsername(data.username);
      setLoginPassword("");
    } catch {
      setLoginError("No se pudo conectar con el servidor.");
    } finally {
      setLoginLoading(false);
    }
  }

  async function handleLogout() {
    await fetch(`${API_URL}/api/v1/auth/logout`, {
      method: "POST",
      credentials: "include",
    });
    setAuthenticated(false);
    setUsername(null);
    setSummary(null);
    setAccounts([]);
    setAccountSnapshots([]);
    setTransactions([]);
    setMonthlySummary([]);
  }

  const accountMap = new Map(
    accounts.map((account) => [account.id, account]),
  );

  const filteredTransactions = transactions.filter((transaction) => {
    const accountOk =
      accountFilter === "all" ||
      String(transaction.account_id) === accountFilter;
    const typeOk =
      typeFilter === "all" ||
      transaction.transaction_type === typeFilter;

    return accountOk && typeOk;
  });

  const latest = new Map<number, AccountSnapshot>();

  for (const snapshot of accountSnapshots) {
    const previous = latest.get(snapshot.account_id);

    if (!previous || snapshot.snapshot_at > previous.snapshot_at) {
      latest.set(snapshot.account_id, snapshot);
    }
  }

  const latestSnapshots = Array.from(latest.values()).sort(
    (a, b) => Number(b.total_value) - Number(a.total_value),
  );

  const fixedIncomeSnapshots = latestSnapshots.filter(
    (snapshot) => snapshot.source === "FIXED_INCOME_HISTORY",
  );

  const variableSnapshots = latestSnapshots.filter(
    (snapshot) => snapshot.source !== "FIXED_INCOME_HISTORY",
  );

  const totalAccounts = latestSnapshots.reduce(
    (sum, snapshot) => sum + Number(snapshot.total_value),
    0,
  );

  const fixedIncomeTotal = fixedIncomeSnapshots.reduce(
    (sum, snapshot) => sum + Number(snapshot.total_value),
    0,
  );

  const variableTotal = variableSnapshots.reduce(
    (sum, snapshot) => sum + Number(snapshot.total_value),
    0,
  );

  const fixedIncomeInterestTotal = monthlySummary.reduce(
    (sum, month) => sum + Number(month.interest_value),
    0,
  );

  const latestMonthlyInterest =
    monthlySummary.length > 0
      ? Number(monthlySummary[monthlySummary.length - 1].interest_value)
      : 0;

  if (!authChecked) {
    return <main className="dashboard"><div className="loading">Verificando acceso…</div></main>;
  }

  if (!authenticated) {
    return (
      <main className="dashboard login-page">
        <form className="login-card" onSubmit={handleLogin}>
          <p className="eyebrow">INVESTMENTS / PRIVATE</p>
          <h1>Mi portafolio</h1>
          <p className="subtitle">Inicia sesión para acceder a tus inversiones.</p>

          <label>
            <span>Usuario</span>
            <input
              value={loginUsername}
              onChange={(event) => setLoginUsername(event.target.value)}
              autoComplete="username"
            />
          </label>

          <label>
            <span>Contraseña</span>
            <input
              type="password"
              value={loginPassword}
              onChange={(event) => setLoginPassword(event.target.value)}
              autoComplete="current-password"
            />
          </label>

          {loginError && <div className="error">{loginError}</div>}

          <button type="submit" disabled={loginLoading}>
            {loginLoading ? "Entrando…" : "Iniciar sesión"}
          </button>
        </form>
      </main>
    );
  }

  const annualRate = 0.10;
  const monthlyRate = Math.pow(1 + annualRate, 1 / 12) - 1;

  const fixedIncomeBenchmark = monthlySummary.map((month) => ({
    month: month.month,
    actualInterest: Number(month.interest_value),
    benchmarkMonthlyInterest:
      Number(month.total_value) * monthlyRate,
    benchmarkValue:
      Number(month.total_value) +
      Number(month.total_value) * monthlyRate,
  }));

  const fixedIncomeBenchmarkTotal =
    fixedIncomeBenchmark.reduce(
      (sum, month) => sum + month.benchmarkMonthlyInterest,
      0,
    );

  const snapshotDate = summary?.snapshot_at
    ? new Date(summary.snapshot_at)
    : new Date();

  const variableBenchmark = transactions.reduce((total, transaction) => {
    if (!transaction.trade_date) return total;

    const amount = Number(transaction.total_amount ?? 0);

    if (
      amount <= 0 ||
      transaction.transaction_type !== "BUY"
    ) {
      return total;
    }

    const start = new Date(transaction.trade_date);

    const years =
      Math.max(
        0,
        snapshotDate.getTime() - start.getTime(),
      ) /
      (365.25 * 24 * 60 * 60 * 1000);

    return (
      total +
      amount * (Math.pow(1 + annualRate, years) - 1)
    );
  }, 0);

const variableActualGain = Number(summary?.gain ?? 0);

  const variableVsBenchmark =
    variableActualGain - variableBenchmark;

const fixedIncomeVsBenchmark =
  fixedIncomeInterestTotal - fixedIncomeBenchmarkTotal;

  return (
    <main className="dashboard">
      <header className="topbar">
        <div>
          <p className="eyebrow">INVESTMENTS / OVERVIEW</p>
          <h1>Mi portafolio</h1>
          <p className="subtitle">
            Patrimonio, rendimiento e intereses en una sola vista.
          </p>
        </div>

        <div className="topbar-meta">
          <span className="live-dot" />
          <span>{username ?? "admin"}</span>
          <button type="button" onClick={handleLogout}>
            Salir
          </button>
        </div>
      </header>

      <nav className="dashboard-tabs" aria-label="Vista del portafolio">
        <button
          type="button"
          className={activeTab === "all" ? "active" : ""}
          onClick={() => setActiveTab("all")}
        >
          Todo
        </button>

        <button
          type="button"
          className={activeTab === "fixed" ? "active" : ""}
          onClick={() => setActiveTab("fixed")}
        >
          Renta fija
        </button>

        <button
          type="button"
          className={activeTab === "variable" ? "active" : ""}
          onClick={() => setActiveTab("variable")}
        >
          Renta variable
        </button>
      </nav>

      {loading && (
        <div className="loading">
          Cargando portafolio…
        </div>
      )}

      {error && (
        <div className="error">
          No se pudo cargar el dashboard: {error}
        </div>
      )}

      {!loading && !error && summary && (
        <>
          {/* ==================================================
              TODO
          ================================================== */}

          {activeTab === "all" && (
            <>
              <section className="hero-grid">
                <article className="hero-card">
                  <span className="metric-label">
                    Patrimonio total
                  </span>
                  <strong className="hero-value">
                    {money(String(totalAccounts), "MXN")}
                  </strong>
                  <span className="metric-foot">
                    Todas las cuentas
                  </span>
                </article>

                <article className="metric-card">
                  <span className="metric-label">
                    Renta fija
                  </span>
                  <strong className="positive">
                    {money(String(fixedIncomeTotal), "MXN")}
                  </strong>
                  <span className="metric-foot">
                    13 cuentas
                  </span>
                </article>

                <article className="metric-card">
                  <span className="metric-label">
                    Renta variable
                  </span>
                  <strong>
                    {money(String(variableTotal), "MXN")}
                  </strong>
                  <span className="metric-foot">
                    GBM / Fintual
                  </span>
                </article>

                <article className="metric-card">
                  <span className="metric-label">
                    Intereses acumulados
                  </span>
                  <strong className="positive">
                    {money(
                      String(fixedIncomeInterestTotal),
                      "MXN",
                    )}
                  </strong>
                  <span className="metric-foot">
                    Desde octubre 2022
                  </span>
                </article>
              </section>

              <section className="dashboard-insight">
                <div>
                  <p className="eyebrow">PORTFOLIO MIX</p>
                  <h2>¿Dónde está tu dinero?</h2>
                  <p>
                    La mayor parte del patrimonio está actualmente
                    en renta fija. La pestaña correspondiente permite
                    comparar sus intereses contra un benchmark del
                    10% anual.
                  </p>
                </div>

                <div className="insight-numbers">
                  <div>
                    <span>Renta fija</span>
                    <strong>
                      {totalAccounts > 0
                        ? `${(
                            (fixedIncomeTotal /
                              totalAccounts) *
                            100
                          ).toFixed(1)}%`
                        : "—"}
                    </strong>
                  </div>

                  <div>
                    <span>Renta variable</span>
                    <strong>
                      {totalAccounts > 0
                        ? `${(
                            (variableTotal /
                              totalAccounts) *
                            100
                          ).toFixed(1)}%`
                        : "—"}
                    </strong>
                  </div>
                </div>
              </section>

              <section className="main-grid">
                <article className="panel">
                  <div className="panel-header">
                    <div>
                      <p className="eyebrow">ALLOCATION</p>
                      <h2>Distribución</h2>
                    </div>
                    <span className="panel-note">
                      {money(String(totalAccounts), "MXN")}
                    </span>
                  </div>

                  <div className="allocation-list">
                    {latestSnapshots.map((snapshot) => {
                      const account = accountMap.get(
                        snapshot.account_id,
                      );

                      const percentage =
                        totalAccounts > 0
                          ? (Number(snapshot.total_value) /
                              totalAccounts) *
                            100
                          : 0;

                      return (
                        <div
                          className="allocation-item"
                          key={snapshot.account_id}
                        >
                          <div className="allocation-top">
                            <div>
                              <strong>
                                {account?.name ??
                                  `Cuenta ${snapshot.account_id}`}
                              </strong>
                              <span>
                                {account?.institution ?? "—"}
                              </span>
                            </div>

                            <div className="allocation-amount">
                              <strong>
                                {money(
                                  snapshot.total_value,
                                  snapshot.currency,
                                )}
                              </strong>
                              <span>
                                {percentage.toFixed(1)}%
                              </span>
                            </div>
                          </div>

                          <div className="allocation-bar">
                            <span
                              style={{
                                width: `${Math.min(
                                  percentage,
                                  100,
                                )}%`,
                              }}
                            />
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </article>

                <article className="panel">
                  <div className="panel-header">
                    <div>
                      <p className="eyebrow">VARIABLE</p>
                      <h2>Rendimiento actual</h2>
                    </div>
                  </div>

                  <div className="summary-list">
                    <div>
                      <span>Valor</span>
                      <strong>
                        {money(
                          summary.total_value,
                          summary.currency,
                        )}
                      </strong>
                    </div>

                    <div>
                      <span>Capital aportado</span>
                      <strong>
                        {money(
                          summary.contributed_capital,
                          summary.currency,
                        )}
                      </strong>
                    </div>

                    <div>
                      <span>Ganancia</span>
                      <strong className="positive">
                        {money(
                          summary.gain,
                          summary.currency,
                        )}
                      </strong>
                    </div>

                    <div>
                      <span>Rendimiento</span>
                      <strong className="positive">
                        {summary.return_percentage === null
                          ? "—"
                          : `${summary.return_percentage}%`}
                      </strong>
                    </div>
                  </div>
                </article>
              </section>
            </>
          )}

          {/* ==================================================
              RENTA FIJA
          ================================================== */}

          {activeTab === "fixed" && (
            <>
              <section className="hero-grid">
                <article className="hero-card">
                  <span className="metric-label">
                    Patrimonio renta fija
                  </span>
                  <strong className="hero-value">
                    {money(
                      String(fixedIncomeTotal),
                      "MXN",
                    )}
                  </strong>
                  <span className="metric-foot">
                    Septiembre 2026
                  </span>
                </article>

                <article className="metric-card">
                  <span className="metric-label">
                    Intereses acumulados
                  </span>
                  <strong className="positive">
                    {money(
                      String(fixedIncomeInterestTotal),
                      "MXN",
                    )}
                  </strong>
                  <span className="metric-foot">
                    48 meses registrados
                  </span>
                </article>

                <article className="metric-card">
                  <span className="metric-label">
                    Interés último mes
                  </span>
                  <strong className="positive">
                    {money(
                      String(latestMonthlyInterest),
                      "MXN",
                    )}
                  </strong>
                  <span className="metric-foot">
                    Septiembre 2026
                  </span>
                </article>

                <article className="metric-card">
                  <span className="metric-label">
                    Benchmark 10% anual
                  </span>
                  <strong>
                    {money(
                      String(fixedIncomeBenchmarkTotal),
                      "MXN",
                    )}
                  </strong>
                  <span className="metric-foot">
                    Referencia hipotética
                  </span>
                </article>
              </section>

              <section className="comparison-card">
                <div>
                  <p className="eyebrow">BENCHMARK</p>
                  <h2>Renta fija vs 10% anual</h2>
                  <p>
                    Comparación orientativa. El benchmark calcula
                    10% anual equivalente a una tasa mensual compuesta
                    aplicada al saldo de cada mes. No representa un
                    rendimiento realmente disponible.
                  </p>
                </div>

                <div className="comparison-grid">
                  <div>
                    <span>Intereses registrados</span>
                    <strong className="positive">
                      {money(
                        String(fixedIncomeInterestTotal),
                        "MXN",
                      )}
                    </strong>
                  </div>

                  <div>
                    <span>Benchmark</span>
                    <strong>
                      {money(
                        String(fixedIncomeBenchmarkTotal),
                        "MXN",
                      )}
                    </strong>
                  </div>

                  <div>
                    <span>Diferencia</span>
                    <strong
                      className={
                        fixedIncomeVsBenchmark >= 0
                          ? "positive"
                          : "negative"
                      }
                    >
                      {money(
                        String(fixedIncomeVsBenchmark),
                        "MXN",
                      )}
                    </strong>
                  </div>
                </div>
              </section>

              <section className="chart-grid">
                <article className="chart-card">
                  <div className="chart-heading">
                    <div>
                      <p className="eyebrow">PATRIMONIO</p>
                      <h2>Evolución mensual</h2>
                    </div>
                    <span>48 meses</span>
                  </div>

                  <div className="mini-chart">
                    {monthlySummary.map((month) => {
                      const max = Math.max(
                        ...monthlySummary.map((item) =>
                          Number(item.total_value),
                        ),
                        1,
                      );

                      const height =
                        (Number(month.total_value) / max) *
                        100;

                      const [year, monthNumber] =
                        month.month.slice(0, 7).split("-");

                      const label = new Date(
                        Number(year),
                        Number(monthNumber) - 1,
                        1,
                      ).toLocaleDateString("es-MX", {
                        month: "short",
                        year: "2-digit",
                      });

                      return (
                        <div
                          className="chart-column"
                          key={month.month}
                          title={`${label}: ${money(
                            month.total_value,
                            "MXN",
                          )}`}
                        >
                          <span
                            style={{
                              height: `${Math.max(
                                height,
                                2,
                              )}%`,
                            }}
                          />
                        </div>
                      );
                    })}
                  </div>
                </article>

                <article className="chart-card">
                  <div className="chart-heading">
                    <div>
                      <p className="eyebrow">INTERESES</p>
                      <h2>Interés generado por mes</h2>
                    </div>
                    <span>MXN</span>
                  </div>

                  <div className="interest-chart">
                    {monthlySummary.map((month) => {
                      const max = Math.max(
                        ...monthlySummary.map((item) =>
                          Number(item.interest_value),
                        ),
                        1,
                      );

                      const height =
                        (Number(month.interest_value) / max) *
                        100;

                      const [year, monthNumber] =
                        month.month.slice(0, 7).split("-");

                      const label = new Date(
                        Number(year),
                        Number(monthNumber) - 1,
                        1,
                      ).toLocaleDateString("es-MX", {
                        month: "short",
                        year: "2-digit",
                      });

                      return (
                        <div
                          className="chart-column"
                          key={month.month}
                          title={`${label}: ${money(
                            month.interest_value,
                            "MXN",
                          )}`}
                        >
                          <span
                            style={{
                              height: `${Math.max(
                                height,
                                2,
                              )}%`,
                            }}
                          />
                        </div>
                      );
                    })}
                  </div>
                </article>
              </section>

              <section className="main-grid">
                <article className="panel">
                  <div className="panel-header">
                    <div>
                      <p className="eyebrow">FIXED INCOME</p>
                      <h2>Distribución actual</h2>
                    </div>
                    <span className="panel-note">
                      {money(
                        String(fixedIncomeTotal),
                        "MXN",
                      )}
                    </span>
                  </div>

                  <div className="allocation-list">
                    {fixedIncomeSnapshots.map((snapshot) => {
                      const account = accountMap.get(
                        snapshot.account_id,
                      );

                      const percentage =
                        fixedIncomeTotal > 0
                          ? (Number(snapshot.total_value) /
                              fixedIncomeTotal) *
                            100
                          : 0;

                      return (
                        <div
                          className="allocation-item"
                          key={snapshot.account_id}
                        >
                          <div className="allocation-top">
                            <div>
                              <strong>
                                {account?.name ??
                                  `Cuenta ${snapshot.account_id}`}
                              </strong>
                              <span>
                                {account?.institution ?? "—"}
                              </span>
                            </div>

                            <div className="allocation-amount">
                              <strong>
                                {money(
                                  snapshot.total_value,
                                  snapshot.currency,
                                )}
                              </strong>
                              <span>
                                {percentage.toFixed(1)}%
                              </span>
                            </div>
                          </div>

                          <div className="allocation-bar">
                            <span
                              style={{
                                width: `${Math.min(
                                  percentage,
                                  100,
                                )}%`,
                              }}
                            />
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </article>

                <article className="panel">
                  <div className="panel-header">
                    <div>
                      <p className="eyebrow">DETAIL</p>
                      <h2>Último mes</h2>
                    </div>
                  </div>

                  <div className="summary-list">
                    {monthlySummary.length > 0 &&
                      (() => {
                        const latest =
                          monthlySummary[
                            monthlySummary.length - 1
                          ];

                        return (
                          <>
                            <div>
                              <span>Patrimonio</span>
                              <strong>
                                {money(
                                  latest.total_value,
                                  "MXN",
                                )}
                              </strong>
                            </div>

                            <div>
                              <span>Intereses</span>
                              <strong className="positive">
                                {money(
                                  latest.interest_value,
                                  "MXN",
                                )}
                              </strong>
                            </div>

                            <div>
                              <span>Movimientos</span>
                              <strong>
                                {money(
                                  String(
                                    Number(
                                      latest.contribution_value,
                                    ) -
                                      Number(
                                        latest.withdrawal_value,
                                      ),
                                  ),
                                  "MXN",
                                )}
                              </strong>
                            </div>

                            <div>
                              <span>Cuentas</span>
                              <strong>
                                {latest.account_count}
                              </strong>
                            </div>
                          </>
                        );
                      })()}
                  </div>
                </article>
              </section>

              <section className="panel monthly-performance">
                <div className="panel-header">
                  <div>
                    <p className="eyebrow">HISTORY</p>
                    <h2>Histórico mensual</h2>
                  </div>

                  <span className="panel-note">
                    {monthlySummary.length} meses
                  </span>
                </div>

                <div className="table-wrap">
                  <table>
                    <thead>
                      <tr>
                        <th>Mes</th>
                        <th>Patrimonio</th>
                        <th>Intereses</th>
                        <th>Movimientos</th>
                        <th>Cuentas</th>
                      </tr>
                    </thead>

                    <tbody>
                      {monthlySummary.map((month) => {
                        const [year, monthNumber] =
                          month.month.slice(0, 7).split("-");

                        const date = new Date(
                          Number(year),
                          Number(monthNumber) - 1,
                          1,
                        );

                        const movement =
                          Number(
                            month.contribution_value,
                          ) -
                          Number(
                            month.withdrawal_value,
                          );

                        return (
                          <tr key={month.month}>
                            <td>
                              {date.toLocaleDateString(
                                "es-MX",
                                {
                                  month: "long",
                                  year: "numeric",
                                },
                              )}
                            </td>

                            <td>
                              {money(
                                month.total_value,
                                "MXN",
                              )}
                            </td>

                            <td className="positive">
                              {money(
                                month.interest_value,
                                "MXN",
                              )}
                            </td>

                            <td>
                              {money(
                                String(movement),
                                "MXN",
                              )}
                            </td>

                            <td>
                              {month.account_count}
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </section>
            </>
          )}

          {/* ==================================================
              RENTA VARIABLE
          ================================================== */}

          {activeTab === "variable" && (
            <>
              <section className="hero-grid">
                <article className="hero-card">
                  <span className="metric-label">
                    Patrimonio renta variable
                  </span>
                  <strong className="hero-value">
                    {money(
                      String(variableTotal),
                      "MXN",
                    )}
                  </strong>
                  <span className="metric-foot">
                    GBM / Fintual
                  </span>
                </article>

                <article className="metric-card">
                  <span className="metric-label">
                    Ganancia real
                  </span>
                  <strong
                    className={
                      variableActualGain >= 0
                        ? "positive"
                        : "negative"
                    }
                  >
                    {money(
                      summary.gain,
                      summary.currency,
                    )}
                  </strong>
                  <span className="metric-foot">
                    Según GBM / Fintual
                  </span>
                </article>

                <article className="metric-card">
                  <span className="metric-label">
                    Benchmark 10% anual
                  </span>
                  <strong>
                    {money(
                      String(variableBenchmark),
                      summary.currency,
                    )}
                  </strong>
                  <span className="metric-foot">
                    Ganancia hipotética
                  </span>
                </article>

                <article className="metric-card">
                  <span className="metric-label">
                    Real vs benchmark
                  </span>
                  <strong
                    className={
                      variableVsBenchmark >= 0
                        ? "positive"
                        : "negative"
                    }
                  >
                    {money(
                      String(variableVsBenchmark),
                      summary.currency,
                    )}
                  </strong>
                  <span className="metric-foot">
                    Diferencia acumulada
                  </span>
                </article>
              </section>

              <section className="comparison-card">
                <div>
                  <p className="eyebrow">10% ANUAL</p>
                  <h2>¿Conviene más la renta variable?</h2>
                  <p>
                    El benchmark trata cada compra registrada como
                    si hubiera permanecido invertida al 10% anual
                    desde su fecha hasta el último snapshot.
                    Es una referencia comparativa, no un cálculo
                    de rendimiento financiero oficial.
                  </p>
                </div>

                <div className="comparison-grid">
                  <div>
                    <span>Ganancia real</span>
                    <strong
                      className={
                        variableActualGain >= 0
                          ? "positive"
                          : "negative"
                      }
                    >
                      {money(
                        String(variableActualGain),
                        summary.currency,
                      )}
                    </strong>
                  </div>

                  <div>
                    <span>Ganancia benchmark</span>
                    <strong>
                      {money(
                        String(variableBenchmark),
                        summary.currency,
                      )}
                    </strong>
                  </div>

                  <div>
                    <span>Resultado</span>
                    <strong
                      className={
                        variableVsBenchmark >= 0
                          ? "positive"
                          : "negative"
                      }
                    >
                      {variableVsBenchmark >= 0
                        ? "Supera benchmark"
                        : "Debajo del benchmark"}
                    </strong>
                  </div>
                </div>
              </section>

              <section className="main-grid">
                <article className="panel">
                  <div className="panel-header">
                    <div>
                      <p className="eyebrow">VARIABLE INCOME</p>
                      <h2>Distribución</h2>
                    </div>

                    <span className="panel-note">
                      {money(
                        String(variableTotal),
                        "MXN",
                      )}
                    </span>
                  </div>

                  <div className="allocation-list">
                    {variableSnapshots.map((snapshot) => {
                      const account = accountMap.get(
                        snapshot.account_id,
                      );

                      const percentage =
                        variableTotal > 0
                          ? (Number(snapshot.total_value) /
                              variableTotal) *
                            100
                          : 0;

                      return (
                        <div
                          className="allocation-item"
                          key={snapshot.account_id}
                        >
                          <div className="allocation-top">
                            <div>
                              <strong>
                                {account?.name ??
                                  `Cuenta ${snapshot.account_id}`}
                              </strong>
                              <span>
                                {account?.institution ?? "—"}
                              </span>
                            </div>

                            <div className="allocation-amount">
                              <strong>
                                {money(
                                  snapshot.total_value,
                                  snapshot.currency,
                                )}
                              </strong>
                              <span>
                                {percentage.toFixed(1)}%
                              </span>
                            </div>
                          </div>

                          <div className="allocation-bar">
                            <span
                              style={{
                                width: `${Math.min(
                                  percentage,
                                  100,
                                )}%`,
                              }}
                            />
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </article>

                <article className="panel">
                  <div className="panel-header">
                    <div>
                      <p className="eyebrow">PERFORMANCE</p>
                      <h2>Resultado</h2>
                    </div>
                  </div>

                  <div className="summary-list">
                    <div>
                      <span>Valor actual</span>
                      <strong>
                        {money(
                          summary.total_value,
                          summary.currency,
                        )}
                      </strong>
                    </div>

                    <div>
                      <span>Capital aportado</span>
                      <strong>
                        {money(
                          summary.contributed_capital,
                          summary.currency,
                        )}
                      </strong>
                    </div>

                    <div>
                      <span>Ganancia</span>
                      <strong className="positive">
                        {money(
                          summary.gain,
                          summary.currency,
                        )}
                      </strong>
                    </div>

                    <div>
                      <span>Rendimiento</span>
                      <strong className="positive">
                        {summary.return_percentage === null
                          ? "—"
                          : `${summary.return_percentage}%`}
                      </strong>
                    </div>

                    <div>
                      <span>Benchmark 10%</span>
                      <strong>
                        {money(
                          String(variableBenchmark),
                          summary.currency,
                        )}
                      </strong>
                    </div>
                  </div>
                </article>
              </section>

              <section className="panel transactions-panel">
                <div className="panel-header">
                  <div>
                    <p className="eyebrow">ACTIVITY</p>
                    <h2>Operaciones</h2>
                  </div>

                  <span className="panel-note">
                    {filteredTransactions.length} registros
                  </span>
                </div>

                <div className="filters">
                  <label>
                    <span>Cuenta</span>
                    <select
                      value={accountFilter}
                      onChange={(event) =>
                        setAccountFilter(event.target.value)
                      }
                    >
                      <option value="all">Todas</option>

                      {accounts.map((account) => (
                        <option
                          key={account.id}
                          value={String(account.id)}
                        >
                          {account.name}
                        </option>
                      ))}
                    </select>
                  </label>

                  <label>
                    <span>Tipo</span>
                    <select
                      value={typeFilter}
                      onChange={(event) =>
                        setTypeFilter(event.target.value)
                      }
                    >
                      <option value="all">Todos</option>

                      {Array.from(
                        new Set(
                          transactions.map(
                            (transaction) =>
                              transaction.transaction_type,
                          ),
                        ),
                      ).map((type) => (
                        <option key={type} value={type}>
                          {type}
                        </option>
                      ))}
                    </select>
                  </label>
                </div>

                <div className="table-wrap">
                  <table>
                    <thead>
                      <tr>
                        <th>Fecha</th>
                        <th>Cuenta</th>
                        <th>Tipo</th>
                        <th>Cantidad</th>
                        <th>Precio</th>
                        <th>Total</th>
                        <th>Estado</th>
                      </tr>
                    </thead>

                    <tbody>
                      {filteredTransactions.map(
                        (transaction) => {
                          const account = accountMap.get(
                            transaction.account_id,
                          );

                          return (
                            <tr key={transaction.id}>
                              <td>
                                {transaction.trade_date
                                  ? new Date(
                                      transaction.trade_date,
                                    ).toLocaleDateString(
                                      "es-MX",
                                    )
                                  : "—"}
                              </td>

                              <td>
                                {account?.name ??
                                  `Cuenta ${transaction.account_id}`}
                              </td>

                              <td>
                                {transaction.transaction_type}
                              </td>

                              <td>
                                {number(
                                  transaction.quantity,
                                )}
                              </td>

                              <td>
                                {money(
                                  transaction.unit_price,
                                  transaction.currency,
                                )}
                              </td>

                              <td>
                                {money(
                                  transaction.total_amount,
                                  transaction.currency,
                                )}
                              </td>

                              <td>
                                {transaction.status}
                              </td>
                            </tr>
                          );
                        },
                      )}

                      {filteredTransactions.length === 0 && (
                        <tr>
                          <td colSpan={7}>
                            No hay operaciones para los filtros
                            seleccionados.
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </section>
            </>
          )}
        </>
      )}
    </main>
  );
}

export default App;
