import { useState, useEffect } from "react";
import { api, setToken, isAuthed } from "./api";

const avatarColor = (s) => ["#10b981","#8b5cf6","#38bdf8","#f59e0b","#fb7185","#34d399"][(s||"?").charCodeAt(0)%6];
const toneIcon = (t) => ({positif:"😊","négatif":"😟",neutre:"😐",tendu:"😬",constructif:"🤝"}[t] || "💬");

export default function App() {
  const [authed, setAuthed] = useState(isAuthed());
  const [user, setUser] = useState(null);
  const [page, setPage] = useState("dashboard");
  const [arg, setArg] = useState(null);

  useEffect(() => { if (isAuthed()) api.me().then(setUser).catch(() => { setToken(null); setAuthed(false); }); }, []);

  if (!authed) return <Auth onDone={async () => { setUser(await api.me()); setAuthed(true); }} />;

  const go = (p, a = null) => { setArg(a); setPage(p); };
  return (
    <>
      <div className="glow" style={{ width: 460, height: 460, background: "#10b981", top: -160, left: -120 }} />
      <div className="glow" style={{ width: 420, height: 420, background: "#8b5cf6", bottom: -160, right: -100 }} />
      <div className="shell fade">
        <aside className="side">
          <div style={{ display: "flex", alignItems: "center", gap: 10, padding: "0 8px 24px" }}>
            <div style={{ width: 34, height: 34, borderRadius: 10, background: "linear-gradient(135deg,#10b981,#8b5cf6)", display: "grid", placeItems: "center", fontSize: 18 }}>🎙️</div>
            <b style={{ fontSize: 19 }}>Scribe</b>
          </div>
          <nav style={{ display: "flex", flexDirection: "column", gap: 4 }}>
            <a className={`nav ${page==="dashboard"?"active":""}`} onClick={() => go("dashboard")}>◳ Tableau de bord</a>
            <a className={`nav ${page==="new"?"active":""}`} onClick={() => go("new")}>＋ Nouvelle réunion</a>
            <a className={`nav ${page==="meetings"?"active":""}`} onClick={() => go("meetings")}>☰ Mes réunions</a>
          </nav>
          <div style={{ marginTop: "auto", fontSize: 13, color: "var(--faint)" }}>
            <div style={{ marginBottom: 8, overflow: "hidden", textOverflow: "ellipsis" }}>{user?.email}</div>
            <button className="btn btn-ghost" style={{ width: "100%", justifyContent: "center", padding: 8 }}
              onClick={() => { setToken(null); setAuthed(false); }}>Déconnexion</button>
          </div>
        </aside>
        <main className="main">
          {page === "dashboard" && <Dashboard go={go} />}
          {page === "new" && <NewMeeting go={go} />}
          {page === "meetings" && <Meetings go={go} />}
          {page === "meeting" && <MeetingDetail id={arg} go={go} />}
        </main>
      </div>
    </>
  );
}

function Auth({ onDone }) {
  const [mode, setMode] = useState("login");
  const [email, setEmail] = useState(""); const [pw, setPw] = useState(""); const [name, setName] = useState("");
  const [err, setErr] = useState("");
  const submit = async (e) => {
    e.preventDefault(); setErr("");
    try { if (mode === "reg") await api.register(email, pw, name); await api.login(email, pw); onDone(); }
    catch (x) { setErr(x.message); }
  };
  return (
    <div style={{ minHeight: "100vh", display: "grid", placeItems: "center", padding: 20 }}>
      <div className="glow" style={{ width: 460, height: 460, background: "#10b981", top: -160, left: -120 }} />
      <div className="glow" style={{ width: 420, height: 420, background: "#8b5cf6", bottom: -160, right: -100 }} />
      <div className="fade" style={{ width: "100%", maxWidth: 400, position: "relative", zIndex: 1 }}>
        <div style={{ textAlign: "center", marginBottom: 22 }}>
          <div style={{ fontSize: 40 }}>🎙️</div>
          <h1 style={{ fontSize: 28 }}>Scribe</h1>
          <p style={{ color: "var(--muted)", marginTop: 4 }}>Vos réunions Teams, <span className="grad">résumées automatiquement</span>.</p>
        </div>
        <div className="card" style={{ padding: 26 }}>
          <div style={{ display: "flex", gap: 8, background: "#0d1320", padding: 5, borderRadius: 12, marginBottom: 18 }}>
            <button className="btn" style={{ flex: 1, justifyContent: "center", background: mode==="login"?"#1c2740":"transparent" }} onClick={() => setMode("login")}>Connexion</button>
            <button className="btn" style={{ flex: 1, justifyContent: "center", background: mode==="reg"?"#1c2740":"transparent" }} onClick={() => setMode("reg")}>Inscription</button>
          </div>
          <form onSubmit={submit} style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            {mode === "reg" && <input className="input" placeholder="Nom complet" value={name} onChange={(e) => setName(e.target.value)} />}
            <input className="input" type="email" placeholder="vous@entreprise.fr" value={email} onChange={(e) => setEmail(e.target.value)} required />
            <input className="input" type="password" placeholder="Mot de passe" value={pw} onChange={(e) => setPw(e.target.value)} required />
            {err && <div style={{ color: "var(--rose)", fontSize: 13 }}>{err}</div>}
            <button className="btn btn-primary" style={{ justifyContent: "center" }}>{mode==="login"?"Se connecter →":"Créer mon compte →"}</button>
          </form>
        </div>
      </div>
    </div>
  );
}

function Dashboard({ go }) {
  const [s, setS] = useState(null);
  useEffect(() => { api.dashboard().then(setS).catch(() => {}); }, []);
  if (!s) return <Center><div className="spinner" /></Center>;
  const kpis = [["Réunions", s.total_meetings, "🗂️", "#10b981"], ["Analysées", s.analyzed, "✅", "#34d399"],
    ["Décisions", s.total_decisions, "📌", "#8b5cf6"], ["Actions", s.total_actions, "⚡", "#f59e0b"]];
  return (
    <div className="fade">
      <Header title="Tableau de bord" sub="Vue d'ensemble de vos réunions">
        <button className="btn btn-primary" onClick={() => go("new")}>＋ Nouvelle réunion</button>
      </Header>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(150px,1fr))", gap: 14, marginBottom: 22 }}>
        {kpis.map(([l, v, i, c]) => (
          <div className="kpi" key={l}><div style={{ fontSize: 22 }}>{i}</div>
            <div style={{ fontSize: 30, fontWeight: 800, marginTop: 6, color: c }}>{v}</div>
            <div style={{ color: "var(--muted)", fontSize: 13 }}>{l}</div></div>
        ))}
      </div>
      <div className="card" style={{ padding: 22, marginBottom: 18 }}>
        <h3 style={{ fontSize: 16, marginBottom: 14 }}>🏷️ Thèmes dominants</h3>
        {s.top_topics.length ? s.top_topics.map((t) => (
          <div key={t.label} style={{ marginBottom: 10 }}>
            <div style={{ display: "flex", justifyContent: "space-between", fontSize: 13, marginBottom: 4 }}><span>{t.label}</span><span style={{ color: "var(--faint)" }}>{t.count}</span></div>
            <div style={{ height: 7, background: "#0d1320", borderRadius: 6 }}><div style={{ height: "100%", width: `${Math.min(t.count * 25, 100)}%`, background: "#8b5cf6", borderRadius: 6 }} /></div>
          </div>
        )) : <span style={{ color: "var(--faint)" }}>Aucune donnée — créez une réunion.</span>}
      </div>
      <div className="card" style={{ padding: 22 }}>
        <h3 style={{ fontSize: 16, marginBottom: 12 }}>Réunions récentes</h3>
        {s.recent.length ? s.recent.map((m) => (
          <div className="row" key={m.id} style={{ background: "#0f1626", border: "1px solid var(--line)", marginBottom: 8, cursor: "pointer" }} onClick={() => go("meeting", m.id)}>
            <span>{m.title}</span><StatusChip status={m.status} />
          </div>
        )) : <span style={{ color: "var(--faint)" }}>—</span>}
      </div>
    </div>
  );
}

function NewMeeting({ go }) {
  const [title, setTitle] = useState(""); const [url, setUrl] = useState("");
  const [step, setStep] = useState("form"); const [err, setErr] = useState(""); const [mid, setMid] = useState(null);

  const create = async () => {
    setErr("");
    try { const m = await api.createMeeting(title || "Réunion Teams", url.trim()); setMid(m.id); setStep("joined"); }
    catch (e) { setErr(e.message); }
  };
  const finalize = async () => {
    setStep("processing");
    try { await api.finalize(mid); go("meeting", mid); }
    catch (e) { setErr(e.message); setStep("joined"); }
  };

  return (
    <div className="fade" style={{ maxWidth: 620 }}>
      <Header title="Nouvelle réunion" sub="Collez le lien de la réunion Teams" />
      {step === "form" && (
        <div className="card" style={{ padding: 24, display: "flex", flexDirection: "column", gap: 14 }}>
          <input className="input" placeholder="Titre (optionnel)" value={title} onChange={(e) => setTitle(e.target.value)} />
          <input className="input" placeholder="https://teams.live.com/meet/…  (ou Meet / Zoom)" value={url} onChange={(e) => setUrl(e.target.value)} />
          <p style={{ fontSize: 12.5, color: "var(--faint)" }}>🔒 Assurez-vous que les participants consentent à l'enregistrement. Un bot « Scribe » rejoindra la réunion et la transcrira.</p>
          {err && <div style={{ color: "var(--rose)", fontSize: 13 }}>{err}</div>}
          <button className="btn btn-primary" style={{ justifyContent: "center" }} disabled={!url.trim()} onClick={create}>Envoyer le bot →</button>
        </div>
      )}
      {step === "joined" && (
        <div className="card" style={{ padding: 30, textAlign: "center" }}>
          <div style={{ fontSize: 36 }}>🤖</div>
          <h3 style={{ margin: "10px 0 6px" }}>Le bot Scribe a rejoint la réunion</h3>
          <p style={{ color: "var(--muted)", marginBottom: 18, fontSize: 14 }}>Il transcrit en direct. Cliquez ci-dessous une fois la réunion terminée pour générer le compte-rendu.</p>
          {err && <div style={{ color: "var(--rose)", fontSize: 13, marginBottom: 10 }}>{err}</div>}
          <button className="btn btn-primary" style={{ margin: "0 auto" }} onClick={finalize}>Terminer & générer le compte-rendu</button>
        </div>
      )}
      {step === "processing" && <Center><div className="spinner" /><p style={{ color: "var(--muted)", marginTop: 14 }}>Récupération du transcript & analyse IA…</p></Center>}
    </div>
  );
}

function Meetings({ go }) {
  const [ms, setMs] = useState(null);
  useEffect(() => { api.meetings().then(setMs).catch(() => {}); }, []);
  if (!ms) return <Center><div className="spinner" /></Center>;
  return (
    <div className="fade">
      <Header title="Mes réunions" />
      {ms.length ? (
        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          {ms.map((m) => (
            <div className="card row" key={m.id} style={{ cursor: "pointer" }} onClick={() => go("meeting", m.id)}>
              <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
                <div style={{ width: 42, height: 42, borderRadius: 12, background: "#0f1626", display: "grid", placeItems: "center", fontSize: 20 }}>📹</div>
                <div><div style={{ fontWeight: 600 }}>{m.title}</div>
                  <div style={{ fontSize: 13, color: "var(--faint)", marginTop: 2 }}>{m.platform} · {new Date(m.created_at).toLocaleDateString("fr-FR")} {m.sentiment ? "· " + toneIcon(m.sentiment) + " " + m.sentiment : ""}</div></div>
              </div>
              <StatusChip status={m.status} />
            </div>
          ))}
        </div>
      ) : <div className="card" style={{ padding: 40, textAlign: "center", color: "var(--muted)" }}>Aucune réunion. <a style={{ color: "var(--brand2)" }} onClick={() => go("new")}>Créez la première</a>.</div>}
    </div>
  );
}

function MeetingDetail({ id, go }) {
  const [m, setM] = useState(null); const [tab, setTab] = useState("cr");
  useEffect(() => { api.meeting(id).then(setM).catch(() => {}); }, [id]);
  if (!m) return <Center><div className="spinner" /></Center>;
  const del = async () => { if (confirm("Supprimer cette réunion ?")) { await api.remove(id); go("meetings"); } };
  return (
    <div className="fade">
      <button className="btn btn-ghost" style={{ padding: "7px 13px", fontSize: 13, marginBottom: 14 }} onClick={() => go("meetings")}>← Mes réunions</button>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 14, marginBottom: 18 }}>
        <div><h1 style={{ fontSize: 24 }}>{m.title}</h1>
          <div style={{ color: "var(--muted)", marginTop: 6, fontSize: 14 }}>{m.platform} · {toneIcon(m.sentiment)} {m.sentiment || ""} {m.error ? "· ⚠️ " + m.error : ""}</div></div>
        <button className="btn btn-ghost" style={{ fontSize: 13, color: "var(--rose)" }} onClick={del}>🗑️ Supprimer</button>
      </div>
      <div style={{ display: "flex", gap: 6, background: "#0d1320", padding: 5, borderRadius: 12, width: "fit-content", marginBottom: 16 }}>
        {[["cr", "📝 Compte-rendu"], ["tr", "📜 Transcription"]].map(([k, l]) => (
          <button key={k} className="btn" style={{ background: tab===k?"#1c2740":"transparent", padding: "8px 14px" }} onClick={() => setTab(k)}>{l}</button>
        ))}
      </div>
      {tab === "cr" ? (
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          <Section title="Résumé">{m.summary || <Muted>Pas encore analysé.</Muted>}</Section>
          {!!m.decisions?.length && <Section title="📌 Décisions">{m.decisions.map((d, i) => <li key={i} style={{ marginLeft: 18, marginBottom: 4 }}>{d}</li>)}</Section>}
          {!!m.actions?.length && <Section title="⚡ Actions">{m.actions.map((a, i) => (
            <div key={i} style={{ padding: "8px 0", borderBottom: "1px solid #1b2438", fontSize: 14 }}><b>{a.responsable || "—"}</b> · {a.tache}{a.echeance ? <span style={{ color: "var(--faint)" }}> · {a.echeance}</span> : ""}</div>
          ))}</Section>}
          {!!m.key_points?.length && <Section title="🔑 Points clés">{m.key_points.map((p, i) => <li key={i} style={{ marginLeft: 18, marginBottom: 4 }}>{p}</li>)}</Section>}
          {!!m.topics?.length && <Section title="🏷️ Thèmes"><div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>{m.topics.map((t, i) => <span key={i} className="chip" style={{ color: "#a78bfa", background: "#8b5cf614", border: "1px solid #8b5cf633" }}>{t}</span>)}</div></Section>}
        </div>
      ) : (
        <div className="card" style={{ padding: 22, maxHeight: 560, overflowY: "auto" }}>
          {m.transcript ? m.transcript.split("\n").map((line, i) => {
            const [who, ...rest] = line.split(":"); const text = rest.join(":");
            return <div key={i} style={{ display: "flex", gap: 10, marginBottom: 10 }}>
              <span style={{ width: 30, height: 30, borderRadius: "50%", background: avatarColor(who), display: "grid", placeItems: "center", fontSize: 12, fontWeight: 700, color: "#04130d", flexShrink: 0 }}>{(who||"?").slice(0,2).toUpperCase()}</span>
              <div style={{ fontSize: 14 }}><b>{who}</b><br />{text}</div></div>;
          }) : <Muted>Aucune transcription.</Muted>}
        </div>
      )}
    </div>
  );
}

// ─── Petits composants ───────────────────────────────────────────────────
const Center = ({ children }) => <div style={{ display: "grid", placeItems: "center", padding: 60 }}>{children}</div>;
const Muted = ({ children }) => <span style={{ color: "var(--faint)" }}>{children}</span>;
const Header = ({ title, sub, children }) => (
  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24 }}>
    <div><h1 style={{ fontSize: 26 }}>{title}</h1>{sub && <p style={{ color: "var(--muted)", marginTop: 4, fontSize: 14 }}>{sub}</p>}</div>
    {children}
  </div>
);
const Section = ({ title, children }) => (
  <div className="card" style={{ padding: 22 }}><h3 style={{ fontSize: 15, marginBottom: 10 }}>{title}</h3><div style={{ fontSize: 14.5, lineHeight: 1.6 }}>{children}</div></div>
);
function StatusChip({ status }) {
  const map = { done: ["Terminé", "#10b981"], failed: ["Échec", "#fb7185"], recording: ["En cours", "#f59e0b"], analyzing: ["Analyse", "#38bdf8"], joining: ["Connexion", "#8b5cf6"] };
  const [label, c] = map[status] || [status, "#64718c"];
  return <span className="chip" style={{ color: c, background: c + "14", border: `1px solid ${c}33` }}>● {label}</span>;
}
