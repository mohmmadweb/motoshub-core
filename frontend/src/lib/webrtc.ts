import { http } from "./http";

/**
 * Peer-to-peer voice and video calling.
 *
 * The server never carries media: it records that a call happened and relays
 * the SDP/ICE handshake over the DM socket, after which the two browsers talk
 * directly. That relay is why a call works at all without a media server, and
 * why the only server-side cost is a row in the calls table.
 *
 * STUN alone is enough for two peers on the same corporate network or with
 * ordinary NAT. Symmetric NAT on both ends needs a TURN relay, which this
 * deployment does not run — see `callLimitation`.
 */
const ICE_SERVERS: RTCIceServer[] = [
  { urls: ["stun:stun.l.google.com:19302", "stun:stun1.l.google.com:19302"] },
];

export type CallKind = "audio" | "video";
export type CallState = "idle" | "ringing" | "connecting" | "active" | "ended";

export type CallSignal =
  | { sdp: RTCSessionDescriptionInit }
  | { candidate: RTCIceCandidateInit };

export const callLimitation =
  "برقراری تماس نیازمند اتصال مستقیم بین دو مرورگر است؛ در برخی شبکه‌ها ممکن است برقرار نشود.";

export type CallHandle = {
  pc: RTCPeerConnection;
  localStream: MediaStream;
  close: () => void;
};

/** Ask for the microphone (and camera for a video call). */
export async function getLocalStream(kind: CallKind): Promise<MediaStream> {
  return navigator.mediaDevices.getUserMedia({
    audio: true,
    video: kind === "video" ? { width: { ideal: 1280 }, height: { ideal: 720 } } : false,
  });
}

/**
 * Build the connection. `onSignal` is called with anything the peer must
 * receive; feed the peer's messages back in through the returned handle.
 */
export function createPeer(
  localStream: MediaStream,
  onSignal: (signal: CallSignal) => void,
  onRemoteStream: (stream: MediaStream) => void,
  onStateChange: (state: RTCPeerConnectionState) => void,
): CallHandle {
  const pc = new RTCPeerConnection({ iceServers: ICE_SERVERS });

  localStream.getTracks().forEach((t) => pc.addTrack(t, localStream));

  pc.onicecandidate = (e) => {
    if (e.candidate) onSignal({ candidate: e.candidate.toJSON() });
  };
  pc.ontrack = (e) => onRemoteStream(e.streams[0]);
  pc.onconnectionstatechange = () => onStateChange(pc.connectionState);

  return {
    pc,
    localStream,
    close: () => {
      localStream.getTracks().forEach((t) => t.stop());
      pc.getSenders().forEach((s) => s.track?.stop());
      pc.onicecandidate = null;
      pc.ontrack = null;
      pc.onconnectionstatechange = null;
      pc.close();
    },
  };
}

export async function makeOffer(pc: RTCPeerConnection): Promise<RTCSessionDescriptionInit> {
  const offer = await pc.createOffer();
  await pc.setLocalDescription(offer);
  return offer;
}

export async function acceptOffer(
  pc: RTCPeerConnection,
  offer: RTCSessionDescriptionInit,
): Promise<RTCSessionDescriptionInit> {
  await pc.setRemoteDescription(new RTCSessionDescription(offer));
  const answer = await pc.createAnswer();
  await pc.setLocalDescription(answer);
  return answer;
}

/**
 * Apply whatever the peer sent. Candidates that arrive before the remote
 * description are dropped rather than thrown — the offer that follows carries
 * the same information, and a rejected candidate would abort the call.
 */
export async function applySignal(pc: RTCPeerConnection, signal: CallSignal): Promise<RTCSessionDescriptionInit | null> {
  if ("sdp" in signal && signal.sdp) {
    if (signal.sdp.type === "answer") {
      await pc.setRemoteDescription(new RTCSessionDescription(signal.sdp));
      return null;
    }
    return acceptOffer(pc, signal.sdp);
  }
  if ("candidate" in signal && signal.candidate) {
    try {
      await pc.addIceCandidate(new RTCIceCandidate(signal.candidate));
    } catch {
      /* ordering race — the description that follows carries the same route */
    }
  }
  return null;
}

// ── Server-side call records ────────────────────────────────────────────────
export const placeCall = (to: string, kind: CallKind) =>
  http<{ id: string; status: string; kind: CallKind }>("/chat/calls", {
    method: "POST",
    body: JSON.stringify({ to, kind }),
  });

export const setCallStatus = (callId: string, status: "accepted" | "declined" | "ended" | "missed") =>
  http<{ id: string; status: string; duration: number }>(`/chat/calls/${callId}`, {
    method: "PATCH",
    body: JSON.stringify({ status }),
  });

export type CallRecord = {
  id: string;
  direction: "in" | "out";
  peer: string;
  peerId: string;
  kind: CallKind;
  status: string;
  duration: number;
  at: string;
};

export const callHistory = () => http<CallRecord[]>("/chat/calls");

/** ‏۰۳:۴۵ — a duration a human can read. */
export const formatDuration = (seconds: number): string => {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
};
