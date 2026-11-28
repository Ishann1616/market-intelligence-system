import { useEffect, useState } from "react";
import { API_URL } from "./config";

const STRATEGIES = [
  "Manager",
  "Static 50/50",
  "Momentum",
  "Mean-Reversion",
  "Buy & Hold",
];

function ResultsSummary() {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch(`${API_URL}/results/summary`)
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then(setData)
      .catch((err) => setError(err.message));
  }, []);

  if (error) return <p>results error: {error}</p>;
  if (!data) return <p>loading results...</p>;

  const avg = data.average_sharpe;
  const bh = data.bootstrap_counts["Buy & Hold"];
  const st = data.bootstrap_counts["Static 50/50"];

  return (
    <div>
      <h2>Result: the manager did not beat its benchmarks</h2>
      <p>
        Average Sharpe over 6 tickers (lookback {data.lookback}): Buy & Hold{" "}
        {avg["Buy & Hold"].toFixed(3)}, Static 50/50{" "}
        {avg["Static 50/50"].toFixed(3)}, Manager {avg["Manager"].toFixed(3)}.
        The pre-registered success criterion was{" "}
        {data.success_criterion_met ? "met" : "not met"}.
      </p>
      <p>
        Manager vs Buy & Hold: worse on {bh.manager_worse}/6, significant on{" "}
        {bh.significant}. Manager vs Static 50/50: worse on {st.manager_worse}
        /6, better on {st.manager_better}, significant on {st.significant}.
      </p>

      <h3>Sharpe ratio by ticker</h3>
      <table>
        <thead>
          <tr>
            <th>Ticker</th>
            {STRATEGIES.map((s) => (
              <th key={s}>{s}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.sharpe_by_ticker.map((row) => (
            <tr key={row.ticker}>
              <td>{row.ticker}</td>
              {STRATEGIES.map((s) => (
                <td key={s}>{row[s].toFixed(3)}</td>
              ))}
            </tr>
          ))}
          <tr>
            <td>
              <b>Average</b>
            </td>
            {STRATEGIES.map((s) => (
              <td key={s}>
                <b>{avg[s].toFixed(3)}</b>
              </td>
            ))}
          </tr>
        </tbody>
      </table>

      <h3>Bootstrap: Manager minus benchmark (Sharpe difference, 95% CI)</h3>
      <table>
        <thead>
          <tr>
            <th>Ticker</th>
            <th>Benchmark</th>
            <th>Diff</th>
            <th>95% CI</th>
            <th>Verdict</th>
          </tr>
        </thead>
        <tbody>
          {data.bootstrap_manager_vs.map((b) => (
            <tr key={`${b.ticker}-${b.vs}`}>
              <td>{b.ticker}</td>
              <td>{b.vs}</td>
              <td>{b.diff.toFixed(3)}</td>
              <td>
                ({b.ci_low.toFixed(2)}, {b.ci_high.toFixed(2)})
              </td>
              <td>{b.verdict}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <p>
        Caveats: 6 correlated mega-cap survivors, 10 years, bootstrap is per
        ticker while the pre-registered metric is the cross-ticker average.
      </p>
    </div>
  );
}

export default ResultsSummary;