import { useEffect, useRef, useState } from "react";
import { Phone, PhoneOff, Video, Mic, MicOff, VideoOff } from "lucide-react";
import Avatar from "./Avatar";
import { formatDuration, type CallKind, type CallState } from "../lib/webrtc";

/**
 * The in-call surface: the incoming-call prompt, and the live call itself.
 *
 * Media is rendered from the two MediaStreams the peer connection produced —
 * nothing here simulates a call. When `remoteStream` has no video track (an
 * audio call, or the other side turned their camera off) the avatar stands in.
 */
export default function CallPanel({
  state,
  kind,
  peerName,
  peerColor,
  incoming,
  localStream,
  remoteStream,
  seconds,
  micOn,
  camOn,
  onAccept,
  onDecline,
  onHangUp,
  onToggleMic,
  onToggleCam,
}: {
  state: CallState;
  kind: CallKind;
  peerName: string;
  peerColor?: string;
  incoming: boolean;
  localStream: MediaStream | null;
  remoteStream: MediaStream | null;
  seconds: number;
  micOn: boolean;
  camOn: boolean;
  onAccept: () => void;
  onDecline: () => void;
  onHangUp: () => void;
  onToggleMic: () => void;
  onToggleCam: () => void;
}) {
  const localRef = useRef<HTMLVideoElement>(null);
  const remoteRef = useRef<HTMLVideoElement>(null);
  const [remoteHasVideo, setRemoteHasVideo] = useState(false);

  useEffect(() => {
    if (localRef.current && localStream) localRef.current.srcObject = localStream;
  }, [localStream]);

  useEffect(() => {
    if (remoteRef.current && remoteStream) remoteRef.current.srcObject = remoteStream;
    setRemoteHasVideo(!!remoteStream?.getVideoTracks().some((t) => t.enabled));
  }, [remoteStream]);

  if (state === "idle" || state === "ended") return null;

  // ── incoming call prompt ──────────────────────────────────────────────────
  if (incoming && state === "ringing") {
    return (
      <div className="fixed inset-0 z-[60] flex items-center justify-center bg-black/60 p-4" dir="rtl">
        <div className="bg-white rounded-2xl shadow-2xl w-full max-w-xs overflow-hidden text-center p-6">
          <Avatar name={peerName} color={peerColor} size={72} />
          <p className="text-base font-bold text-ink-900 mt-3">{peerName}</p>
          <p className="text-xs text-ink-500 mt-1">
            تماس {kind === "video" ? "تصویری" : "صوتی"} ورودی…
          </p>
          <div className="flex items-center justify-center gap-4 mt-6">
            <button
              onClick={onDecline}
              aria-label="رد تماس"
              className="w-12 h-12 rounded-full bg-rose-600 text-white flex items-center justify-center hover:bg-rose-700 transition-colors"
            >
              <PhoneOff size={20} />
            </button>
            <button
              onClick={onAccept}
              aria-label="پاسخ به تماس"
              className="w-12 h-12 rounded-full bg-emerald-600 text-white flex items-center justify-center hover:bg-emerald-700 transition-colors animate-pulse"
            >
              {kind === "video" ? <Video size={20} /> : <Phone size={20} />}
            </button>
          </div>
        </div>
      </div>
    );
  }

  // ── live call ─────────────────────────────────────────────────────────────
  const label =
    state === "ringing" ? "در حال زنگ زدن…" :
    state === "connecting" ? "در حال اتصال…" :
    formatDuration(seconds);

  return (
    <div className="fixed inset-0 z-[60] flex flex-col bg-navy-950" dir="rtl">
      <div className="flex-1 relative flex items-center justify-center overflow-hidden">
        {kind === "video" && remoteHasVideo ? (
          <video ref={remoteRef} autoPlay playsInline className="w-full h-full object-cover" />
        ) : (
          <div className="flex flex-col items-center text-center">
            <Avatar name={peerName} color={peerColor} size={96} />
            <p className="text-xl font-bold text-white mt-4">{peerName}</p>
            <p className="text-sm text-navy-300 mt-1">{label}</p>
          </div>
        )}

        {/* Audio always plays, even when the avatar is showing. */}
        {(kind === "audio" || !remoteHasVideo) && (
          <audio ref={remoteRef as unknown as React.RefObject<HTMLAudioElement>} autoPlay className="hidden" />
        )}

        {kind === "video" && localStream && (
          <video
            ref={localRef}
            autoPlay
            playsInline
            muted
            className="absolute bottom-4 left-4 w-32 h-24 rounded-xl object-cover border-2 border-white/25 shadow-lg"
          />
        )}

        {kind === "video" && remoteHasVideo && (
          <span className="absolute top-4 right-4 bg-black/50 text-white text-xs px-3 py-1.5 rounded-full">
            {peerName} · {label}
          </span>
        )}
      </div>

      <div className="p-6 flex items-center justify-center gap-4">
        <button
          onClick={onToggleMic}
          aria-label={micOn ? "بی‌صدا کردن میکروفون" : "فعال‌کردن میکروفون"}
          aria-pressed={!micOn}
          className={`w-12 h-12 rounded-full flex items-center justify-center transition-colors ${
            micOn ? "bg-white/15 text-white hover:bg-white/25" : "bg-white text-navy-900"
          }`}
        >
          {micOn ? <Mic size={19} /> : <MicOff size={19} />}
        </button>

        {kind === "video" && (
          <button
            onClick={onToggleCam}
            aria-label={camOn ? "خاموش‌کردن دوربین" : "روشن‌کردن دوربین"}
            aria-pressed={!camOn}
            className={`w-12 h-12 rounded-full flex items-center justify-center transition-colors ${
              camOn ? "bg-white/15 text-white hover:bg-white/25" : "bg-white text-navy-900"
            }`}
          >
            {camOn ? <Video size={19} /> : <VideoOff size={19} />}
          </button>
        )}

        <button
          onClick={onHangUp}
          aria-label="پایان تماس"
          className="w-14 h-14 rounded-full bg-rose-600 text-white flex items-center justify-center hover:bg-rose-700 transition-colors"
        >
          <PhoneOff size={22} />
        </button>
      </div>
    </div>
  );
}
