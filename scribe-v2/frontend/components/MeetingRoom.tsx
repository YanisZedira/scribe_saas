"use client";
/** MeetingRoom — interface de visioconférence Scribe (LiveKit, visio propre).
 *
 *  Utilise @livekit/components-react : grille vidéo, barre de contrôle
 *  (micro/caméra/partage d'écran/raccrocher) et thème sombre. Le LiveKit Agent
 *  (côté serveur) transcrit en temps réel chaque participant → /segment.
 *
 *  Flux : token via /api/livekit/token → connexion à la room (= meeting.id) →
 *  à la fin, "Terminer" déclenche finalize + analyse Qwen → compte-rendu.
 */
import * as React from "react";
import "@livekit/components-styles";
import {
  LiveKitRoom, VideoConference, RoomAudioRenderer,
} from "@livekit/components-react";
import { Card, Button } from "./ui/primitives";
import { api, type Meeting } from "@/lib/api";

export function MeetingRoom({ meeting, onEnded }: {
  meeting: Meeting; onEnded: () => void;
}) {
  const [conn, setConn] = React.useState<{ token: string; url: string } | null>(null);
  const [error, setError] = React.useState("");
  const [ending, setEnding] = React.useState(false);

  React.useEffect(() => {
    api.livekitToken(meeting.room_name || meeting.id)
      .then(setConn)
      .catch((e) => setError(e.message));
  }, [meeting]);

  const end = async () => {
    setEnding(true);
    try { await api.finalizeVisio(meeting.id); onEnded(); }
    catch (e: any) { setError(e.message); setEnding(false); }
  };

  if (error) {
    return (
      <Card className="p-8 text-center max-w-xl">
        <div className="text-rose-400 mb-3">LiveKit indisponible : {error}</div>
        <p className="text-sm text-muted-foreground">Vérifie que le serveur LiveKit
          et le LiveKit Agent tournent (voir README self-host).</p>
      </Card>
    );
  }
  if (!conn) return <Card className="p-8 text-center">Connexion à la salle…</Card>;

  return (
    <div className="animate-fade-up">
      <div className="flex items-center justify-between mb-3">
        <h1 className="text-xl font-bold">📹 {meeting.title}</h1>
        <Button variant="primary" onClick={end} disabled={ending}>
          {ending ? "Génération du compte-rendu…" : "Terminer & générer le CR"}
        </Button>
      </div>
      <div style={{ height: "70vh" }} className="rounded-2xl overflow-hidden border border-border">
        <LiveKitRoom token={conn.token} serverUrl={conn.url} connect audio video
          data-lk-theme="default" style={{ height: "100%" }}
          onDisconnected={() => { /* l'utilisateur clique "Terminer" pour finaliser */ }}>
          <VideoConference />
          <RoomAudioRenderer />
        </LiveKitRoom>
      </div>
      <p className="text-xs text-muted-foreground mt-2">
        🔴 Transcription en temps réel par le LiveKit Agent (Whisper local).
        Cliquez « Terminer » quand la réunion est finie.
      </p>
    </div>
  );
}
