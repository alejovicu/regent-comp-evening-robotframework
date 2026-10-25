import { useCallback, useState } from "react";

// A single status message area (#flash-message) used by every page, so tests
// always know where to look for success and error feedback. The message stays
// until the next action replaces it or the user closes it.
export function useFlash() {
  const [flash, setFlash] = useState(null);
  const show = useCallback((type, text) => setFlash({ type, text }), []);
  const clear = useCallback(() => setFlash(null), []);
  return [flash, show, clear];
}

export function Flash({ flash, onClose }) {
  if (!flash) return null;
  return (
    <div id="flash-message" role="status" className={`flash flash-${flash.type}`}
         data-type={flash.type}>
      <span id="flash-text">{flash.text}</span>
      {onClose && (
        <button id="flash-close" className="link" onClick={onClose} aria-label="Close">×</button>
      )}
    </div>
  );
}
