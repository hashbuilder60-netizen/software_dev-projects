import bcrypt from "bcryptjs";
import express from "express";
import jwt from "jsonwebtoken";
import { requireAuth, type AuthRequest } from "./middleware/auth.js";

const app = express();
app.use(express.json());

type User = { email: string; passwordHash: string };
const users: User[] = [];

app.post("/register", async (req, res) => {
  const email = String(req.body?.email ?? "").trim().toLowerCase();
  const password = String(req.body?.password ?? "");
  if (!email || !password) return res.status(400).json({ error: "email and password required" });
  if (users.some((u) => u.email === email)) return res.status(409).json({ error: "user already exists" });
  const passwordHash = await bcrypt.hash(password, 10);
  users.push({ email, passwordHash });
  return res.status(201).json({ message: "registered" });
});

app.post("/login", async (req, res) => {
  const email = String(req.body?.email ?? "").trim().toLowerCase();
  const password = String(req.body?.password ?? "");
  const user = users.find((u) => u.email === email);
  if (!user || !(await bcrypt.compare(password, user.passwordHash))) return res.status(401).json({ error: "invalid credentials" });
  const token = jwt.sign({ email }, process.env.JWT_SECRET || "dev-secret", { expiresIn: "1h" });
  return res.json({ token });
});

app.get("/me", requireAuth, (req: AuthRequest, res) => res.json({ email: req.user?.email }));

const port = process.env.PORT || 4100;
app.listen(port, () => {
  console.log(`jwt-auth-service listening on :${port}`);
});