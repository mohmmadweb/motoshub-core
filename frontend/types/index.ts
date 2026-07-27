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
