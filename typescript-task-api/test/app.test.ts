import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import request from "supertest";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import { createApp } from "../src/app.js";

describe("typescript-task-api", () => {
  let tempDir = "";
  let app = createApp();

  beforeEach(() => {
    tempDir = mkdtempSync(join(tmpdir(), "ts-task-api-"));
    app = createApp({ storagePath: join(tempDir, "work-items.json") });
  });

  afterEach(() => {
    rmSync(tempDir, { recursive: true, force: true });
  });

  it("returns health", async () => {
    const res = await request(app).get("/health");
    expect(res.status).toBe(200);
    expect(res.body.status).toBe("ok");
    expect(res.body.storage).toBe("json-file");
  });

  it("supports idempotent creation and fetch", async () => {
    const payload = {
      title: "Ship release note pipeline",
      description: "Backfill changelog publishing step",
      priority: "high",
    };

    const first = await request(app)
      .post("/v1/work-items")
      .set("Idempotency-Key", "release:notes:001")
      .send(payload);
    const second = await request(app)
      .post("/v1/work-items")
      .set("Idempotency-Key", "release:notes:001")
      .send(payload);

    expect(first.status).toBe(201);
    expect(second.status).toBe(200);
    expect(first.body.item.id).toBe(second.body.item.id);
  });

  it("supports optimistic concurrency on updates", async () => {
    const created = await request(app)
      .post("/v1/work-items")
      .set("Idempotency-Key", "work:item:optimistic")
      .send({ title: "Coordinate migration", priority: "urgent" });

    const ok = await request(app)
      .patch(`/v1/work-items/${created.body.item.id}`)
      .send({ status: "in_progress", expectedVersion: 1 });
    const conflict = await request(app)
      .patch(`/v1/work-items/${created.body.item.id}`)
      .send({ status: "done", expectedVersion: 1 });

    expect(ok.status).toBe(200);
    expect(ok.body.version).toBe(2);
    expect(conflict.status).toBe(409);
  });

  it("supports filtered listing and stats", async () => {
    await request(app)
      .post("/v1/work-items")
      .set("Idempotency-Key", "list:one")
      .send({ title: "Refactor queue worker", priority: "medium" });
    const second = await request(app)
      .post("/v1/work-items")
      .set("Idempotency-Key", "list:two")
      .send({ title: "Mitigate deploy drift", priority: "urgent" });
    await request(app)
      .patch(`/v1/work-items/${second.body.item.id}`)
      .send({ status: "blocked", expectedVersion: 1 });

    const filtered = await request(app).get("/v1/work-items").query({ priority: "urgent" });
    const stats = await request(app).get("/v1/work-items/stats");

    expect(filtered.status).toBe(200);
    expect(filtered.body.total).toBeGreaterThanOrEqual(1);
    expect(filtered.body.items[0].priority).toBe("urgent");
    expect(stats.status).toBe(200);
    expect(stats.body.total).toBeGreaterThanOrEqual(2);
  });
});
