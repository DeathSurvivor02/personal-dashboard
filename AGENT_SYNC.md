# Agent Sync — Personal Dashboard & Cross-Repo Session

* **Updated:** 2026-11-19 03:32 EST
* **Agents:** Antigravity, Claude Code (`claude -p --dangerously-skip-permissions`), Codex CLI (`codex exec`)

## 1. Global Rules Sync
* Source: `C:\Users\bynoe\.gemini\GEMINI.md`
* Synced to Claude Code: `C:\Users\bynoe\.claude\CLAUDE.md` (added Universal Repository Architecture section).
* Synced to Codex CLI: `C:\Users\bynoe\.codex\AGENTS.md` (added Universal Repository Architecture section alongside Zero Emojis, Notion Engineering Sync, and Repository Safety).

## 2. Personal Dashboard (`Dashboard` / `feature/themes-html`)
* **Root Cause (Codex + Claude):** Commit `8e76792` removed `#theme` while `index.html` still attached a listener to `document.getElementById('theme')`, throwing a null dereference before `showTab()` ran and leaving all `#panel-*` hidden. `index.html` also expected `window.__PERSISTED_ACADEMIC_STATE__` from the desktop host.
* **Fixes Applied:**
  * Restored startup rendering across all 5 tabs (`Schoolwork`, `GitHub`, `Wordle`, `Chess.com`, `Spotify`).
  * Consolidated secondary controls (System/Light/Dark mode, 6 palette pills wired to `--bg`/`--ink`/`--focus`, Schoolwork sync, GitHub/Chess.com usernames, Wordle practice, Spotify client ID/reconnect/disconnect) into a single accessible **Settings** modal in the top bar.
  * Preserved account persistence (`DeathSurvivor02`, `eanbynoe`, Spotify, Wordle, Schoolwork) in `localStorage`, `academic_state.json`, and `school_sync_config.json`.
  * Rebuilt `academic_dashboard.exe` (`cargo build --release --bin academic_dashboard`), installed to `AppData\Local\Programs\AcademicDashboard\AcademicDashboard.exe`, and verified zero JS errors in Edge headless and on `127.0.0.1:43821`.

## 3. SiteLine (`YMInc - Software`, Local Read-Only — Not Pushed)
* Inspected WPF desktop app (`MainWindow.xaml.cs`, `DatabaseService.cs`), React/Vite mock frontend, and Node scripts.
* Produced architecture Mermaid diagram and prioritized recommendations: (1) move Neon credentials/pepper out of source into `.env` and fix password reset, (2) split `MainWindow.xaml.cs` (1,389 lines) and `DatabaseService.cs` (2,172 lines) by feature, (3) complete write-path QA (`QA-08`, `QA-09`, `QA-13`, `QA-14`), (4) decide React frontend scope, and (5) apply token-driven UI/UX polish across dialogs.

## 4. Portfolio (`portfolio` / `feature/live-previews`)
* Replaced hardcoded Valorant and Transit demos with real implementations:
  * `src/services/valorantApi.js`: live fetch to `valorant-api-six.vercel.app` with timeout, real status/latency, and demo-mode warning when `HENRIK_API_KEY` is unset.
  * `src/data/transit.js`: Toronto station graph and A* routing engine (matching the offline Flutter Transit Routing Engine).
  * Updated `src/components/Projects/Demos.jsx` and `src/data/site.js`.
* Verified `npm run build` and `eslint .` pass cleanly.
