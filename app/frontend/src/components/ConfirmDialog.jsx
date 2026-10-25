// A plain in-page dialog instead of window.confirm, so tests can click it like any button.
export default function ConfirmDialog({ message, onConfirm, onCancel }) {
  return (
    <div className="modal-backdrop">
      <div id="confirm-dialog" className="card modal" role="dialog">
        <p id="confirm-message">{message}</p>
        <div className="actions">
          <button id="confirm-no" className="secondary" onClick={onCancel}>Cancel</button>
          <button id="confirm-yes" className="danger" onClick={onConfirm}>Yes, delete</button>
        </div>
      </div>
    </div>
  );
}
