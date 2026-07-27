export interface Author {
  id: string;
  name: string;
  avatar_color: string;
}

export interface User {
  id: string;
  username: string;
  name: string;
  title: string;
  email: string;
  avatar_color: string;
  presence: string;
  tenant_id: string | null;
  company_id: string | null;
  permissions: string[];
}

export type Visibility = "public" | "private";

export interface News {
  id: string; title: string; summary: string; body: string;
  author: Author | null; pinned: boolean; views: number; comment_count: number;
  visibility: Visibility; scope: string; created_at: string;
}
export interface BlogPost {
  id: string; title: string; author: Author | null; excerpt: string; body: string;
  rating: string; tags: string[]; visibility: Visibility; created_at: string;
}
export interface EventItem {
  id: string; title: string; starts_at: string; location: string; description: string;
  attendees: number; mode: string; visibility: Visibility; created_at: string;
}
export interface MediaItem {
  id: string; kind: string; title: string; album: string; color: string;
  rating: string; visibility: Visibility; created_at: string;
}
export interface KnowledgeDoc {
  id: string; title: string; category: string; doc_type: string; size: string;
  visibility: Visibility; created_at: string;
}

export interface Group {
  id: string; name: string; description: string; privacy: Visibility;
  color: string; category: string; owner: Author | null;
  member_count: number; is_member: boolean; created_at: string;
}
export interface ForumTopic {
  id: string; title: string; body: string; author: Author | null;
  category: string; views: number; solved: boolean; visibility: Visibility;
  reply_count: number; created_at: string;
}

export interface Project {
  id: string; name: string; client: string; health: "green" | "yellow" | "red";
  progress: number; budget_total: string; budget_used: string; deadline: string | null;
  manager: Author | null; task_count: number; created_at: string;
}
export interface Task {
  id: string; project: string; title: string;
  status: "planning" | "in_progress" | "review" | "done";
  assignee: Author | null; priority: "low" | "medium" | "high";
  due: string | null; progress: number; created_at: string;
}

export interface Contract {
  id: string; title: string; vendor: string;
  stage: "negotiation" | "rfp" | "evaluation" | "executing" | "settled";
  contract_type: string; value: string; deadline: string | null;
  owner: Author | null; created_at: string;
}

export type NfStage = "proposal" | "screening" | "jury" | "approval" | "contract" | "monitoring" | "exit";
export interface NfProject {
  id: string; code: string; title_fa: string; field: string; rahbar: string;
  budget: string; stage: NfStage; sub_status: string; green_path: boolean;
  progress: number; created_at: string;
}

export interface TrainingCourse {
  id: string; title: string; instructor: string; starts_at: string | null;
  hours: number; capacity: number; status: "open" | "running" | "done";
  satisfaction: string | null; enrolled: number; is_enrolled: boolean; created_at: string;
}
export interface Ticket {
  id: string; number: string; subject: string; category: string;
  priority: "low" | "medium" | "urgent"; status: "open" | "in_review" | "answered" | "closed";
  author: Author | null; created_at: string;
}
export interface PollOption { id: string; label: string; votes: number; }
export interface Poll {
  id: string; question: string; ends_at: string | null;
  options: PollOption[]; my_vote: string | null; created_at: string;
}

export interface ResearchOpportunity {
  id: string; title: string; field: string;
  stage: "open" | "review" | "judging" | "running" | "closed";
  budget: string; supervisor: string; deadline: string | null;
  applicant_count: number; created_at: string;
}
export interface AwardEntry { id: string; track: string; title: string; company: string; status: string; score: number | null; }
export interface AwardTrack { id: string; title: string; categories: string[]; submission_count: number; entries: AwardEntry[]; created_at: string; }
export interface Notification { id: string; text: string; kind: string; read: boolean; link: string; created_at: string; }
