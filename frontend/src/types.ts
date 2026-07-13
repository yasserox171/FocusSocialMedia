export interface User {
  id: number;
  username: string;
  display_name: string;
  bio: string;
  avatar: string | null;
  kind: "human" | "agent" | "center";
  is_active: boolean;
  is_staff?: boolean;
  date_joined: string;
}

export interface Post {
  id: number;
  author: User;
  text: string;
  image: string | null;
  video: string | null;
  link_url: string;
  link_title: string;
  created_at: string;
  likes_count: number;
  liked_by_me: boolean;
}

export interface Paginated<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface Message {
  id: number;
  conversation: number;
  sender: number;
  text: string;
  created_at: string;
  is_read: boolean;
}

export interface Conversation {
  id: number;
  other_user: User;
  last_message: Message | null;
  unread_count: number;
  updated_at: string;
}

export interface Notification {
  id: number;
  kind: "like" | "message" | "new_post";
  text: string;
  post_id: number | null;
  conversation_id: number | null;
  is_read: boolean;
  created_at: string;
  actor: { id: number; display_name: string; avatar: string | null };
}

export interface AgentProfile {
  id: number;
  username: string;
  display_name: string;
  topic: string;
  system_prompt: string;
  enabled: boolean;
  posts_per_day: number;
  active_hour_start: number;
  active_hour_end: number;
  last_posted_at: string | null;
  posts_count: number;
}

export interface Invite {
  id: number;
  token: string;
  display_name: string;
  note: string;
  created_at: string;
  used: boolean;
}

export interface Stats {
  users_total: number;
  users_human: number;
  users_agent: number;
  posts_total: number;
  posts_week: number;
  likes_total: number;
}
