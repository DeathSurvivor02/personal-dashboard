use dioxus::prelude::*;

fn main() {
    dioxus::launch(App);
}

#[derive(Clone, Copy, PartialEq)]
enum Theme {
    ObsidianEmerald,
    MidnightBlue,
    MinimalistSlate,
    CarbonCrimson,
    DeepViolet,
    AbyssalTeal,
}

impl Theme {
    fn colors(&self) -> (&'static str, &'static str, &'static str, &'static str, &'static str) {
        match self {
            Theme::ObsidianEmerald => ("#09090B", "#18181B", "#10B981", "#06B6D4", "#F4F4F5"),
            Theme::MidnightBlue => ("#0B0F17", "#111827", "#3B82F6", "#6366F1", "#F8FAFC"),
            Theme::MinimalistSlate => ("#FFFFFF", "#F1F5F9", "#4F46E5", "#64748B", "#0F172A"),
            Theme::CarbonCrimson => ("#0A0A0C", "#17171B", "#EF4444", "#F59E0B", "#F8FAFC"),
            Theme::DeepViolet => ("#0D0B14", "#181424", "#8B5CF6", "#EC4899", "#F5F3FF"),
            Theme::AbyssalTeal => ("#071314", "#0E2224", "#14B8A6", "#EAB308", "#F0FDFA"),
        }
    }
}

#[component]
fn App() -> Element {
    let mut theme = use_signal(|| Theme::ObsidianEmerald);
    let (bg, surface, primary, accent, text) = theme().colors();

    rsx! {
        document::Link {
            rel: "stylesheet",
            href: "https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css"
        }
        style {
            {format!(
                "body {{ background-color: {bg}; color: {text}; font-family: -apple-system, BlinkMacSystemFont, \"Segoe UI\", Roboto, \"Inter\", sans-serif; margin: 0; }} .theme-surface {{ background-color: {surface}; }} .theme-primary {{ color: {primary}; }} .theme-accent {{ color: {accent}; }} .custom-scrollbar::-webkit-scrollbar {{ width: 5px; }} .custom-scrollbar::-webkit-scrollbar-thumb {{ background-color: #1E293B; border-radius: 9999px; }}"
            )}
        }

        div { class: "h-screen w-screen overflow-hidden flex flex-col antialiased text-xs select-none",
            style: "background-color: {bg}; color: {text};",
            // ─── MINIMALIST TOP HEADER (Linear Style) ─────────────────────────
            header { class: "h-12 px-5 py-2.5 border-b border-[#1E293B] flex items-center justify-between",
                style: "background-color: {surface};",
                div { class: "flex items-center space-x-2.5",
                    div { class: "w-6 h-6 rounded flex items-center justify-center font-bold text-xs",
                        style: "background-color: {primary}22; border: 1px solid {primary}66; color: {primary};",
                        "⌘"
                    }
                    span { class: "font-semibold tracking-tight", "Personal Command" }
                    span { class: "text-gray-500 font-mono", "/" }
                    span { class: "text-gray-400 font-mono", "dashboard.os" }
                }

                div { class: "flex items-center space-x-3",
                    select {
                        class: "px-2 py-1 rounded bg-[#121826] border border-[#1E293B] text-gray-200 text-[11px] font-mono outline-none",
                        onchange: move |evt| {
                            let val = evt.value();
                            theme.set(match val.as_str() {
                                "midnight" => Theme::MidnightBlue,
                                "slate" => Theme::MinimalistSlate,
                                "crimson" => Theme::CarbonCrimson,
                                "violet" => Theme::DeepViolet,
                                "teal" => Theme::AbyssalTeal,
                                _ => Theme::ObsidianEmerald,
                            });
                        },
                        option { value: "obsidian", "Obsidian & Emerald" }
                        option { value: "midnight", "Midnight & Electric Blue" }
                        option { value: "slate", "Minimalist Slate" }
                        option { value: "crimson", "Carbon & Crimson" }
                        option { value: "violet", "Deep Violet & Rose" }
                        option { value: "teal", "Abyssal Teal & Gold" }
                    }
                    div { class: "flex items-center space-x-1.5 px-2 py-0.5 rounded bg-[#121826] border border-[#1E293B]",
                        span { class: "w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" }
                        span { class: "text-gray-300 font-medium text-[11px]", "Deep Work" }
                    }
                    span { class: "text-gray-400 font-mono text-[11px]", "Rust Dioxus • Desktop" }
                }
            }

            // ─── SPLIT DUAL-PANE BODY ─────────────────────────────────────────
            div { class: "flex-1 flex overflow-hidden",

                // ─── LEFT PANE: OPERATIONS & ACADEMICS (40% width) ───────────
                div { class: "w-2/5 min-w-[340px] max-w-[500px] h-full flex flex-col border-r border-[#1E293B] bg-[#0E131F] overflow-y-auto custom-scrollbar p-5 space-y-5",
                    
                    div { class: "flex items-center justify-between pb-2 border-b border-[#1E293B]",
                        div { class: "flex items-center space-x-2",
                            span { class: "w-2 h-2 rounded bg-indigo-500" }
                            h2 { class: "font-semibold text-[11px] tracking-wider uppercase text-gray-400 font-mono", "Operations & Academics" }
                        }
                        span { class: "text-[11px] font-mono text-indigo-400", "Pane 01" }
                    }

                    // YM Inc. POS Support Section
                    div { class: "space-y-3",
                        div { class: "flex items-center justify-between",
                            div { class: "flex items-center space-x-2",
                                span { "" }
                                h3 { class: "font-semibold text-gray-200", "YM Inc. POS Support" }
                            }
                            span { class: "text-[10px] font-mono px-2 py-0.5 rounded bg-indigo-950 text-indigo-300 border border-indigo-800/40", "3 Active" }
                        }

                        div { class: "space-y-2",
                            PosTicket {
                                priority: "P0 Blocker",
                                status: "Investigating",
                                code: "POS-204",
                                title: "Payment Gateway Webhook Latency Spike",
                                desc: "Store terminal timeout on auth callback during batch push",
                                badge_bg: "bg-rose-950 text-rose-300",
                                status_color: "text-red-400"
                            }
                            PosTicket {
                                priority: "P1 Hardware",
                                status: "In Testing",
                                code: "POS-189",
                                title: "Terminal Provisioning — Station #104",
                                desc: "IP assigned, pending barcode scanner test handshake",
                                badge_bg: "bg-amber-950 text-amber-300",
                                status_color: "text-yellow-400"
                            }
                            PosTicket {
                                priority: "P2 Rollout",
                                status: "Ready",
                                code: "POS-177",
                                title: "Store 42 Client Onboarding & Receipt Profile",
                                desc: "Cashier training checklist & thermal printer mapping",
                                badge_bg: "bg-emerald-950 text-emerald-300",
                                status_color: "text-emerald-400"
                            }
                        }
                    }

                    // Academic Course Tracker Section
                    div { class: "space-y-3 pt-2",
                        div { class: "flex items-center justify-between",
                            div { class: "flex items-center space-x-2",
                                span { "" }
                                h3 { class: "font-semibold text-gray-200", "Academic Course Progress" }
                            }
                            span { class: "text-[10px] font-mono text-gray-400", "Fall 2026" }
                        }

                        div { class: "space-y-2.5",
                            CourseItem {
                                course: "CS-401 Distributed Systems",
                                assignment: "Raft Consensus Lab",
                                due: "Due Tomorrow",
                                due_color: "text-red-400",
                                progress: 75
                            }
                            CourseItem {
                                course: "PHYS-350 Astrophysics",
                                assignment: "Degeneracy Pressure Problem Set",
                                due: "Due in 3 days",
                                due_color: "text-yellow-400",
                                progress: 40
                            }
                            CourseItem {
                                course: "MATH-310 Numerical Analysis",
                                assignment: "Runge-Kutta 4th Order Error Bounds",
                                due: "Next Monday",
                                due_color: "text-gray-400",
                                progress: 90
                            }
                        }
                    }
                }

                // ─── RIGHT PANE: ENGINEERING LAB & RECREATION (60% width) ─────
                div { class: "flex-1 h-full bg-[#0A0D14] flex flex-col overflow-y-auto custom-scrollbar p-6 space-y-6",
                    
                    div { class: "flex items-center justify-between pb-2 border-b border-[#1E293B]",
                        div { class: "flex items-center space-x-2",
                            span { class: "w-2 h-2 rounded bg-sky-400" }
                            h2 { class: "font-semibold text-[11px] tracking-wider uppercase text-gray-400 font-mono", "Engineering Lab & Recreation" }
                        }
                        span { class: "text-[11px] font-mono text-sky-400", "Pane 02" }
                    }

                    // Featured Project: Neutron Star Simulation
                    div { class: "p-4 rounded-xl bg-[#121826] border border-[#1E293B] space-y-3 shadow-md",
                        div { class: "flex items-center justify-between pb-2 border-b border-[#1E293B]",
                            div {
                                div { class: "flex items-center space-x-2",
                                    span { "" }
                                    h3 { class: "font-bold text-white text-sm", "Neutron Star Simulation" }
                                    span { class: "text-[10px] font-mono px-2 py-0.5 rounded bg-indigo-950 text-indigo-300 border border-indigo-800/40", "Active R&D" }
                                }
                                p { class: "text-[11px] text-gray-400 mt-0.5", "Astrophysics numerical modeling, relativistic equation of state & decoupled physics pipeline." }
                            }
                            div { class: "flex space-x-1.5",
                                span { class: "text-[10px] font-mono px-2 py-0.5 rounded bg-[#0A0D14] text-gray-300 border border-[#1E293B]", "Rust" }
                                span { class: "text-[10px] font-mono px-2 py-0.5 rounded bg-[#0A0D14] text-gray-300 border border-[#1E293B]", "WGPU" }
                                span { class: "text-[10px] font-mono px-2 py-0.5 rounded bg-[#0A0D14] text-sky-400 border border-[#1E293B]", "Rayon" }
                            }
                        }

                        // Optimization Strategies Notes
                        div { class: "space-y-2",
                            div { class: "flex justify-between items-center text-[11px]",
                                span { class: "font-semibold text-gray-300 uppercase tracking-wider font-mono", "Optimization Strategies" }
                                span { class: "text-gray-400", "Status: Taking notes on options" }
                            }

                            div { class: "grid grid-cols-1 md:grid-cols-3 gap-2",
                                StrategyCard {
                                    title: "Ready - Fixed Step",
                                    badge: "Decided",
                                    badge_class: "bg-emerald-950 text-emerald-300 border-emerald-800/40",
                                    desc: "Decouple physics calculations from frame rate."
                                }
                                StrategyCard {
                                    title: "Multi-thread",
                                    badge: "Planning",
                                    badge_class: "bg-amber-950 text-amber-300 border-amber-800/40",
                                    desc: "Offload heavy computations to worker threads."
                                }
                                StrategyCard {
                                    title: "Approx.",
                                    badge: "Evaluating",
                                    badge_class: "bg-indigo-950 text-indigo-300 border-indigo-800/40",
                                    desc: "Use simplified models where high detail isn't critical."
                                }
                            }
                        }
                    }

                    // Lower Row: GitHub, Chess.com & Wordle
                    div { class: "grid grid-cols-1 md:grid-cols-3 gap-3",
                        
                        // GitHub Card
                        div { class: "p-3 rounded-xl bg-[#0E131F] border border-[#1E293B] space-y-2",
                            div { class: "flex justify-between items-center pb-1.5 border-b border-[#1E293B]",
                                span { class: "font-semibold text-white text-xs", "GitHub" }
                                span { class: "text-[10px] font-mono text-sky-400", "@DeathSurvivor02" }
                            }
                            div { class: "space-y-1.5 text-[11px]",
                                div { class: "p-1.5 rounded bg-[#121826] border border-[#1E293B] flex justify-between",
                                    span { class: "text-gray-200", "personal-dashboard" }
                                    span { class: "text-emerald-400 font-mono", "clean" }
                                }
                                div { class: "p-1.5 rounded bg-[#121826] border border-[#1E293B] flex justify-between",
                                    span { class: "text-gray-400", "Open Pull Requests" }
                                    span { class: "text-white font-mono", "0" }
                                }
                            }
                        }

                        // Chess.com Card
                        div { class: "p-3 rounded-xl bg-[#0E131F] border border-[#1E293B] space-y-2",
                            div { class: "flex justify-between items-center pb-1.5 border-b border-[#1E293B]",
                                span { class: "font-semibold text-white text-xs", "Chess.com" }
                                span { class: "text-[10px] font-mono px-1.5 py-0.2 rounded bg-emerald-950 text-emerald-300", "Your Turn" }
                            }
                            div { class: "p-2 rounded bg-[#121826] border border-[#1E293B] flex justify-between items-center",
                                div {
                                    p { class: "font-semibold text-white text-xs", "Daily Puzzle" }
                                    p { class: "text-[10px] text-gray-400", "Mate in 2" }
                                }
                                button { class: "px-2 py-1 rounded bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-[11px]", "Solve" }
                            }
                        }

                        // Wordle Card
                        div { class: "p-3 rounded-xl bg-[#0E131F] border border-[#1E293B] space-y-2",
                            div { class: "flex justify-between items-center pb-1.5 border-b border-[#1E293B]",
                                span { class: "font-semibold text-white text-xs", "Daily Wordle" }
                                span { class: "text-[10px] font-mono text-indigo-400", "Streak: 14 " }
                            }
                            div { class: "flex justify-center space-x-1 pt-1",
                                div { class: "w-6 h-6 rounded bg-emerald-600 text-white font-bold flex items-center justify-center text-xs", "R" }
                                div { class: "w-6 h-6 rounded bg-emerald-600 text-white font-bold flex items-center justify-center text-xs", "U" }
                                div { class: "w-6 h-6 rounded bg-emerald-600 text-white font-bold flex items-center justify-center text-xs", "S" }
                                div { class: "w-6 h-6 rounded bg-amber-500 text-white font-bold flex items-center justify-center text-xs", "T" }
                                div { class: "w-6 h-6 rounded bg-[#121826] text-gray-400 border border-[#1E293B] flex items-center justify-center text-xs font-mono", "Y" }
                            }
                            p { class: "text-center text-[10px] text-gray-400 font-mono", "Guess 2 of 6" }
                        }
                    }

                }
            }
        }
    }
}

// ─── REUSABLE SUB-COMPONENTS ──────────────────────────────────────────────────

#[component]
fn PosTicket(priority: &'static str, status: &'static str, code: &'static str, title: &'static str, desc: &'static str, badge_bg: &'static str, status_color: &'static str) -> Element {
    rsx! {
        div { class: "p-2.5 rounded-lg bg-[#121826] border border-[#1E293B] space-y-1",
            div { class: "flex justify-between items-center",
                span { class: "text-[10px] font-mono px-1.5 py-0.2 rounded {badge_bg} font-semibold", "{priority}" }
                span { class: "text-[10px] font-mono {status_color}", "{status}" }
            }
            p { class: "font-medium text-gray-200", "{title}" }
            p { class: "text-[11px] text-gray-400", "{desc}" }
        }
    }
}

#[component]
fn CourseItem(course: &'static str, assignment: &'static str, due: &'static str, due_color: &'static str, progress: u32) -> Element {
    rsx! {
        div { class: "p-2.5 rounded-lg bg-[#121826] border border-[#1E293B] space-y-1.5",
            div { class: "flex justify-between items-center",
                span { class: "font-semibold text-gray-200", "{course}" }
                span { class: "text-[11px] font-mono font-semibold {due_color}", "{due}" }
            }
            div { class: "flex justify-between text-[11px] text-gray-400",
                span { "{assignment}" }
                span { class: "font-mono text-indigo-400 font-semibold", "{progress}%" }
            }
            div { class: "w-full bg-[#0A0D14] h-1.5 rounded-full overflow-hidden border border-[#1E293B]",
                div {
                    class: "bg-indigo-500 h-full rounded-full transition-all duration-500",
                    style: "width: {progress}%;"
                }
            }
        }
    }
}

#[component]
fn StrategyCard(title: &'static str, badge: &'static str, badge_class: &'static str, desc: &'static str) -> Element {
    rsx! {
        div { class: "p-3 rounded-lg bg-[#0A0D14] border border-[#1E293B] space-y-1",
            div { class: "flex justify-between items-center",
                span { class: "font-semibold text-white", "{title}" }
                span { class: "text-[9px] font-mono px-1.5 py-0.2 rounded border {badge_class}", "{badge}" }
            }
            p { class: "text-[11px] text-gray-400 leading-snug", "{desc}" }
        }
    }
}
