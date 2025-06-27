import { useEffect, useState } from 'react';

export default function App() {
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    fetch('/LOGS')
      .then(r => r.text())
      .then(t => setLogs(t.split('\n').slice(-20)));
  }, []);

  return (
    <div className="p-4">
      <h1 className="text-xl font-bold mb-2">OpenOperator Dashboard</h1>
      <ul className="text-sm bg-gray-100 p-2 rounded">
        {logs.map((l, i) => <li key={i}>{l}</li>)}
      </ul>
    </div>
  );
}
