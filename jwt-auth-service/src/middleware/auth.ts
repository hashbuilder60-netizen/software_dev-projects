import { NextFunction, Request, Response } from "express";
import jwt from "jsonwebtoken";

export type AuthRequest = Request & { user?: { email: string } };

export function requireAuth(req: AuthRequest, res: Response, next: NextFunction) {
  const auth = req.header("authorization") || "";
  const token = auth.startsWith("Bearer ") ? auth.slice(7) : "";
  if (!token) {
    return res.status(401).json({ error: "missing token" });
  }

  try {
    const payload = jwt.verify(token, process.env.JWT_SECRET || "dev-secret") as { email: string };
    req.user = { email: payload.email };
    return next();
  } catch {
    return res.status(401).json({ error: "invalid token" });
  }
}