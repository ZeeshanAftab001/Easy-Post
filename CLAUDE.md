# CLAUDE.md — EasyPost AI Operational Guide

## 🚀 Development Operations

### Backend (FastAPI / Python)
- **Start Server**: `uvicorn main:app --reload --port 8000` (from `backend/`)
- **Database Migrations**: `alembic upgrade head` (if applicable)
- **Environment**: Ensure `.env` contains AWS, Meta, OpenAI, and WhatsApp credentials.

### Frontend (React / Vite)
- **Start Dev Server**: `npm run dev` (from `frontend/`)
- **Production Build**: `npm run build`
- **Dependency Install**: `npm install`

---

## 🛠️ Project Architecture

### Infrastructure Metaphor
The system is designed as an **Operator Terminal** for social media orchestration.
- **Nodes**: Connected social media accounts (Facebook and Instagram).

- **Deployment**: The act of publishing content to one or more nodes.
- **Narratives**: AI-generated or manual post captions.

### High-Fidelity Tech Stack
- **Backend**: FastAPI with LangGraph for agentic workflow control.
- **Frontend**: React + TailwindCSS with a custom "Obsidian-Lime" tactical theme.
- **Intelligence**: OpenAI GPT-4o mediated via custom MCP (Model Context Protocol) servers.
- **Orchestration**: Parallel async deployment via `asyncio.gather` for multi-platform broadcasting.

---

## ✒️ Coding Standards & Patterns

### Design System (Obsidian-Lime)
- **Aesthetic**: Deep dark backgrounds (`#000000`), glassmorphism, and Toxic Lime (`#ccff00`) accents.
- **Typography**: `Plus Jakarta Sans` for headers, `JetBrains Mono` for technical labels/data.
- **Interaction**: Use `reveal` CSS animations for all new component entrances.

### API & Logic Patterns
- **Concurrency**: Always use `async/await` and prioritize `asyncio.gather` for multi-platform network requests.
- **Error Handling**: Hardened WhatsApp webhooks with `try-except` blocks to prevent Meta retry loops on AI failure.
- **State Management**: LocalStorage for JWT tokens; real-time status badges for social connectivity.

### File Structure
- `backend/app/chat/routes/`: Router logic for WhatsApp, AI, and Posts.
- `backend/app/mcp/`: Tool definitions for social platform interactions.
- `frontend/src/pages/`: Modular page definitions (Dashboard, ContentHub, etc.).
- `frontend/src/components/`: Reusable high-fidelity UI modules.

---

## 📡 Deployment Nodes
- **Facebook/Instagram**: Meta Graph API integration.
- **WhatsApp**: Meta Cloud API for automated operator commands.

