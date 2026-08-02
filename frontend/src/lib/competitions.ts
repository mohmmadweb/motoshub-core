import { http } from "./http";

export const voteEntryApi = (entry: string) =>
  http<{ votes: number; my_vote: boolean }>(`/competitions/vote?entry=${entry}`, { method: "POST" });

export const joinChallengeApi = (challenge: string) =>
  http<{ joined: number; is_joined: boolean }>(`/challenges/${challenge}/join`, { method: "POST" });
