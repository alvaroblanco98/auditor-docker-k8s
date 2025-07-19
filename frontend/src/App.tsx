import React, { useState } from 'react';

function App() {
  const [file, setFile] = useState<File | null>(null);
  const [response, setResponse] = useState<any>(null);

  const handleUpload = async () => {
    if (!file) return;
    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch("http://localhost:8000/scan/", {
      method: "POST",
      body: formData
    });

    const data = await res.json();
    setResponse(data);
  };

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Auditor Docker/K8s</h1>
      <input type="file" onChange={e => setFile(e.target.files?.[0] || null)} />
      <button className="ml-4 bg-blue-600 text-white px-4 py-2 rounded" onClick={handleUpload}>
        Subir y analizar
      </button>
      {response && (
        <pre className="mt-6 bg-gray-100 p-4 rounded">{JSON.stringify(response, null, 2)}</pre>
      )}
    </div>
  );
}

export default App;

