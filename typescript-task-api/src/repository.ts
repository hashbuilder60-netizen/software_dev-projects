import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname } from "node:path";

import type { WorkItem } from "./domain.js";

type StoredState = {
  workItems: WorkItem[];
};

export class WorkItemRepository {
  constructor(private readonly storagePath: string) {}

  list(): WorkItem[] {
    return this.readState().workItems;
  }

  findById(id: string): WorkItem | undefined {
    return this.list().find((item) => item.id === id);
  }

  findByIdempotencyKey(idempotencyKey: string): WorkItem | undefined {
    return this.list().find((item) => item.idempotencyKey === idempotencyKey);
  }

  save(workItem: WorkItem): WorkItem {
    const state = this.readState();
    const index = state.workItems.findIndex((item) => item.id === workItem.id);

    if (index >= 0) {
      state.workItems[index] = workItem;
    } else {
      state.workItems.push(workItem);
    }

    this.writeState(state);
    return workItem;
  }

  private readState(): StoredState {
    try {
      const raw = readFileSync(this.storagePath, "utf8");
      return JSON.parse(raw) as StoredState;
    } catch {
      return { workItems: [] };
    }
  }

  private writeState(state: StoredState): void {
    mkdirSync(dirname(this.storagePath), { recursive: true });
    writeFileSync(this.storagePath, JSON.stringify(state, null, 2));
  }
}
