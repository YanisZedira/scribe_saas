// Client API vers le backend FastAPI (proxifié par Vite sur /api).
let token = localStorage.getItem("scribe_token");
export const setToken = (t) => {
  token = t;
  t ? localStorage.setItem("scribe_token", t) : localStorage.removeItem("scribe_token");
};
export const isAuthed = () => !!token;

async function req(path, { method = "GET", body, form } = {}) {
  const headers = {};
  if (token) headers.Authorization = `Bearer ${token}`;
  let payload;
  if (form) payload = form;
  else if (body) { headers["Content-Type"] = "application/json"; payload = JSON.stringify(body); }
  const res = await fetch(path, { method, headers, body: payload });
  if (!res.ok) {
    let d; try { d = await res.json(); } catch { d = { detail: res.statusText }; }
    throw new Error(d.detail || "Erreur");
  }
  return res.status === 204 ? null : res.json();
}

export const api = {
  register: (email, password, full_name) =>
    req("/api/auth/register", { method: "POST", body: { email, password, full_name } }),
  login: async (email, password) => {
    const fd = new URLSearchParams();
    fd.set("username", email); fd.set("password", password);
    const res = await fetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: fd,
    });
    if (!res.ok) throw new Error("Identifiants incorrects");
    const { access_token } = await res.json();
    setToken(access_token);
  },
  me: () => req("/api/auth/me"),
  dashboard: () => req("/api/dashboard"),
  meetings: () => req("/api/meetings"),
  meeting: (id) => req(`/api/meetings/${id}`),
  createMeeting: (title, meeting_url) =>
    req("/api/meetings", { method: "POST", body: { title, meeting_url } }),
  finalize: (id) => req(`/api/meetings/${id}/finalize`, { method: "POST" }),
  remove: (id) => req(`/api/meetings/${id}`, { method: "DELETE" }),
};
