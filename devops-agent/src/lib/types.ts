export type GitReference = {
  repo_url: string;
  branch: string;
  commit?: string | null;
  path?: string | null;
};

export type DeploymentTicket = {
  ticket_id: string;
  thread_id: string;
  status:
    | "draft"
    | "design"
    | "coding"
    | "plan_pending"
    | "review"
    | "awaiting_approval"
    | "approved"
    | "applied"
    | "drift_detected"
    | "closed";
  requested_by: string;
  environment: string;
  target_cloud: string;
  terraform_workspace: string;
  git: GitReference;
  intent_summary: string;
  constraints: Record<string, unknown>;
  current_stage: string;
  flags: Record<string, boolean>;
  created_at: string;
  updated_at: string;
};
