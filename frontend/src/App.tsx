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
      <button
        className="ml-4 bg-blue-600 text-white px-4 py-2 rounded"
        onClick={handleUpload}
      >
        Subir y analizar
      </button>

      {response && (
        <div className="mt-6">
          <h2 className="text-lg font-semibold mb-2">Archivo: {response.filename}</h2>

          <div className="mb-6">
            <h3 className="text-md font-semibold">Contenido original</h3>
            <pre className="bg-gray-100 p-4 rounded text-sm whitespace-pre-wrap overflow-auto max-h-64">
              {response.original_content}
            </pre>
          </div>

          {Object.entries(response.results).map(([tool, findings]) => (
            <div key={tool} className="mb-8">
              <h3 className="text-xl font-bold mb-2">{tool.toUpperCase()}</h3>

              {Array.isArray(findings) && findings.length > 0 ? (
                <div className="overflow-auto">
                  <table className="min-w-full text-sm border border-gray-300 rounded">
                    <thead className="bg-gray-100">
                      <tr>
                        {Object.keys(findings[0]).map((col) => (
                          <th key={col} className="text-left p-2 border-b border-gray-300">
                            {col}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {findings.map((item, index) => (
                        <tr key={index} className="border-b">
                          {Object.values(item).map((val, i) => (
                            <td key={i} className="p-2 align-top whitespace-pre-wrap">
                              {typeof val === "string" ? val : JSON.stringify(val)}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <p className="text-gray-500 italic">No se encontraron problemas.</p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default App;
