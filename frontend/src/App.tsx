import React, { useEffect, useState } from 'react';
import ReactDiffViewer, { DiffMethod } from 'react-diff-viewer';
import { AiOutlineLoading3Quarters, AiOutlineCheckCircle, AiOutlineCloseCircle } from 'react-icons/ai';

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
      <div className="min-h-screen bg-gray-50 font-sans text-gray-800 px-4 py-6">
        <header className="mb-6 border-b pb-4 flex items-center justify-between">
          <h1 className="text-3xl font-bold text-blue-700 flex items-center gap-2">
            Docker & Kubernetes Auditor
          </h1>
        </header>

        <div className="max-w-6xl mx-auto space-y-8">

          {/* Estado del análisis */}
          {loading && (
            <div className="flex items-center text-blue-600 gap-2">
              <AiOutlineLoading3Quarters className="animate-spin" />
              <span>Analizando archivo...</span>
            </div>
          )}
          {error && (
            <div className="flex items-center text-red-600 gap-2">
              <AiOutlineCloseCircle />
              <span>{error}</span>
            </div>
          )}
          {response && (
            <div className="flex items-center text-green-600 gap-2">
              <AiOutlineCheckCircle />
              <span>Análisis completado correctamente</span>
            </div>
          )}

          {/* Subida de archivo */}
          <section className="bg-white p-6 rounded shadow">
            <h2 className="text-xl font-semibold mb-4">Subir nuevo archivo</h2>
            <div className="flex items-center gap-4">
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
          </section>

          {/* Historial */}
          <section className="bg-white p-6 rounded shadow">
            <h2 className="text-xl font-semibold mb-4">Historial de análisis anteriores</h2>
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
          </section>

          {/* Resultados */}
          {dataToDisplay && (
            <section className="bg-white p-6 rounded shadow">
              <h2 className="text-xl font-semibold mb-4">Resultados del análisis</h2>
              <h3 className="font-medium text-gray-700 mb-2">Archivo: {dataToDisplay.filename}</h3>

              {dataToDisplay.suggested_content && (
                <div className="mb-8">
                  <h4 className="text-md font-semibold mb-2">Comparativa original vs sugerido</h4>
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
                  <div className="mt-4 space-x-4">
                    <a
                      href={`data:text/plain;charset=utf-8,${encodeURIComponent(dataToDisplay.suggested_content)}`}
                      download={`remediado-${dataToDisplay.filename}`}
                      className="inline-block bg-green-600 text-white px-4 py-2 rounded"
                    >
                      Descargar versión remediada
                    </a>
                    <a
                      href={`data:application/json;charset=utf-8,${encodeURIComponent(JSON.stringify(dataToDisplay, null, 2))}`}
                      download={`analisis-${dataToDisplay.filename}.json`}
                      className="inline-block bg-blue-600 text-white px-4 py-2 rounded"
                    >
                      Exportar análisis (.json)
                    </a>
                  </div>
                </div>
              )}

              {/* Filtro */}
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

              {/* Tabla */}
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
                        <tr key={i} className="border-b hover:bg-gray-50">
                          <td className="p-2 align-top">{item.tool}</td>
                          <td className="p-2 align-top">{item.file}</td>
                          <td className="p-2 align-top">{item.line ?? "-"}</td>
                          <td className="p-2 align-top">{item.rule}</td>
                          <td className={`p-2 align-top font-bold text-sm`}>
                            <span className={`inline-block px-2 py-1 rounded text-white
                              ${item.severity?.toLowerCase() === 'critical' ? 'bg-red-600' :
                                item.severity?.toLowerCase() === 'high' ? 'bg-orange-500' :
                                item.severity?.toLowerCase() === 'medium' ? 'bg-yellow-500' :
                                item.severity?.toLowerCase() === 'low' ? 'bg-green-500' :
                                'bg-gray-400'
                              }`}>
                              {item.severity}
                            </span>
                          </td>
                          <td className="p-2 align-top whitespace-pre-wrap">{item.message}</td>
                          <td className="p-2 align-top">{item.fix ?? "-"}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </section>
          )}
        </div>
      </div>
    );
  }

export default App;