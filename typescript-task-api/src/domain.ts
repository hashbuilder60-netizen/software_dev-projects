export type WorkItemPriority = "low" | "medium" | "high" | "urgent";
export type WorkItemStatus = "planned" | "in_progress" | "blocked" | "done";

export type WorkItem = {
  id: string;
  title: string;
  description: string;
  priority: WorkItemPriority;
  status: WorkItemStatus;
  version: number;
  idempotencyKey: string;
  createdAt: string;
  updatedAt: string;
  completedAt: string | null;
};

export type WorkItemCreate = {
  title: string;
  description?: string;
  priority?: WorkItemPriority;
};

export type WorkItemUpdate = {
  title?: string;
  description?: string;
  priority?: WorkItemPriority;
  status?: WorkItemStatus;
  expectedVersion: number;
};

export const PRIORITIES: WorkItemPriority[] = ["low", "medium", "high", "urgent"];
export const STATUSES: WorkItemStatus[] = ["planned", "in_progress", "blocked", "done"];
