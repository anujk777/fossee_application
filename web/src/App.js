import React, { useMemo, useState } from 'react';
import axios from 'axios';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Line, Bar, Pie } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

const API_BASE = 'http://127.0.0.1:8000/api';

function App() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [token, setToken] = useState('');
  const [file, setFile] = useState(null);
  const [summary, setSummary] = useState(null);
  const [rawRows, setRawRows] = useState([]);
  const [history, setHistory] = useState([]);

  const parsedRows = useMemo(() => {
    if (!rawRows.length) return [];
    return rawRows;
  }, [rawRows]);

  const login = async () => {
    const response = await axios.post(`${API_BASE}/auth/token/`, { username, password });
    setToken(response.data.token);
  };

  const handleUpload = async () => {
    if (!file || !token) return;
    const formData = new FormData();
    formData.append('file', file);

    const uploadResponse = await axios.post(`${API_BASE}/upload/`, formData, {
      headers: { Authorization: `Token ${token}` },
    });
    setSummary(uploadResponse.data.summary);

    const text = await file.text();
    const lines = text.trim().split('\n');
    const header = lines[0].split(',');
    const rows = lines.slice(1).map((line) => {
      const cols = line.split(',');
      const row = {};
      header.forEach((h, idx) => {
        row[h] = cols[idx];
      });
      return row;
    });
    setRawRows(rows);
  };

  const fetchHistory = async () => {
    if (!token) return;
    const response = await axios.get(`${API_BASE}/history/`, {
      headers: { Authorization: `Token ${token}` },
    });
    setHistory(response.data);
  };

  const downloadPdf = () => {
    if (!token) return;
    window.open(`${API_BASE}/report/pdf/`, '_blank');
  };

  const lineData = {
    labels: parsedRows.map((r) => r['Session ID']),
    datasets: [
      {
        label: 'Wind Speed (km/h)',
        data: parsedRows.map((r) => Number(r['Wind Speed (km/h)'])),
        borderColor: '#1976d2',
      },
    ],
  };

  const barData = {
    labels: parsedRows.map((r) => r['Session ID']),
    datasets: [
      {
        label: 'Distance Covered (km)',
        data: parsedRows.map((r) => Number(r['Distance Covered (km)'])),
        backgroundColor: '#2e7d32',
      },
    ],
  };

  const boardCountMap = parsedRows.reduce((acc, row) => {
    acc[row['Board Type']] = (acc[row['Board Type']] || 0) + 1;
    return acc;
  }, {});

  const pieData = {
    labels: Object.keys(boardCountMap),
    datasets: [
      {
        data: Object.values(boardCountMap),
        backgroundColor: ['#ef5350', '#42a5f5', '#ffca28', '#8d6e63'],
      },
    ],
  };

  return (
    <div className="container">
      <h1>Windsurf Performance Parameter Visualizer</h1>

      <div className="card">
        <h2>Login</h2>
        <input value={username} onChange={(e) => setUsername(e.target.value)} placeholder="Username" />
        <input value={password} onChange={(e) => setPassword(e.target.value)} type="password" placeholder="Password" />
        <button onClick={login}>Login</button>
      </div>

      <div className="card">
        <h2>Upload CSV</h2>
        <input type="file" accept=".csv" onChange={(e) => setFile(e.target.files[0])} />
        <button onClick={handleUpload}>Upload</button>
        <button onClick={fetchHistory}>Refresh History</button>
        <button onClick={downloadPdf}>Download PDF</button>
      </div>

      {summary && (
        <div className="card">
          <h2>Summary</h2>
          <pre>{JSON.stringify(summary, null, 2)}</pre>
        </div>
      )}

      {parsedRows.length > 0 && (
        <div className="card charts">
          <Line data={lineData} />
          <Bar data={barData} />
          <Pie data={pieData} />
        </div>
      )}

      <div className="card">
        <h2>Last 5 Uploads</h2>
        <pre>{JSON.stringify(history, null, 2)}</pre>
      </div>
    </div>
  );
}

export default App;
