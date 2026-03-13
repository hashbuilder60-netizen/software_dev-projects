import express from "express";

export const app = express();
app.use(express.json());

type Task = { id: number; title: string; done: boolean };
const tasks: Task[] = [];
let nextId = 1;

app.get("/health", (_req, res) => {
  res.json({ status: "ok", stack: "typescript" });
});

app.get("/tasks", (_req, res) => {
  res.json(tasks);
});

app.post("/tasks", (req, res) => {
  const title = String(req.body?.title ?? "").trim();
  if (!title) {
    return res.status(400).json({ error: "title is required" });
  }
  const task = { id: nextId++, title, done: false };
  tasks.push(task);
  return res.status(201).json(task);
});

app.patch("/tasks/:id", (req, res) => {
  const id = Number(req.params.id);
  const task = tasks.find((t) => t.id === id);
  if (!task) {
    return res.status(404).json({ error: "task not found" });
  }
  if (typeof req.body?.done !== "boolean") {
    return res.status(400).json({ error: "done must be boolean" });
  }
  task.done = req.body.done;
  return res.json(task);
});