// Thin fetch wrapper. All calls go to /api, which nginx (or the Vite dev server)
// forwards to the FastAPI backend.
const TOKEN_KEY = "shopcart_token";

export const getToken = () => localStorage.getItem(TOKEN_KEY);
export const setToken = (t) =>
  t ? localStorage.setItem(TOKEN_KEY, t) : localStorage.removeItem(TOKEN_KEY);

export async function api(path, { method = "GET", body } = {}) {
  const headers = { "Content-Type": "application/json" };
  const token = getToken();
  if (token) headers.Authorization = `Bearer ${token}`;
  const res = await fetch(`/api${path}`, {
    method,
    headers,
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  if (res.status === 204) return null;
  const data = await res.json().catch(() => null);
  if (!res.ok) {
    if (res.status === 401 && path !== "/auth/login") {
      setToken(null);
      window.location.assign("/login");
    }
    throw new Error(formatError(data) || `Request failed (${res.status})`);
  }
  return data;
}

function formatError(data) {
  if (!data || !data.detail) return null;
  if (typeof data.detail === "string") return data.detail;
  // FastAPI validation errors: [{loc: [...], msg: "..."}]
  return data.detail
    .map((d) => `${d.loc[d.loc.length - 1]}: ${d.msg}`)
    .join("; ");
}

export const money = (n) => `$${Number(n).toFixed(2)}`;
