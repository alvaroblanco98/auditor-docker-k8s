import React, { useState } from "react";

function App() {
  const [file, setFile] = useState<File | null>(null);
  const [response, setResponse] = useState<any>(null);

  const handleUpload = async () => {
    if (!file) return;
    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch("http://localhost:8000/scan/", {
      method: "POST",
      body: formData,
    });

    const data = await res.json();
    setResponse(data);
  };

  return (
    <div className="p-4">
      <h1 className="text-xl font-bold">Auditor Docker / Kubernetes</h1>
      <input type="file" onChange={e => setFile(e.target.files?.[0] || null)} />
      <button onClick={handleUpload} className="bg-blue-500 text-white px-4 py-2 ml-2">Subir</button>
      {response && (
        <pre className="mt-4 bg-gray-100 p-4 rounded">{JSON.stringify(response, null, 2)}</pre>
      )}
    </div>
  );
}

export default App;
