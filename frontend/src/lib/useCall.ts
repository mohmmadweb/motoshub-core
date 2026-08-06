import { useCallback, useEffect, useRef, useState } from "react";
import {
  acceptOffer, applySignal, createPeer, getLocalStream, makeOffer,
  placeCall, setCallStatus,
  type CallHandle, type CallKind, type CallSignal, type CallState,
} from "./webrtc";

type Incoming = { callId: string; from: string; fromName: string; avatarColor?: string; kind: CallKind };

/**
 * Drives one call at a time.
 *
 * The DM socket is owned by the Chat page, so this hook does not open its own:
 * it is handed a `send` for outbound signalling and is fed inbound events
 * through `handleSocketEvent`. That keeps a single socket per user, which is
 * what the server's per-user group assumes.
 */
export function useCall(send: (payload: Record<string, unknown>) => void) {
  const [state, setState] = useState<CallState>("idle");
  const [kind, setKind] = useState<CallKind>("audio");
  const [peer, setPeer] = useState<{ id: string; name: string; color?: string } | null>(null);
  const [incoming, setIncoming] = useState(false);
  const [localStream, setLocalStream] = useState<MediaStream | null>(null);
  const [remoteStream, setRemoteStream] = useState<MediaStream | null>(null);
  const [seconds, setSeconds] = useState(0);
  const [micOn, setMicOn] = useState(true);
  const [camOn, setCamOn] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const handle = useRef<CallHandle | null>(null);
  const callId = useRef<string | null>(null);
  const pendingOffer = useRef<Incoming | null>(null);
  // Candidates that arrive before the answerer has a peer connection.
  const earlySignals = useRef<CallSignal[]>([]);

  const teardown = useCallback(() => {
    handle.current?.close();
    handle.current = null;
    callId.current = null;
    pendingOffer.current = null;
    earlySignals.current = [];
    setLocalStream(null);
    setRemoteStream(null);
    setSeconds(0);
    setMicOn(true);
    setCamOn(true);
    setIncoming(false);
    setPeer(null);
    setState("idle");
  }, []);

  // The call timer only runs while the call is actually up.
  useEffect(() => {
    if (state !== "active") return;
    const iv = setInterval(() => setSeconds((s) => s + 1), 1000);
    return () => clearInterval(iv);
  }, [state]);

  const attachPeer = useCallback(
    (peerId: string, stream: MediaStream) =>
      createPeer(
        stream,
        (signal) => send({ type: "call:signal", to: peerId, callId: callId.current, signal }),
        (remote) => setRemoteStream(remote),
        (connState) => {
          if (connState === "connected") setState("active");
          if (connState === "failed" || connState === "disconnected") {
            setError("اتصال برقرار نشد؛ ممکن است شبکه اجازهٔ اتصال مستقیم ندهد.");
            if (callId.current) setCallStatus(callId.current, "ended").catch(() => {});
            teardown();
          }
        },
      ),
    [send, teardown],
  );

  /** Ring someone. */
  const start = useCallback(
    async (peerId: string, peerName: string, callKind: CallKind, color?: string) => {
      setError(null);
      let stream: MediaStream;
      try {
        stream = await getLocalStream(callKind);
      } catch {
        setError(callKind === "video"
          ? "دسترسی به دوربین یا میکروفون داده نشد."
          : "دسترسی به میکروفون داده نشد.");
        return;
      }
      try {
        const call = await placeCall(peerId, callKind);
        callId.current = call.id;
      } catch {
        stream.getTracks().forEach((t) => t.stop());
        setError("امکان برقراری تماس با این کاربر وجود ندارد.");
        return;
      }
      setKind(callKind);
      setPeer({ id: peerId, name: peerName, color });
      setIncoming(false);
      setLocalStream(stream);
      setState("ringing");

      handle.current = attachPeer(peerId, stream);
      const offer = await makeOffer(handle.current.pc);
      send({ type: "call:signal", to: peerId, callId: callId.current, signal: { sdp: offer } });
    },
    [attachPeer, send],
  );

  /** Answer the call currently ringing. */
  const accept = useCallback(async () => {
    const inv = pendingOffer.current;
    if (!inv) return;
    setState("connecting");
    let stream: MediaStream;
    try {
      stream = await getLocalStream(inv.kind);
    } catch {
      setError("دسترسی به میکروفون داده نشد.");
      await setCallStatus(inv.callId, "declined").catch(() => {});
      teardown();
      return;
    }
    setLocalStream(stream);
    handle.current = attachPeer(inv.from, stream);
    await setCallStatus(inv.callId, "accepted").catch(() => {});

    // Replay anything that arrived while we were asking for the microphone.
    for (const signal of earlySignals.current) {
      const answer = await applySignal(handle.current.pc, signal);
      if (answer) {
        send({ type: "call:signal", to: inv.from, callId: inv.callId, signal: { sdp: answer } });
      }
    }
    earlySignals.current = [];
  }, [attachPeer, send, teardown]);

  const decline = useCallback(async () => {
    if (callId.current) await setCallStatus(callId.current, "declined").catch(() => {});
    teardown();
  }, [teardown]);

  const hangUp = useCallback(async () => {
    if (callId.current) await setCallStatus(callId.current, "ended").catch(() => {});
    teardown();
  }, [teardown]);

  const toggleMic = useCallback(() => {
    const track = localStream?.getAudioTracks()[0];
    if (!track) return;
    track.enabled = !track.enabled;
    setMicOn(track.enabled);
  }, [localStream]);

  const toggleCam = useCallback(() => {
    const track = localStream?.getVideoTracks()[0];
    if (!track) return;
    track.enabled = !track.enabled;
    setCamOn(track.enabled);
  }, [localStream]);

  /** Feed every `call:*` frame from the DM socket in here. */
  const handleSocketEvent = useCallback(
    async (d: Record<string, unknown>) => {
      const type = d.type as string;

      if (type === "call:invite") {
        // One call at a time: a second caller is declined rather than silently
        // replacing the conversation already in progress.
        if (state !== "idle") {
          setCallStatus(d.callId as string, "declined").catch(() => {});
          return;
        }
        const inv: Incoming = {
          callId: d.callId as string,
          from: d.from as string,
          fromName: (d.fromName as string) ?? "—",
          avatarColor: d.avatarColor as string | undefined,
          kind: (d.kind as CallKind) ?? "audio",
        };
        pendingOffer.current = inv;
        callId.current = inv.callId;
        setKind(inv.kind);
        setPeer({ id: inv.from, name: inv.fromName, color: inv.avatarColor });
        setIncoming(true);
        setState("ringing");
        return;
      }

      if (type === "call:state") {
        const status = d.status as string;
        if (status === "accepted") setState((s) => (s === "ringing" ? "connecting" : s));
        if (status === "declined" || status === "ended" || status === "missed") {
          if (status === "declined") setError("تماس رد شد.");
          teardown();
        }
        return;
      }

      if (type === "call:signal") {
        const signal = d.signal as CallSignal;
        if (!handle.current) {
          // The callee has not accepted yet — hold the handshake until they do.
          earlySignals.current.push(signal);
          return;
        }
        const answer = await applySignal(handle.current.pc, signal);
        if (answer) {
          send({ type: "call:signal", to: d.from, callId: d.callId, signal: { sdp: answer } });
        }
      }
    },
    [send, state, teardown],
  );

  // A call must not survive the page: hang up on unload.
  useEffect(() => {
    const onUnload = () => {
      if (callId.current) navigator.sendBeacon?.("/api/v1/chat/calls");
      handle.current?.close();
    };
    window.addEventListener("beforeunload", onUnload);
    return () => window.removeEventListener("beforeunload", onUnload);
  }, []);

  return {
    state, kind, peer, incoming, localStream, remoteStream, seconds, micOn, camOn, error,
    start, accept, decline, hangUp, toggleMic, toggleCam, handleSocketEvent,
    clearError: () => setError(null),
    acceptOffer,   // re-exported for tests
  };
}
