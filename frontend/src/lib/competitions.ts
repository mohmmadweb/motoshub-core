import { http } from "./http";

export const voteEntryApi = (entry: string) =>
  http<{ votes: number; my_vote: boolean }>(`/competitions/vote?entry=${entry}`, { method: "POST" });

export const joinChallengeApi = (challenge: string) =>
  http<{ joined: number; is_joined: boolean }>(`/challenges/${challenge}/join`, { method: "POST" });

/** Submit a work to a competition. `by` and the swatch are stamped server-side. */
export const submitEntryApi = async (competition: string, title: string, file?: File | null) => {
  let attachment: unknown = {};
  if (file) {
    const form = new FormData();
    form.append("file", file);
    attachment = await http("/uploads", { method: "POST", body: form });
  }
  return http("/competition-entries", {
    method: "POST",
    body: JSON.stringify({ competition, title, attachment }),
  });
};

export const deleteEntryApi = (entry: string) =>
  http(`/competition-entries/${entry}`, { method: "DELETE" });
