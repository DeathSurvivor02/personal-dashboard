# Personal Productivity & Engineering Dashboard

A unified, modular command center built for developers, STEM students, and engineering support specialists. It combines daily developer workflows, academic course tracking, POS support management, physics simulation R&D notes, and daily mental warmups into a sleek sidebar layout.

[![GitHub Repo](https://img.shields.io/badge/GitHub-DeathSurvivor02%2Fpersonal--dashboard-blue?logo=github)](https://github.com/DeathSurvivor02/personal-dashboard)
[![SDLC](https://img.shields.io/badge/SDLC-Agile%20%2F%20Incremental-success)](sdlc_specification.md)

---

## System Architecture & Layout

```text
App Layout Shell
├── Left Sidebar (Collapsible)
│   ├── User Avatar & Status Pill ('Deep Work', 'POS Support', 'In Class')
│   ├── Navigation Filters (All, Work, School, Projects, Play)
│   ├── Quick Status Badges (Pending moves, PR alerts, Due tasks)
│   └── Mini Ambient/Media Controller (Lofi / Focus Sounds)
├── Top Header Bar
│   ├── Date & Weather Indicator
│   ├── Quick Scratchpad & Command Palette (`Cmd/Ctrl + K`)
│   ├── Pomodoro / Focus Timer Widget
│   └── Theme Toggle (Dark / Light)
└── Main Grid Viewport (Modular Responsive Cards)
    ├── Work & School Stream (Row 1)
    │   ├── YM Inc. POS Kanban & Incident Log
    │   └── School Assignment & Course Progress Tracker
    ├── Projects & Engineering Hub (Row 2)
    │   ├── Personal Projects (Neutron Star Simulation & Architecture Notes)
    │   └── GitHub Activity & Open PRs
    └── Mind & Recreation Zone (Row 3)
        ├── Chess.com Live Puzzle & Game Monitor
        └── Daily Wordle Mini-Game
```

---

## Core Modules & Features

### 1. Work Task Management — YM Inc. POS Support
* **Tailored POS Lifecycle:** Support tickets, terminal configurations, hardware provisioning, API integration checkpoints, and client rollout.
* **Severity Matrix:** P0 (Store Blocker / Outage) to P3 (General inquiry).
* **Kanban Board:** Backlog -> Investigating -> Testing -> Deployed / Resolved.
* **Incident Log / Quick Pad:** Fast scratchpad for store IDs, terminal serials, and phone notes.

### 2. School Assignment & Course Progress Tracker
* **Course Organization:** Course-based grouping (e.g. CS-401, MATH-310).
* **Visual Progress:** Dynamic progress bars (`% completed`) reflecting submitted vs. pending assignments.
* **Urgency Alerts:** *Due Today*, *Upcoming (2-3 days)*, *Later*.

### 3. Personal Projects & R&D Hub (Simulations & Side Projects)
* **Project Concept & Architecture Cards:** Track technical experiments, indie builds, and simulation ideas.
* **Engineering & Optimization Strategies:**
  * *Featured Example — **Neutron Star Simulation**:*
    * **Fixed Time Step:** Decouple physics calculations from frame rate.
    * **Multi-threading:** Offload heavy numerical computations to worker threads / compute shaders.
    * **Approximations:** Simplified analytical models where high-fidelity simulation isn't critical.
    * **Status:** Taking notes on options; specific strategies to be decided during development.
* **Tech Stack & Tags:** Easily categorize by languages/frameworks (WebGPU, Rust, C++, Three.js, Python).

### 4. GitHub Activity & PR Monitor
* **Pull Requests:** Reviews pending your action, authored PRs, and CI check indicators.
* **Active Repositories:** Fast view of pinned repositories, star counts, open issues, and recent commits.

### 5. Chess.com Widget
* **Daily Puzzle:** Auto-fetches the daily puzzle with interactive solving or board preview.
* **Ongoing Games:** Real-time tracking of active games, current move turns, clock timers, and opponent stats.

### 6. Wordle Mini-App
* Built-in lightweight daily 5-letter word game with streak counters, score distribution, and local history.

### 7. ⏱️ Focus & Daily Utilities
* **Pomodoro Timer:** Preset work/break sessions with sound alerts.
* **Quick Scratchpad (`Ctrl/Cmd + K`):** Instant modal for fleeting ideas and POS terminal notes.
* **Weather & Status Indicator:** Current local conditions and user activity status.

---

## Software Development Life Cycle (SDLC)

This project strictly adheres to an **Agile / Incremental SDLC Model**:

| Phase | Description | Deliverables | Status |
| :--- | :--- | :--- | :--- |
| **Phase 1: Requirements** | Functional & non-functional requirements engineering, user stories, and acceptance criteria. | User Stories & Functional Spec | Completed - Completed |
| **Phase 2: Design** | Component hierarchy, data schemas, UI wireframing, and tech stack selection. | [SDLC Spec Document](sdlc_specification.md) | Completed - Completed |
| **Phase 3: Implementation** | Sprint-based feature development (Frontend, API layers, local persistence). | Codebase & Components | Ready - Ready to Start (Sprint 0) |
| **Phase 4: Testing & QA** | Unit testing, component tests, API integration tests, and E2E flows. | Vitest / RTL / Playwright suites | Planned |
| **Phase 5: Deployment & CI** | Automated GitHub Actions CI/CD pipeline, build verification, and hosting. | Production deployment | Planned |

---

## Technology Stack (Rust-Powered)

| Layer | Choice | Rationale |
| :--- | :--- | :--- |
| **Core Systems & Backend** | **Rust** | Zero-cost abstractions, memory safety, and native concurrency for background sync & physics simulation workloads. |
| **App Architecture** | **Tauri v2 / Dioxus** | Native lightweight desktop executable with minimal RAM footprint (~25MB). |
| **Styling & Components** | **Tailwind CSS + Modular Grid** | Clean dark-mode aesthetic with responsive sidebar and widgets. |
| **Icons** | **Lucide** | Clean, developer-centric iconography. |
| **Async Runtime & Data** | **Tokio + SQLite (`rusqlite`)** | High-performance asynchronous API polling and offline-first persistence. |

---

## Sprint Implementation Plan
- [x] **Phase 1 & 2: SDLC Requirements & Architectural Design**
- [ ] **Sprint 0: Scaffolding & App Shell** (Sidebar, Top bar, Theme, Grid)
- [ ] **Sprint 1: Productivity Modules** (YM Inc. POS Support + School Tracker)
- [ ] **Sprint 2: R&D & Engineering Hub** (Projects & Simulation Strategy Cards)
- [ ] **Sprint 3: External API Integrations** (Chess.com & GitHub API)
- [ ] **Sprint 4: Focus Utilities & Games** (Pomodoro, Scratchpad, Wordle)
- [ ] **Sprint 5: QA Testing & Automated CI/CD**
