import { useEffect, useState } from "react";
import { API_URL } from "./config";

function App() {
  const [status, setStatus] = useState("loading...");

  useEffect(() => {
    fetch(`${API_URL}/health`)
      .then((res) => res.json())
      .then((data) => setStatus(data.status))
      .catch((err) => setStatus(`error: ${err.message}`));
  }, []);

  return (
    <div>
      <h1>Market Intelligence</h1>
      <p>API status: {status}</p>
    </div>
  );
}

export default App;