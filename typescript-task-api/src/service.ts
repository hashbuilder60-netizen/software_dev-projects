import { randomUUID } from "node:crypto";

import { ConflictError, NotFoundError, ValidationError } from "./errors.js";
import {
  PRIORITIES,
  STATUSES,
  type WorkItem,
  type WorkItemCreate,
  type WorkItemPriority,
  type WorkItemStatus,
  type WorkItemUpdate,
} from "./domain.js";
import { WorkItemRepository } from "./repository.js";

type ListOptions = {
  status?: string;
  priority?: string;
  query?: string;
  limit: number;
  offset: number;
};

export class WorkItemService {
  constructor(private readonly repository: WorkItemRepository) {}

  create(payload: WorkItemCreate, idempotencyKey: string): { created: boolean; item: WorkItem } {
    const normalizedKey = idempotencyKey.trim();
    if (!normalizedKey) {
      throw new ValidationError("Idempotency-Key header is required.");
    }

    const existing = this.repository.findByIdempotencyKey(normalizedKey);
    if (existing) {
      return { created: false, item: existing };
    }

    const title = payload.title?.trim();
    if (!title) {
      throw new ValidationError("title is required.");
    }

    const priority = this.validatePriority(payload.priority ?? "medium");
    const now = new Date().toISOString();
    const item: WorkItem = {
      id: randomUUID(),
      title,
      description: payload.description?.trim() ?? "",
      priority,
      status: "planned",
      version: 1,
      idempotencyKey: normalizedKey,
      createdAt: now,
      updatedAt: now,
      completedAt: null,
    };

    return { created: true, item: this.repository.save(item) };
  }

  list(options: ListOptions): { items: WorkItem[]; total: number } {
    const status = options.status ? this.validateStatus(options.status) : undefined;
    const priority = options.priority ? this.validatePriority(options.priority) : undefined;
    const query = options.query?.trim().toLowerCase();

    const filtered = this.repository
      .list()
      .filter((item) => (status ? item.status === status : true))
      .filter((item) => (priority ? item.priority === priority : true))
      .filter((item) => {
        if (!query) {
          return true;
        }
        return (
          item.title.toLowerCase().includes(query) ||
          item.description.toLowerCase().includes(query)
        );
      })
      .sort((left, right) => right.createdAt.localeCompare(left.createdAt));

    return {
      items: filtered.slice(options.offset, options.offset + options.limit),
      total: filtered.length,
    };
  }

  get(id: string): WorkItem {
    const item = this.repository.findById(id);
    if (!item) {
      throw new NotFoundError("work item not found");
    }
    return item;
  }

  update(id: string, payload: WorkItemUpdate): WorkItem {
    const current = this.get(id);

    if (payload.expectedVersion !== current.version) {
      throw new ConflictError("expectedVersion does not match the current version.");
    }

    const title = payload.title !== undefined ? payload.title.trim() : current.title;
    if (!title) {
      throw new ValidationError("title cannot be empty.");
    }

    const nextStatus = payload.status ? this.validateStatus(payload.status) : current.status;
    const nextPriority = payload.priority ? this.validatePriority(payload.priority) : current.priority;
    const now = new Date().toISOString();

    const updated: WorkItem = {
      ...current,
      title,
      description: payload.description !== undefined ? payload.description.trim() : current.description,
      priority: nextPriority,
      status: nextStatus,
      version: current.version + 1,
      updatedAt: now,
      completedAt: nextStatus === "done" ? current.completedAt ?? now : null,
    };

    return this.repository.save(updated);
  }

  stats(): Record<string, number> {
    const items = this.repository.list();
    return {
      total: items.length,
      planned: items.filter((item) => item.status === "planned").length,
      in_progress: items.filter((item) => item.status === "in_progress").length,
      blocked: items.filter((item) => item.status === "blocked").length,
      done: items.filter((item) => item.status === "done").length,
    };
  }

  private validatePriority(value: string): WorkItemPriority {
    if (!PRIORITIES.includes(value as WorkItemPriority)) {
      throw new ValidationError(`priority must be one of: ${PRIORITIES.join(", ")}`);
    }
    return value as WorkItemPriority;
  }

  private validateStatus(value: string): WorkItemStatus {
    if (!STATUSES.includes(value as WorkItemStatus)) {
      throw new ValidationError(`status must be one of: ${STATUSES.join(", ")}`);
    }
    return value as WorkItemStatus;
  }
}
