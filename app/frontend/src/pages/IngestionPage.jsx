import { useCallback, useEffect, useState } from "react";
import { api } from "../api.js";
import { Flash, useFlash } from "../flash.jsx";

export default function IngestionPage() {
  const [files, setFiles] = useState([]);
  const [filename, setFilename] = useState("catalog.csv");
  const [replace, setReplace] = useState(false);
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [busy, setBusy] = useState(false);
  const [flash, showFlash, clearFlash] = useFlash();

  const loadFiles = useCallback(async () => {
    try {
      const list = await api("/admin/sftp/files");
      setFiles(list);
      if (list.length && !list.some((f) => f.filename === filename)) setFilename(list[0].filename);
    } catch (e) {
      showFlash("error", e.message);
    }
  }, [filename, showFlash]);

  const loadHistory = useCallback(
    () => api("/admin/ingestions").then(setHistory).catch(() => {}),
    []
  );

  useEffect(() => { loadFiles(); loadHistory(); }, []);

  async function ingest() {
    setBusy(true);
    setResult(null);
    try {
      const res = await api("/admin/ingest", { method: "POST", body: { filename, replace } });
      setResult(res);
      showFlash(res.errors.length ? "warning" : "success",
        `Ingested ${res.filename}: ${res.created} created, ${res.updated} updated, ${res.deleted} deleted, ${res.errors.length} rejected`);
      loadHistory();
    } catch (e) {
      showFlash("error", e.message);
    } finally {
      setBusy(false);
    }
  }

  async function resetDemo() {
    try {
      await api("/admin/reset", { method: "POST" });
      setResult(null);
      showFlash("success", "Demo data reset to the sample catalog");
      loadHistory();
    } catch (e) {
      showFlash("error", e.message);
    }
  }

  return (
    <section>
      <h1 id="page-title">SFTP catalog ingestion</h1>
      <Flash flash={flash} onClose={clearFlash} />
      <div className="card">
        <p className="muted">
          Upload a CSV with columns <code>sku,name,price,description</code> to the SFTP
          {" "}<code>upload</code> folder, then import it here.
        </p>
        <div className="form-row">
          <label htmlFor="ingest-file">File on SFTP server</label>
          <select id="ingest-file" value={filename} onChange={(e) => setFilename(e.target.value)}>
            {files.length === 0 && <option value={filename}>{filename}</option>}
            {files.map((f) => (
              <option key={f.filename} value={f.filename}>{f.filename} ({f.size} bytes)</option>
            ))}
          </select>
          <button id="refresh-files" className="secondary" onClick={loadFiles}>Refresh list</button>
        </div>
        <label className="checkbox">
          <input id="ingest-replace" type="checkbox" checked={replace}
                 onChange={(e) => setReplace(e.target.checked)} />
          Replace catalog (remove products that are not in the file)
        </label>
        <div className="actions">
          <button id="ingest-button" onClick={ingest} disabled={busy}>
            {busy ? "Importing…" : "Import catalog"}
          </button>
          <button id="reset-demo-button" className="secondary" onClick={resetDemo}>Reset demo data</button>
        </div>
      </div>

      {result && (
        <div id="ingest-result" className="card">
          <h2>Result for {result.filename}</h2>
          <ul className="stats">
            <li>Created: <strong id="ingest-created">{result.created}</strong></li>
            <li>Updated: <strong id="ingest-updated">{result.updated}</strong></li>
            <li>Deleted: <strong id="ingest-deleted">{result.deleted}</strong></li>
            <li>Rejected: <strong id="ingest-rejected">{result.errors.length}</strong></li>
          </ul>
          {result.errors.length > 0 && (
            <ul id="ingest-errors" className="errors">
              {result.errors.map((err) => (
                <li key={err.line} id={`ingest-error-line-${err.line}`}>Line {err.line}: {err.error}</li>
              ))}
            </ul>
          )}
        </div>
      )}

      <h2>History</h2>
      {history.length === 0 ? (
        <p id="history-empty" className="empty">No imports yet.</p>
      ) : (
        <table id="ingestion-history">
          <thead><tr><th>When</th><th>By</th><th>File</th><th>Created</th><th>Updated</th><th>Deleted</th><th>Rejected</th></tr></thead>
          <tbody>
            {history.map((h, i) => (
              <tr key={i}>
                <td>{new Date(h.at).toLocaleString()}</td><td>{h.by}</td><td>{h.filename}</td>
                <td>{h.created}</td><td>{h.updated}</td><td>{h.deleted}</td><td>{h.errors.length}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  );
}
