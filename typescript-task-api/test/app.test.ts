import request from "supertest";
import { describe, expect, it } from "vitest";
import { app } from "../src/app.js";

describe("typescript-task-api", () => {
  it("returns health", async () => {
    const res = await request(app).get("/health");
    expect(res.status).toBe(200);
    expect(res.body.status).toBe("ok");
  });
});