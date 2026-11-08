use dioxus::prelude::*;

fn main() {
    dioxus::launch(App);
}

#[derive(Clone, Copy, PartialEq)]
enum NavTab {
    All,
    Work,
    School,
    Projects,
    Play,
}

#[component]
fn App() -> Element {
    let mut current_tab = use_signal(|| NavTab::All);
    let pomodoro_seconds = use_signal(|| 25 * 60);
    let mut is_timer_running = use_signal(|| false);

    // Format timer
    let minutes = *pomodoro_seconds.read() / 60;
    let seconds = *pomodoro_seconds.read() % 60;

    rsx! {
        // Tailwind CDN inject for rapid prototyping & beautiful styling
        document::Link {
            rel: "stylesheet",
            href: "https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css"
        }
        style {
            r#"
            body {{
                background-color: #0B0F19;
                color: #F3F4F6;
                font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                margin: 0;
            }}
            .custom-scrollbar::-webkit-scrollbar {{
                width: 6px;
            }}
            .custom-scrollbar::-webkit-scrollbar-thumb {{
                background-color: #1F2937;
                border-radius: 9999px;
            }}
            "#
        }

        div { class: "flex h-screen w-screen overflow-hidden",
            // ─── LEFT COLLAPSIBLE SIDEBAR ─────────────────────────────────────
            aside { class: "w-64 bg-gray-900 border-r border-gray-800 flex flex-col justify-between p-4",
                div { class: "space-y-6",
                    // Header Brand & User Profile
                    div { class: "flex items-center space-x-3 pb-4 border-b border-gray-800",
                        div { class: "w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-500 to-purple-600 flex items-center justify-center font-bold text-white shadow-lg",
                            "DS"
                        }
                        div {
                            h2 { class: "font-semibold text-sm text-gray-100", "Command Center" }
                            span { class: "inline-flex items-center text-xs text-green-400 space-x-1",
                                span { class: "w-2 h-2 rounded-full bg-green-500 mr-1 animate-pulse" }
                                "Deep Work: Online"
                            }
                        }
                    }

                    // Navigation Links
                    nav { class: "space-y-1.5",
                        SidebarButton {
                            label: "All Overviews",
                            icon: "📊",
                            active: *current_tab.read() == NavTab::All,
                            on_click: move |_| current_tab.set(NavTab::All)
                        }
                        SidebarButton {
                            label: "YM Inc. POS Support",
                            icon: "💼",
                            active: *current_tab.read() == NavTab::Work,
                            on_click: move |_| current_tab.set(NavTab::Work)
                        }
                        SidebarButton {
                            label: "School & Courses",
                            icon: "📚",
                            active: *current_tab.read() == NavTab::School,
                            on_click: move |_| current_tab.set(NavTab::School)
                        }
                        SidebarButton {
                            label: "R&D Projects Lab",
                            icon: "🔬",
                            active: *current_tab.read() == NavTab::Projects,
                            on_click: move |_| current_tab.set(NavTab::Projects)
                        }
                        SidebarButton {
                            label: "Mind Games & Chess",
                            icon: "♟️",
                            active: *current_tab.read() == NavTab::Play,
                            on_click: move |_| current_tab.set(NavTab::Play)
                        }
                    }
                }

                // Mini Audio / Focus Controller in Sidebar Footer
                div { class: "p-3 bg-gray-800 rounded-xl border border-gray-700/60 flex items-center justify-between",
                    div { class: "flex items-center space-x-2.5",
                        span { class: "text-lg", "🎧" }
                        div {
                            p { class: "text-xs font-medium text-gray-200 leading-tight", "Focus Stream" }
                            p { class: "text-xs text-gray-400", "Binaural Physics Alpha" }
                        }
                    }
                    span { class: "text-xs px-2 py-0.5 rounded bg-indigo-900/60 text-indigo-300 border border-indigo-700/50 font-mono",
                        "LIVE"
                    }
                }
            }

            // ─── MAIN CONTENT VIEWPORT ────────────────────────────────────────
            main { class: "flex-1 flex flex-col h-full overflow-hidden bg-gray-950",
                // Top Action Bar
                header { class: "h-16 px-6 bg-gray-900/70 border-b border-gray-800 flex items-center justify-between backdrop-blur-md",
                    div { class: "flex items-center space-x-4",
                        h1 { class: "text-lg font-bold text-gray-100",
                            match *current_tab.read() {
                                NavTab::All => "Dashboard Overview",
                                NavTab::Work => "YM Inc. POS Support Workspace",
                                NavTab::School => "Academic Tracker & Deadlines",
                                NavTab::Projects => "R&D Simulations & Systems Lab",
                                NavTab::Play => "Recreation, Chess & Wordle",
                            }
                        }
                        span { class: "px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-800 text-gray-300 border border-gray-700",
                            "Rust Dioxus v0.6"
                        }
                    }

                    // Top Bar Widgets: Pomodoro & Quick Status
                    div { class: "flex items-center space-x-4",
                        // Focus Timer Chip
                        div { class: "flex items-center space-x-2 bg-gray-800/80 px-3 py-1.5 rounded-lg border border-gray-700/80",
                            span { class: "text-sm", "⏱️" }
                            span { class: "font-mono font-medium text-indigo-400 text-sm",
                                "{minutes:02}:{seconds:02}"
                            }
                            button {
                                class: "text-xs px-2 py-0.5 rounded bg-indigo-600 hover:bg-indigo-500 text-white font-semibold transition",
                                onclick: move |_| {
                                    let current = *is_timer_running.read();
                                    is_timer_running.set(!current);
                                },
                                if *is_timer_running.read() { "Pause" } else { "Start" }
                            }
                        }

                        // Weather & Date
                        div { class: "text-xs text-gray-400 text-right hidden sm:block",
                            p { class: "font-medium text-gray-200", "Sunny • 18°C" }
                            p { "Local Station" }
                        }
                    }
                }

                // Scrollable Grid Canvas
                div { class: "flex-1 p-6 overflow-y-auto custom-scrollbar space-y-6",
                    // ROW 1: R&D LAB & SIMULATION SPOTLIGHT (Featured Widget)
                    if *current_tab.read() == NavTab::All || *current_tab.read() == NavTab::Projects {
                        div { class: "p-6 rounded-2xl bg-gradient-to-r from-gray-900 to-indigo-950/40 border border-indigo-900/40 shadow-xl",
                            div { class: "flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-gray-800",
                                div {
                                    div { class: "flex items-center space-x-2",
                                        span { class: "text-xl", "🔬" }
                                        h3 { class: "text-lg font-bold text-white", "Neutron Star Simulation" }
                                        span { class: "px-2 py-0.5 text-xs rounded bg-purple-900/60 text-purple-300 border border-purple-700/50",
                                            "In R&D / Notes"
                                        }
                                    }
                                    p { class: "text-xs text-gray-400 mt-1",
                                        "Astrophysics numerical modeling, relativistic equation of state, and high-performance physics pipeline."
                                    }
                                }
                                div { class: "flex items-center space-x-2",
                                    span { class: "text-xs px-2.5 py-1 rounded-md bg-gray-800 text-gray-300 border border-gray-700 font-mono", "Rust / WGPU" }
                                    span { class: "text-xs px-2.5 py-1 rounded-md bg-gray-800 text-gray-300 border border-gray-700 font-mono", "Rayon Concurrency" }
                                }
                            }

                            // Optimization Strategies Grid
                            div { class: "mt-4 grid grid-cols-1 md:grid-cols-3 gap-4",
                                StrategyCard {
                                    title: "Fixed Time Step",
                                    icon: "⏳",
                                    desc: "Decouple physics calculations from frame rate to guarantee deterministic numerical stability.",
                                    status: "Decided"
                                }
                                StrategyCard {
                                    title: "Multi-threading",
                                    icon: "⚡",
                                    desc: "Offload heavy RK4 integration and gravitational tensor field steps to Rust worker threads.",
                                    status: "In Planning"
                                }
                                StrategyCard {
                                    title: "Approximations",
                                    icon: "📐",
                                    desc: "Use simplified analytical models in outer crust where ultra-high relativistic detail isn't critical.",
                                    status: "Evaluating"
                                }
                            }
                        }
                    }

                    // ROW 2: WORK & ACADEMIA SECTION
                    div { class: "grid grid-cols-1 lg:grid-cols-2 gap-6",
                        // YM Inc. POS Support Widget
                        if *current_tab.read() == NavTab::All || *current_tab.read() == NavTab::Work {
                            div { class: "p-5 rounded-2xl bg-gray-900 border border-gray-800 flex flex-col justify-between shadow-lg",
                                div {
                                    div { class: "flex items-center justify-between pb-3 border-b border-gray-800",
                                        div { class: "flex items-center space-x-2",
                                            span { "💼" }
                                            h3 { class: "font-semibold text-gray-100", "YM Inc. POS Implementation Support" }
                                        }
                                        span { class: "text-xs px-2 py-0.5 rounded bg-blue-900/50 text-blue-300 border border-blue-800",
                                            "3 Active Rollouts"
                                        }
                                    }
                                    div { class: "mt-4 space-y-3",
                                        TaskRow {
                                            title: "Terminal Provisioning — Station #104",
                                            tag: "P1 - Hardware",
                                            stage: "Testing",
                                            color: "text-yellow-400"
                                        }
                                        TaskRow {
                                            title: "API Payment Gateway Gateway Webhook Latency",
                                            tag: "P0 - Blocker",
                                            stage: "Investigating",
                                            color: "text-red-400"
                                        }
                                        TaskRow {
                                            title: "Store 42 Onboarding & Cashier Barcode Config",
                                            tag: "P2 - Rollout",
                                            stage: "Ready to Deploy",
                                            color: "text-green-400"
                                        }
                                    }
                                }
                                div { class: "mt-4 pt-3 border-t border-gray-800/80 flex items-center justify-between text-xs text-gray-400",
                                    span { "Terminal Scratchpad: Ready" }
                                    button { class: "text-indigo-400 hover:text-indigo-300 font-medium", "+ New Ticket / Note" }
                                }
                            }
                        }

                        // School Assignment Tracker Widget
                        if *current_tab.read() == NavTab::All || *current_tab.read() == NavTab::School {
                            div { class: "p-5 rounded-2xl bg-gray-900 border border-gray-800 flex flex-col justify-between shadow-lg",
                                div {
                                    div { class: "flex items-center justify-between pb-3 border-b border-gray-800",
                                        div { class: "flex items-center space-x-2",
                                            span { "📚" }
                                            h3 { class: "font-semibold text-gray-100", "Academic Course Tracker" }
                                        }
                                        span { class: "text-xs px-2 py-0.5 rounded bg-purple-900/50 text-purple-300 border border-purple-800",
                                            "Semester Active"
                                        }
                                    }
                                    div { class: "mt-4 space-y-3",
                                        CourseProgressRow {
                                            course: "CS-401 Distributed Systems",
                                            assignment: "Raft Consensus Lab",
                                            due: "Due Tomorrow",
                                            progress: 75
                                        }
                                        CourseProgressRow {
                                            course: "PHYS-350 Astrophysics",
                                            assignment: "Degeneracy Pressure Problem Set",
                                            due: "Due in 3 days",
                                            progress: 40
                                        }
                                        CourseProgressRow {
                                            course: "MATH-310 Numerical Analysis",
                                            assignment: "Runge-Kutta Error Bounds",
                                            due: "Next Monday",
                                            progress: 90
                                        }
                                    }
                                }
                                div { class: "mt-4 pt-3 border-t border-gray-800/80 flex items-center justify-between text-xs text-gray-400",
                                    span { "Overall Completion: 68%" }
                                    button { class: "text-indigo-400 hover:text-indigo-300 font-medium", "View Syllabi" }
                                }
                            }
                        }
                    }

                    // ROW 3: DEVELOPER ACTIVITY & RECREATION (GitHub, Chess, Wordle)
                    if *current_tab.read() == NavTab::All || *current_tab.read() == NavTab::Play {
                        div { class: "grid grid-cols-1 md:grid-cols-3 gap-6",
                            // GitHub Monitor
                            div { class: "p-5 rounded-2xl bg-gray-900 border border-gray-800 shadow-lg",
                                div { class: "flex items-center justify-between pb-3 border-b border-gray-800",
                                    div { class: "flex items-center space-x-2",
                                        span { "🐙" }
                                        h4 { class: "font-semibold text-gray-200 text-sm", "GitHub Monitor" }
                                    }
                                    span { class: "text-xs text-green-400 font-mono", "@DeathSurvivor02" }
                                }
                                div { class: "mt-3 space-y-2 text-xs",
                                    div { class: "p-2.5 rounded-lg bg-gray-800/60 border border-gray-700/50",
                                        p { class: "font-semibold text-gray-200", "personal-dashboard" }
                                        p { class: "text-gray-400 text-xs", "Sprint 0: Rust Dioxus setup" }
                                    }
                                    div { class: "p-2.5 rounded-lg bg-gray-800/60 border border-gray-700/50",
                                        p { class: "font-semibold text-gray-200", "0 Pending Review Requests" }
                                        p { class: "text-gray-400 text-xs", "All PRs merged & clean" }
                                    }
                                }
                            }

                            // Chess.com Daily & Live
                            div { class: "p-5 rounded-2xl bg-gray-900 border border-gray-800 shadow-lg",
                                div { class: "flex items-center justify-between pb-3 border-b border-gray-800",
                                    div { class: "flex items-center space-x-2",
                                        span { "♟️" }
                                        h4 { class: "font-semibold text-gray-200 text-sm", "Chess.com Hub" }
                                    }
                                    span { class: "text-xs px-2 py-0.5 rounded bg-emerald-900/60 text-emerald-300 font-medium", "Your Turn" }
                                }
                                div { class: "mt-3 space-y-2 text-xs",
                                    div { class: "p-2.5 rounded-lg bg-gray-800/60 border border-gray-700/50 flex justify-between items-center",
                                        div {
                                            p { class: "font-medium text-gray-200", "Daily Puzzle #1108" }
                                            p { class: "text-gray-400", "Mate in 2 • Rating 1820" }
                                        }
                                        button { class: "px-2 py-1 bg-emerald-600 hover:bg-emerald-500 text-white rounded text-xs font-semibold",
                                            "Solve"
                                        }
                                    }
                                    p { class: "text-gray-400 text-xs text-center pt-1", "1 Ongoing match vs grandmaster_bot" }
                                }
                            }

                            // Wordle Mini-Game
                            div { class: "p-5 rounded-2xl bg-gray-900 border border-gray-800 shadow-lg",
                                div { class: "flex items-center justify-between pb-3 border-b border-gray-800",
                                    div { class: "flex items-center space-x-2",
                                        span { "🟩" }
                                        h4 { class: "font-semibold text-gray-200 text-sm", "Daily Wordle" }
                                    }
                                    span { class: "text-xs text-indigo-400 font-mono", "Streak: 14 🔥" }
                                }
                                div { class: "mt-3 flex justify-center space-x-1.5",
                                    WordleTile { letter: "R", color: "bg-green-600 text-white" }
                                    WordleTile { letter: "U", color: "bg-green-600 text-white" }
                                    WordleTile { letter: "S", color: "bg-green-600 text-white" }
                                    WordleTile { letter: "T", color: "bg-yellow-500 text-white" }
                                    WordleTile { letter: "Y", color: "bg-gray-700 text-gray-300" }
                                }
                                p { class: "text-center text-xs text-gray-400 mt-3", "Next try: Guess 2 of 6" }
                            }
                        }
                    }
                }
            }
        }
    }
}

// ─── REUSABLE UI COMPONENTS ───────────────────────────────────────────────────

#[component]
fn SidebarButton(label: &'static str, icon: &'static str, active: bool, on_click: EventHandler<MouseEvent>) -> Element {
    let base_classes = "w-full flex items-center space-x-3 px-3 py-2.5 rounded-xl text-sm font-medium transition cursor-pointer";
    let active_classes = if active {
        "bg-indigo-600 text-white shadow-md shadow-indigo-600/20"
    } else {
        "text-gray-400 hover:bg-gray-800 hover:text-gray-200"
    };

    rsx! {
        button {
            class: "{base_classes} {active_classes}",
            onclick: move |e| on_click.call(e),
            span { class: "text-base", "{icon}" }
            span { "{label}" }
        }
    }
}

#[component]
fn StrategyCard(title: &'static str, icon: &'static str, desc: &'static str, status: &'static str) -> Element {
    rsx! {
        div { class: "p-4 rounded-xl bg-gray-900/90 border border-gray-800 hover:border-indigo-600/50 transition",
            div { class: "flex items-center justify-between pb-2",
                div { class: "flex items-center space-x-2",
                    span { "{icon}" }
                    h4 { class: "text-sm font-semibold text-gray-200", "{title}" }
                }
                span { class: "text-xs px-2 py-0.5 rounded bg-gray-800 text-indigo-300 font-mono", "{status}" }
            }
            p { class: "text-xs text-gray-400 leading-relaxed mt-1", "{desc}" }
        }
    }
}

#[component]
fn TaskRow(title: &'static str, tag: &'static str, stage: &'static str, color: &'static str) -> Element {
    rsx! {
        div { class: "p-3 rounded-xl bg-gray-800/60 border border-gray-700/50 flex items-center justify-between",
            div {
                p { class: "text-xs font-semibold text-gray-200", "{title}" }
                span { class: "text-xs font-mono {color}", "{tag}" }
            }
            span { class: "text-xs px-2 py-0.5 rounded bg-gray-700/60 text-gray-300", "{stage}" }
        }
    }
}

#[component]
fn CourseProgressRow(course: &'static str, assignment: &'static str, due: &'static str, progress: u32) -> Element {
    rsx! {
        div { class: "p-3 rounded-xl bg-gray-800/60 border border-gray-700/50 space-y-2",
            div { class: "flex justify-between items-center text-xs",
                span { class: "font-semibold text-gray-200", "{course}" }
                span { class: "text-indigo-400 font-medium", "{due}" }
            }
            div { class: "flex justify-between items-center text-xs text-gray-400",
                span { "{assignment}" }
                span { class: "font-mono", "{progress}%" }
            }
            // Progress Bar
            div { class: "w-full bg-gray-700 h-1.5 rounded-full overflow-hidden",
                div {
                    class: "bg-indigo-500 h-full rounded-full transition-all duration-500",
                    style: "width: {progress}%;"
                }
            }
        }
    }
}

#[component]
fn WordleTile(letter: &'static str, color: &'static str) -> Element {
    rsx! {
        div { class: "w-9 h-9 flex items-center justify-center font-bold text-sm rounded-lg {color} shadow-sm",
            "{letter}"
        }
    }
}
