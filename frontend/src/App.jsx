import { useEffect, useState } from "react";
import Plotly from "plotly.js-dist-min";
import createPlotlyComponent from "react-plotly.js/factory";
import { API_URL } from "./config";

const Plot = createPlotlyComponent(Plotly);

function App() {
  const [tickers, setTickers] = useState([]);
  const [ticker, setTicker] = useState("AAPL");
  const [rows, setRows] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch(`${API_URL}/tickers`)
      .then((res) => res.json())
      .then(setTickers)
      .catch((err) => setError(err.message));
  }, []);

  useEffect(() => {
    setError(null);
    fetch(`${API_URL}/prices/${ticker}?limit=5000`)
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then(setRows)
      .catch((err) => {
        setRows([]);
        setError(err.message);
      });
  }, [ticker]);

  const last = rows[rows.length - 1];

  return (
    <div>
      <h1>Market Intelligence</h1>

      <select value={ticker} onChange={(e) => setTicker(e.target.value)}>
        {tickers.map((t) => (
          <option key={t} value={t}>
            {t}
          </option>
        ))}
      </select>

      {error && <p>error: {error}</p>}
      {last && (
        <p>
          {rows.length} rows, last point {last.date}, close {last.close.toFixed(2)}
        </p>
      )}

      <Plot
        data={[
          {
            x: rows.map((r) => r.date),
            y: rows.map((r) => r.close),
            type: "scatter",
            mode: "lines",
            name: ticker,
          },
        ]}
        layout={{
          title: { text: `${ticker} close` },
          xaxis: { title: { text: "Date" } },
          yaxis: { title: { text: "Close (USD)" } },
          autosize: true,
        }}
        useResizeHandler
        style={{ width: "100%", height: "420px" }}
      />
    </div>
  );
}

export default App;