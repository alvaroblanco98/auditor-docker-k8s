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
            <h3 className="text-md font-semibold mb-2">Comparación: original vs sugerido</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <h4 className="font-semibold text-sm text-gray-700 mb-1">Original</h4>
                <pre className="bg-gray-100 p-4 rounded text-sm whitespace-pre-wrap overflow-auto max-h-96">
                  {response.original_content}
                </pre>
              </div>
              <div>
                <h4 className="font-semibold text-sm text-gray-700 mb-1">Sugerido</h4>
                <pre className="bg-green-50 p-4 rounded text-sm whitespace-pre-wrap overflow-auto max-h-96 border border-green-300">
                  {response.suggested_content || "No se han generado sugerencias."}
                </pre>
              </div>
            </div>
          </div>

          <div className="mb-6">
            <h3 className="text-md font-semibold">Vulnerabilidades detectadas</h3>

            {response.normalized_findings.length === 0 ? (
              <p className="text-gray-500 italic">No se encontraron problemas.</p>
            ) : (
              <div className="overflow-auto">
                <table className="min-w-full text-sm border border-gray-300 rounded">
                  <thead className="bg-gray-100">
                    <tr>
                      <th className="p-2 border-b">Tool</th>
                      <th className="p-2 border-b">File</th>
                      <th className="p-2 border-b">Line</th>
                      <th className="p-2 border-b">Rule / CVE</th>
                      <th className="p-2 border-b">Severity</th>
                      <th className="p-2 border-b">Message</th>
                      <th className="p-2 border-b">Fix</th>
                    </tr>
                  </thead>
                  <tbody>
                    {response.normalized_findings.map((item: any, i: number) => (
                      <tr key={i} className="border-b">
                        <td className="p-2 align-top">{item.tool}</td>
                        <td className="p-2 align-top">{item.file}</td>
                        <td className="p-2 align-top">{item.line ?? "-"}</td>
                        <td className="p-2 align-top">{item.rule}</td>
                        <td
                          className={`p-2 align-top font-bold ${
                            item.severity?.toLowerCase() === 'critical'
                              ? 'text-red-600'
                              : item.severity?.toLowerCase() === 'high'
                              ? 'text-orange-600'
                              : item.severity?.toLowerCase() === 'medium'
                              ? 'text-yellow-600'
                              : item.severity?.toLowerCase() === 'low'
                              ? 'text-green-600'
                              : 'text-gray-700'
                          }`}
                        >
                          {item.severity}
                        </td>
                        <td className="p-2 align-top whitespace-pre-wrap">{item.message}</td>
                        <td className="p-2 align-top">{item.fix ?? "-"}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
