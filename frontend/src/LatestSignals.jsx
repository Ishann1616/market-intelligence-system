import { useEffect, useState } from "react";
import { API_URL } from "./config";

function LatestSignals() {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch(`${API_URL}/signals/latest`)
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then(setData)
      .catch((err) => setError(err.message));
  }, []);

  if (error) return <p>signals error: {error}</p>;
  if (!data) return <p>loading signals...</p>;

  const t = data.totals;

  return (
    <div>
      <h2>Latest forward signals: {data.signal_date}</h2>
      <p>
        Log totals: {t.rows} rows, {t.dates_logged} dates, {t.live_rows} live,{" "}
        {t.late_rows} late. "Live" means the row was logged before the close of
        the next trading day, when the trade would execute. "Late" rows are
        excluded from forward-test results.
      </p>
      <table>
        <thead>
          <tr>
            <th>Ticker</th>
            <th>Agent</th>
            <th>Signal</th>
            <th>Confidence</th>
            <th>Close</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {data.rows.map((r) => (
            <tr key={`${r.ticker}-${r.agent}`}>
              <td>{r.ticker}</td>
              <td>{r.agent}</td>
              <td>{r.signal}</td>
              <td>{r.confidence === null ? "n/a" : r.confidence.toFixed(4)}</td>
              <td>{r.close === null ? "n/a" : r.close.toFixed(2)}</td>
              <td>{r.status.toUpperCase()}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <p>
        Confidence for mean-reversion measures how extreme RSI is, not how
        bullish the stock is.
      </p>
    </div>
  );
}

export default LatestSignals;