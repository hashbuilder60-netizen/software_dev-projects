import express from "express";
import { mkdirSync } from "node:fs";
import { dirname, resolve } from "node:path";

import { ConflictError, NotFoundError, ValidationError } from "./errors.js";
import { WorkItemRepository } from "./repository.js";
import { WorkItemService } from "./service.js";

type AppOptions = {
  storagePath?: string;
};

export function createApp(options: AppOptions = {}) {
  const app = express();
  const storagePath = resolve(options.storagePath ?? "data/work-items.json");
  mkdirSync(dirname(storagePath), { recursive: true });
  const service = new WorkItemService(new WorkItemRepository(storagePath));

  app.use(express.json());

  app.get("/health", (_req, res) => {
    res.json({ status: "ok", stack: "typescript", storage: "json-file" });
  });

  app.get("/v1/work-items", (req, res) => {
    try {
      const limit = Number(req.query.limit ?? 20);
      const offset = Number(req.query.offset ?? 0);
      const result = service.list({
        status: typeof req.query.status === "string" ? req.query.status : undefined,
        priority: typeof req.query.priority === "string" ? req.query.priority : undefined,
        query: typeof req.query.q === "string" ? req.query.q : undefined,
        limit: Number.isFinite(limit) && limit > 0 ? limit : 20,
        offset: Number.isFinite(offset) && offset >= 0 ? offset : 0,
      });
      return res.json({ ...result, limit, offset });
    } catch (error) {
      return sendError(res, error);
    }
  });

  app.get("/v1/work-items/stats", (_req, res) => {
    res.json(service.stats());
  });

  app.get("/v1/work-items/:id", (req, res) => {
    try {
      return res.json(service.get(req.params.id));
    } catch (error) {
      return sendError(res, error);
    }
  });

  app.post("/v1/work-items", (req, res) => {
    try {
      const headerValue = req.header("Idempotency-Key") ?? req.header("idempotency-key") ?? "";
      const result = service.create(req.body, headerValue);
      return res.status(result.created ? 201 : 200).json(result);
    } catch (error) {
      return sendError(res, error);
    }
  });

  app.patch("/v1/work-items/:id", (req, res) => {
    try {
      return res.json(service.update(req.params.id, req.body));
    } catch (error) {
      return sendError(res, error);
    }
  });

  return app;
}

function sendError(res: express.Response, error: unknown) {
  if (error instanceof ValidationError) {
    return res.status(400).json({ error: error.message });
  }
  if (error instanceof ConflictError) {
    return res.status(409).json({ error: error.message });
  }
  if (error instanceof NotFoundError) {
    return res.status(404).json({ error: error.message });
  }
  return res.status(500).json({ error: "internal server error" });
}

export const app = createApp();
