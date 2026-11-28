import Plotly from "plotly.js-dist-min";
import createPlotlyComponent from "react-plotly.js/factory";
import { useEffect, useState } from "react";
import { API_URL } from "./config";

const Plot = createPlotlyComponent(Plotly);

const ORDER = [
  "Buy & Hold",
  "Momentum",
  "Mean-Reversion",
  "Static 50/50",
  "Manager",
];

function EquityChart({ ticker }) {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    setData(null);
    setError(null);
    fetch(`${API_URL}/backtest/${ticker}`)
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then(setData)
      .catch((err) => setError(err.message));
  }, [ticker]);

  if (error) return <p>equity curves error: {error}</p>;
  if (!data) return <p>loading equity curves...</p>;

  const finals = ORDER.map(
    (name) => `${name} ${data.curves[name][data.dates.length - 1].toFixed(2)}`
  );

  return (
    <div>
      <p>
        {data.dates.length} days, {data.dates[0]} to{" "}
        {data.dates[data.dates.length - 1]}. Final values: {finals.join(" | ")}
      </p>
      <Plot
        data={ORDER.map((name) => ({
          x: data.dates,
          y: data.curves[name],
          type: "scatter",
          mode: "lines",
          name,
        }))}
        layout={{
          title: { text: `${ticker}: $10,000 start, 5 strategies` },
          xaxis: { title: { text: "Date" } },
                    yaxis: {
            title: { text: "Portfolio value (USD)" },
            type: "log",
            tickvals: [5000, 10000, 20000, 50000, 100000, 200000, 500000],
            ticktext: ["5k", "10k", "20k", "50k", "100k", "200k", "500k"],
            minor: { showgrid: false },
          },
          autosize: true,
        }}
        useResizeHandler
        style={{ width: "100%", height: "460px" }}
      />
      <p>
        Note: final dollars and Sharpe can rank strategies differently. Sharpe
        adjusts for volatility, dollars do not. The y-axis is logarithmic, so
        equal vertical distances mean equal percentage changes.
      </p>
    </div>
  );
}

export default EquityChart;