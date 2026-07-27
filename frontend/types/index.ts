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
