"use client";
/** Page orchestratrice (App Router) : auth → dashboard → création → rapport.
 *  État applicatif léger en mémoire ; les données viennent du backend FastAPI.
 */
import * as React from "react";
import { Mic, Video, Users, LogOut } from "lucide-react";
import { api, getToken, setToken, type Meeting } from "@/lib/api";
import { Card, Button, Input } from "@/components/ui/primitives";
import { Recorder } from "@/components/Recorder";
import { ReportView } from "@/components/ReportView";
import { MeetingDashboard } from "@/components/MeetingDashboard";
import { MeetingRoom } from "@/components/MeetingRoom";

type Screen = { name: "dashboard" } | { name: "new" } | { name: "meeting"; id: string };

export default function Page() {
  const [authed, setAuthed] = React.useState(false);
  const [user, setUser] = React.useState<any>(null);
  const [meetings, setMeetings] = React.useState<Meeting[]>([]);
  const [screen, setScreen] = React.useState<Screen>({ name: "dashboard" });
  const [current, setCurrent] = React.useState<Meeting | null>(null);

  React.useEffect(() => { if (getToken()) bootstrap(); }, []);
  const bootstrap = async () => { try { setUser(await api.me()); setAuthed(true); refresh(); } catch { setToken(null); } };
  const refresh = async () => setMeetings(await api.meetings());
  const open = async (id: string) => { setCurrent(await api.meeting(id)); setScreen({ name: "meeting", id }); };
  const reloadCurrent = async () => { if (current) setCurrent(await api.meeting(current.id)); refresh(); };

  if (!authed) return <Auth onAuthed={bootstrap} />;

  return (
    <div className="grid grid-cols-[248px_1fr] min-h-screen">
      <aside className="glass border-r border-border p-5 sticky top-0 h-screen flex flex-col">
        <div className="flex items-center gap-2.5 px-2 pb-7">
          <div className="grid place-items-center w-9 h-9 rounded-xl bg-gradient-to-br from-brand to-violet text-lg">🎙️</div>
          <span className="text-lg font-extrabold">Scribe</span>
        </div>
        <nav className="space-y-1">
          <NavItem active={screen.name === "dashboard"} onClick={() => setScreen({ name: "dashboard" })}>◳ Tableau de bord</NavItem>
          <NavItem active={screen.name === "new"} onClick={() => setScreen({ name: "new" })}>✛ Nouvelle réunion</NavItem>
        </nav>
        <div className="mt-auto">
          <div className="text-xs text-muted-foreground px-2 mb-2 truncate">{user?.email}</div>
          <Button variant="ghost" className="w-full text-rose-400" onClick={() => { setToken(null); setAuthed(false); }}><LogOut size={15} /> Déconnexion</Button>
        </div>
      </aside>

      <main className="p-6 md:p-10 max-w-5xl w-full mx-auto">
        {screen.name === "dashboard" && <MeetingDashboard meetings={meetings} onOpen={open} onNew={() => setScreen({ name: "new" })} />}
        {screen.name === "new" && <NewMeeting onCreated={open} />}
        {screen.name === "meeting" && current && (
          <ReportView meeting={current} reload={reloadCurrent}
            onDelete={async () => { await api.deleteMeeting(current.id); await refresh(); setScreen({ name: "dashboard" }); }} />
        )}
      </main>
    </div>
  );
}

function NavItem({ active, onClick, children }: { active?: boolean; onClick: () => void; children: React.ReactNode }) {
  return <button onClick={onClick} className={`block w-full text-left px-3.5 py-2.5 rounded-xl text-sm font-semibold transition ${active ? "bg-gradient-to-r from-brand/20 to-violet/10 text-white border border-[#1f3b52]" : "text-muted-foreground hover:bg-muted/40"}`}>{children}</button>;
}

/* ---- Création de réunion (avec consentement RGPD) ---- */
type Mode = "dictaphone" | "visio" | "livekit";
function NewMeeting({ onCreated }: { onCreated: (id: string) => void }) {
  const [title, setTitle] = React.useState("");
  const [mode, setMode] = React.useState<Mode>("dictaphone");
  const [url, setUrl] = React.useState("");
  const [consent, setConsent] = React.useState(false);
  const [meeting, setMeeting] = React.useState<Meeting | null>(null);
  const [err, setErr] = React.useState("");

  const create = async () => {
    setErr("");
    try {
      const m = await api.createMeeting({
        title: title || "Réunion sans titre", mode, consent_obtained: true,
        meeting_url: mode === "visio" ? url.trim() : undefined,
      });
      setMeeting(m);
    } catch (e: any) { setErr(e.message); }
  };

  if (meeting && mode === "dictaphone") return <div className="max-w-2xl"><h1 className="text-2xl font-bold mb-5">🎤 {meeting.title}</h1><Recorder meetingId={meeting.id} onDone={() => onCreated(meeting.id)} /></div>;
  if (meeting && mode === "visio") return <VisioRoom meeting={meeting} onDone={() => onCreated(meeting.id)} />;
  if (meeting && mode === "livekit") return <MeetingRoom meeting={meeting} onEnded={() => onCreated(meeting.id)} />;

  const modes: [Mode, any, string, string][] = [
    ["dictaphone", Mic, "Dictaphone", "Présentiel — micro"],
    ["livekit", Users, "Salle Scribe", "Notre visio (LiveKit)"],
    ["visio", Video, "Bot externe", "Teams · Meet · Zoom"],
  ];

  return (
    <div className="max-w-2xl animate-fade-up">
      <h1 className="text-2xl font-bold mb-1">Nouvelle réunion</h1>
      <p className="text-muted-foreground text-sm mb-6">Choisissez le mode de captation.</p>
      <Card className="p-6 space-y-4">
        <Input placeholder="Titre de la réunion" value={title} onChange={(e) => setTitle(e.target.value)} />
        <div className="grid grid-cols-3 gap-3">
          {modes.map(([m, Icon, t, d]) => (
            <button key={m} onClick={() => setMode(m)} className={`text-left p-4 rounded-2xl border transition ${mode === m ? "border-brand bg-brand/10" : "border-border bg-[#0f1626]"}`}>
              <Icon size={22} className="text-brand-2" /><div className="font-semibold mt-2 text-sm">{t}</div><div className="text-xs text-muted-foreground">{d}</div>
            </button>
          ))}
        </div>
        {mode === "visio" && (
          <div className="space-y-1.5">
            <label className="text-sm font-medium text-muted-foreground">Lien de la réunion</label>
            <Input placeholder="https://meet.google.com/abc-defg-hij · teams.live.com/meet/… · zoom.us/j/…" value={url} onChange={(e) => setUrl(e.target.value)} />
            <p className="text-xs text-muted-foreground">Un bot Scribe rejoindra la réunion et la transcrira (via Vexa).</p>
          </div>
        )}
        {mode === "livekit" && (
          <p className="text-xs text-muted-foreground">Une salle de visio Scribe sera créée ; invitez les participants et la transcription se fait en direct.</p>
        )}
        <label className="flex gap-2.5 items-start text-sm p-3 rounded-xl bg-amber-500/10 border border-amber-500/25">
          <input type="checkbox" checked={consent} onChange={(e) => setConsent(e.target.checked)} className="mt-1 accent-brand w-4 h-4" />
          <span>🔒 Je recueille le consentement RGPD des participants.</span>
        </label>
        {err && <div className="text-rose-400 text-sm">{err}</div>}
        <Button variant="primary" className="w-full" disabled={!consent || (mode === "visio" && !url.trim())} onClick={create}>Continuer →</Button>
      </Card>
    </div>
  );
}

/* ---- Visio : bot Vexa qui rejoint Teams/Meet/Zoom ---- */
function VisioRoom({ meeting, onDone }: { meeting: Meeting; onDone: () => void }) {
  const [finalizing, setFinalizing] = React.useState(false);
  const [err, setErr] = React.useState("");
  const finalize = async () => {
    setFinalizing(true); setErr("");
    try { await api.finalizeVisio(meeting.id); onDone(); }
    catch (e: any) { setErr(e.message); setFinalizing(false); }
  };
  return (
    <div className="max-w-2xl animate-fade-up">
      <h1 className="text-2xl font-bold mb-5">📹 {meeting.title}</h1>
      <Card className="p-8 text-center">
        <div className="text-4xl mb-3">🤖</div>
        <h3 className="text-lg font-semibold mb-1">Le bot Scribe a rejoint la réunion</h3>
        <p className="text-sm text-muted-foreground mb-6">Il transcrit en temps réel. Cliquez ci-dessous une fois la réunion terminée pour récupérer le transcript et générer le compte-rendu.</p>
        {err && <div className="text-rose-400 text-sm mb-3">{err}</div>}
        <Button variant="primary" onClick={finalize} disabled={finalizing}>
          {finalizing ? "Récupération du transcript…" : "Terminer & générer le compte-rendu"}
        </Button>
      </Card>
    </div>
  );
}

/* ---- Auth ---- */
function Auth({ onAuthed }: { onAuthed: () => void }) {
  const [mode, setMode] = React.useState<"login" | "reg">("login");
  const [email, setEmail] = React.useState(""); const [pw, setPw] = React.useState(""); const [name, setName] = React.useState("");
  const [err, setErr] = React.useState("");
  const submit = async (e: React.FormEvent) => {
    e.preventDefault(); setErr("");
    try { if (mode === "reg") await api.register(email, pw, name); await api.login(email, pw); onAuthed(); }
    catch (x: any) { setErr(x.message); }
  };
  return (
    <div className="grid lg:grid-cols-[1.1fr_.9fr] min-h-screen">
      <div className="p-[7vh_6vw] flex flex-col justify-center px-[6vw]">
        <div className="flex items-center gap-2.5 mb-8"><div className="grid place-items-center w-9 h-9 rounded-xl bg-gradient-to-br from-brand to-violet text-lg">🎙️</div><span className="text-xl font-extrabold">Scribe</span></div>
        <h1 className="text-4xl lg:text-5xl font-extrabold leading-[1.05] mb-4">Vos réunions,<br /><span className="grad-text">transcrites & résumées</span><br />en toute souveraineté.</h1>
        <p className="text-muted-foreground text-lg max-w-md">Transcription locale (Faster-Whisper), diarisation (PyAnnote), analyse (Qwen 2.5). Aucune donnée ne quitte votre infrastructure.</p>
      </div>
      <div className="flex items-center justify-center p-[5vh_4vw]">
        <Card className="w-full max-w-sm p-7">
          <div className="flex gap-2 p-1.5 bg-[#0d1320] rounded-xl mb-5">
            <button className={`flex-1 py-2 rounded-lg text-sm font-semibold ${mode === "login" ? "bg-muted" : "text-muted-foreground"}`} onClick={() => setMode("login")}>Connexion</button>
            <button className={`flex-1 py-2 rounded-lg text-sm font-semibold ${mode === "reg" ? "bg-muted" : "text-muted-foreground"}`} onClick={() => setMode("reg")}>Inscription</button>
          </div>
          <form onSubmit={submit} className="space-y-3">
            {mode === "reg" && <Input placeholder="Nom complet" value={name} onChange={(e) => setName(e.target.value)} />}
            <Input type="email" placeholder="vous@entreprise.fr" value={email} onChange={(e) => setEmail(e.target.value)} required />
            <Input type="password" placeholder="Mot de passe" value={pw} onChange={(e) => setPw(e.target.value)} required />
            {err && <div className="text-rose-400 text-sm">{err}</div>}
            <Button variant="primary" className="w-full">{mode === "login" ? "Se connecter →" : "Créer mon compte →"}</Button>
          </form>
        </Card>
      </div>
    </div>
  );
}
