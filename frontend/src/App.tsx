import React, { useEffect, useState } from 'react';
import ReactDiffViewer, { DiffMethod } from 'react-diff-viewer';

function App() {
  const [file, setFile] = useState<File | null>(null);
  const [response, setResponse] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [severityFilter, setSeverityFilter] = useState<string>("all");
  const [history, setHistory] = useState<any[]>([]);
  const [selectedEntry, setSelectedEntry] = useState<any | null>(null);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const res = await fetch("http://localhost:8000/history/");
      const data = await res.json();
      setHistory(data.history);
    } catch {
      console.error("No se pudo cargar el historial.");
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setLoading(true);
    setError(null);
    setResponse(null);
    setSelectedEntry(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch("http://localhost:8000/scan/", {
        method: "POST",
        body: formData
      });

      if (!res.ok) throw new Error("Error en el análisis");

      const data = await res.json();
      setResponse(data);
      fetchHistory();
    } catch (err) {
      setError("Error al subir el archivo. Por favor, inténtalo de nuevo.");
    } finally {
      setLoading(false);
    }
  };

  const dataToDisplay = response || selectedEntry;
  const findings = dataToDisplay?.normalized_findings || [];
  const filteredFindings = findings.filter((item: any) =>
    severityFilter === "all" ? true : item.severity?.toLowerCase() === severityFilter
  );

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Auditor Docker/K8s</h1>

      {loading && <p className="text-blue-600 mt-2">Analizando archivo...</p>}
      {error && <p className="text-red-600 mt-2">{error}</p>}
      {response && <p className="text-green-600 mt-2">Análisis completado correctamente</p>}

      {/* Formulario */}
      <div className="flex items-center gap-4 mt-4 mb-6">
        <input type="file" onChange={e => setFile(e.target.files?.[0] || null)} />
        <button
          className={`bg-blue-600 text-white px-4 py-2 rounded ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
          onClick={handleUpload}
          disabled={loading}
        >
          {loading ? "Analizando..." : "Subir y analizar"}
        </button>
        {file && <span className="text-sm text-gray-600">{file.name}</span>}
      </div>

      {/* Historial */}
      <div className="mb-8">
        <h2 className="text-md font-semibold mb-2">Historial de análisis anteriores</h2>
        {history.length === 0 ? (
          <p className="text-gray-500 italic">No hay análisis guardados.</p>
        ) : (
          <ul className="list-disc pl-5 space-y-1">
            {history.map((entry) => (
              <li key={entry.id}>
                <button
                  onClick={() => {
                    setSelectedEntry(entry);
                    setResponse(null);
                  }}
                  className="text-blue-600 hover:underline text-sm"
                >
                  {new Date(entry.timestamp).toLocaleDateString()} — {entry.filename}
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* Resultados de análisis */}
      {dataToDisplay && (
        <div className="mt-6">
          <h2 className="text-lg font-semibold mb-4">Archivo: {dataToDisplay.filename}</h2>

          {dataToDisplay.suggested_content && (
            <div className="mb-8">
              <h3 className="text-md font-semibold mb-2">Diferencias entre configuración original y sugerida</h3>
              <div className="border rounded shadow overflow-auto">
                <ReactDiffViewer
                  oldValue={dataToDisplay.original_content}
                  newValue={dataToDisplay.suggested_content}
                  splitView={true}
                  compareMethod={DiffMethod.LINES}
                  showDiffOnly={false}
                  leftTitle="Original"
                  rightTitle="Sugerido"
                />
              </div>
              <a
                href={`data:text/plain;charset=utf-8,${encodeURIComponent(dataToDisplay.suggested_content)}`}
                download={`remediado-${dataToDisplay.filename}`}
                className="inline-block bg-green-600 text-white px-4 py-2 rounded mt-4"
              >
                Descargar versión remediada
              </a>
            </div>
          )}

          <div className="mb-6">
            <h3 className="text-md font-semibold mb-2">Vulnerabilidades detectadas</h3>

            {/* Filtro de severidad */}
            <div className="mb-4">
              <label className="text-sm font-medium text-gray-700 mr-2">Filtrar por severidad:</label>
              <select
                value={severityFilter}
                onChange={e => setSeverityFilter(e.target.value)}
                className="border rounded px-2 py-1 text-sm"
              >
                <option value="all">Todas</option>
                <option value="critical">Critical</option>
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
                <option value="unknown">Unknown</option>
              </select>
            </div>

            {filteredFindings.length === 0 ? (
              <p className="text-gray-500 italic">No se encontraron problemas con esta severidad.</p>
            ) : (
              <div className="overflow-auto">
                <table className="min-w-full text-sm border border-gray-300 rounded">
                  <thead className="bg-gray-100 sticky top-0">
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
                    {filteredFindings.map((item: any, i: number) => (
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