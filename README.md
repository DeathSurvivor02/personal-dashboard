# Personal Productivity & Life Dashboard

A modular personal dashboard designed for developers, students, and professionals. Features a modern sidebar layout bringing together developer workflows, academic tracking, POS project management, and daily mind games.

---

## 🚀 Features & Widgets

### 1. ♟️ Chess.com Widget
- **Daily Puzzle:** Auto-fetches the daily puzzle with interactive solving or board preview.
- **Ongoing Games:** Real-time tracking of active games, current move turns, clock timers, and opponent stats.
- Direct quick links into live matches.

### 2. 🟩 Wordle Mini-App
- Embedded daily Wordle mini-game.
- Streak counters, score distribution, and local history tracking.

### 3. 🐙 GitHub Activity & PR Monitor
- **Pull Requests:** Incoming review requests, authored PRs, CI status indicators, and review badges.
- **Active Repositories:** Fast view of pinned repositories, star counts, open issues, and recent commits.

### 4. 🔬 Personal Projects & R&D Hub (Simulations & Side Projects)
- **Project Concept & Architecture Cards:** Track technical experiments, indie builds, and simulation ideas.
- **Engineering & Optimization Tracker:**
  - *Example (Neutron Star Simulation):*
    - **Optimization Methods:**
      - *Fixed Time Step:* Decouple physics calculations from frame rate.
      - *Multi-threading:* Offload heavy numerical computations to worker threads/compute shaders.
      - *Approximations:* Simplified analytical models where high-fidelity simulation isn't required.
    - **Status & Phase:** Note-taking / Strategy formulation / In-development.
- **Tech Stack & Milestone Tags:** Easily categorize by languages/frameworks (WebGPU, Rust, C++, Three.js, Python) and progress stage.

### 5. 📚 School Assignment & Course Progress Tracker
- Course-based grouping (e.g. CS, Math, Engineering).
- Visual progress tracking (`% completed`) per course.
- Priority and deadline alerts (*Due Today*, *This Week*, *Later*).

### 6. 💼 Work Task Management — YM Inc. POS Support
- Tailored task management for **YM Inc. Point of Sale (POS)** project implementation.
- Milestone and ticket tracking (Terminal provisioning, API integration checkpoints, client onboarding).
- Priority-ranked status board (Backlog, In Progress, Blocked, Deployed).
- Rapid incident / scratchpad log.

---

## 🎨 UI & Layout Design
- **Sidebar Navigation:** Collapsible left-hand navigation with quick jump links, summary badges, and status widgets.
- **Modular Dashboard Grid:** Responsive multi-column layout supporting card collapsing and customizable visibility.
- **Theme Support:** Dark / Light mode default styling.

---

## 🛠️ Tech Stack Architecture
- **Framework:** Next.js (React / TypeScript) / Vite + React
- **Styling:** Tailwind CSS + shadcn/ui
- **Icons:** Lucide React
- **Data Fetching:** TanStack Query (React Query)
- **External APIs:** Chess.com Public API, GitHub REST / GraphQL API

---

## 📂 Project Structure (Planned)

```text
├── src/
│   ├── components/
│   │   ├── layout/
│   │   │   ├── Sidebar.tsx
│   │   │   ├── Header.tsx
│   │   │   └── Shell.tsx
│   │   ├── widgets/
│   │   │   ├── chess/
│   │   │   ├── wordle/
│   │   │   ├── github/
│   │   │   ├── school/
│   │   │   └── work-pos/
│   ├── hooks/
│   ├── lib/
│   └── types/
├── README.md
```

---

## 🗺️ Roadmap
- [x] Planning & Architectural Design
- [ ] Base Project Scaffolding with Sidebar
- [ ] School & Work Task Management modules
- [ ] GitHub & Chess.com API Integrations
- [ ] Wordle Mini-widget
- [ ] Deployment & Live Syncing
