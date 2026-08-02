import { http } from "./http";

export type FriendState = "friend" | "incoming" | "outgoing" | "suggested";

export interface FriendNetwork {
  states: Record<string, FriendState>;
  following: string[];
}

export const getNetwork = () => http<FriendNetwork>("/social/friends");

const act = (op: string, user: string) =>
  http(`/social/friends?do=${op}`, { method: "POST", body: JSON.stringify({ user }) });

export const requestFriend = (user: string) => act("request", user);
export const acceptFriend = (user: string) => act("accept", user);
export const removeFriend = (user: string) => act("remove", user);
export const followUser = (user: string) => act("follow", user);
export const unfollowUser = (user: string) => act("unfollow", user);
