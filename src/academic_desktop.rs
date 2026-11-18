#![windows_subsystem = "windows"]

use std::fs;
use std::io::Write;
#[cfg(windows)]
use std::os::windows::process::CommandExt;
use std::path::{Path, PathBuf};
use std::process::{Command, Stdio};
use tao::{
    dpi::LogicalSize,
    event::{Event, WindowEvent},
    event_loop::{ControlFlow, EventLoopBuilder},
    window::WindowBuilder,
};
use wry::WebViewBuilder;

enum UserEvent {
    SyncCompleted(String),
}

fn resolve_dashboard_dir() -> PathBuf {
    if let Ok(exe_path) = std::env::current_exe() {
        for ancestor in exe_path.ancestors().skip(1) {
            if ancestor.join("index.html").is_file() {
                return ancestor.to_path_buf();
            }
        }
    }
    if let Ok(cwd) = std::env::current_dir() {
        if cwd.join("index.html").is_file() {
            return cwd;
        }
    }
    PathBuf::from(env!("CARGO_MANIFEST_DIR"))
}

fn find_python_exe() -> Option<PathBuf> {
    if let Ok(explicit) = std::env::var("PYTHON_EXE") {
        let p = PathBuf::from(explicit);
        if p.is_file() {
            return Some(p);
        }
    }

    if let Ok(appdata) = std::env::var("APPDATA") {
        let uv_dir = Path::new(&appdata).join("uv").join("python");
        if let Ok(entries) = fs::read_dir(uv_dir) {
            for entry in entries.flatten() {
                let candidate = entry.path().join("python.exe");
                if candidate.is_file() {
                    return Some(candidate);
                }
            }
        }
    }

    if let Ok(local_app) = std::env::var("LOCALAPPDATA") {
        let py_root = Path::new(&local_app).join("Programs").join("Python");
        if let Ok(entries) = fs::read_dir(py_root) {
            for entry in entries.flatten() {
                let candidate = entry.path().join("python.exe");
                if candidate.is_file() {
                    return Some(candidate);
                }
            }
        }
    }

    let venv_fallback = PathBuf::from(
        r"C:\Users\bynoe\Music\Personal-Workspace02\School\Centennial_College\Semester 5\Data  Warehouse\COMP309_Bicycle_Theft_Project\.venv\Scripts\python.exe",
    );
    if venv_fallback.is_file() {
        return Some(venv_fallback);
    }

    if let Ok(path_var) = std::env::var("PATH") {
        for dir in std::env::split_paths(&path_var) {
            let dir_str = dir.to_string_lossy().to_lowercase();
            if dir_str.contains("windowsapps") {
                continue;
            }
            let candidate = dir.join("python.exe");
            if candidate.is_file() {
                return Some(candidate);
            }
        }
    }

    None
}

fn run_school_sync(dashboard_dir: &Path) {
    let script_path = dashboard_dir.join("sync_school.py");
    if !script_path.is_file() {
        return;
    }
    let Some(python_exe) = find_python_exe() else {
        return;
    };
    let mut cmd = Command::new(python_exe);
    cmd.arg(&script_path).current_dir(dashboard_dir);
    #[cfg(windows)]
    cmd.creation_flags(0x08000000);
    let _ = cmd.output();
}

fn copy_to_windows_clipboard(text: &str) {
    if text.is_empty() {
        return;
    }
    let mut cmd = Command::new("clip");
    cmd.stdin(Stdio::piped());
    #[cfg(windows)]
    cmd.creation_flags(0x08000000);
    if let Ok(mut child) = cmd.spawn() {
        if let Some(mut stdin) = child.stdin.take() {
            let _ = stdin.write_all(text.as_bytes());
        }
        let _ = child.wait();
    }
}

fn reveal_in_explorer(file_path: &str) {
    if file_path.is_empty() {
        return;
    }
    let clean = file_path.replace('/', "\\");
    copy_to_windows_clipboard(&clean);
    let p = Path::new(&clean);
    let mut cmd = Command::new("explorer.exe");
    #[cfg(windows)]
    {
        if p.exists() {
            cmd.raw_arg(format!("/select,\"{}\"", clean));
        } else if let Some(parent) = p.parent() {
            cmd.arg(parent);
        } else {
            return;
        }
    }
    let _ = cmd.spawn();
}

fn open_in_browser(url: &str, browser: &str) {
    let target_url = if url.is_empty() {
        "https://luminate.centennialcollege.ca/ultra/course"
    } else {
        url
    };

    if browser.eq_ignore_ascii_case("chrome") {
        let chrome_candidates = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        ];
        for path in chrome_candidates {
            if Path::new(path).is_file() {
                let _ = Command::new(path)
                    .arg("--profile-directory=Default")
                    .arg(target_url)
                    .spawn();
                return;
            }
        }
    } else if browser.eq_ignore_ascii_case("opera") {
        if let Ok(local_app) = std::env::var("LOCALAPPDATA") {
            let opera_gx = Path::new(&local_app)
                .join("Programs")
                .join("Opera GX")
                .join("opera.exe");
            if opera_gx.is_file() {
                let _ = Command::new(opera_gx).arg(target_url).spawn();
                return;
            }
            let opera_std = Path::new(&local_app)
                .join("Programs")
                .join("Opera")
                .join("opera.exe");
            if opera_std.is_file() {
                let _ = Command::new(opera_std).arg(target_url).spawn();
                return;
            }
        }
    }

    let mut cmd = Command::new("cmd");
    cmd.args(["/c", "start", "", target_url]);
    #[cfg(windows)]
    cmd.creation_flags(0x08000000);
    let _ = cmd.spawn();
}

fn read_json_or_null(path: &Path) -> String {
    fs::read_to_string(path)
        .ok()
        .and_then(|raw| serde_json::from_str::<serde_json::Value>(&raw).ok())
        .map(|val| val.to_string())
        .unwrap_or_else(|| "null".to_string())
}

fn spawn_background_sync(
    dashboard_dir: PathBuf,
    state_path: PathBuf,
    proxy: tao::event_loop::EventLoopProxy<UserEvent>,
) {
    std::thread::spawn(move || {
        run_school_sync(&dashboard_dir);
        let state_json = read_json_or_null(&state_path);
        let _ = proxy.send_event(UserEvent::SyncCompleted(state_json));
    });
}

fn main() -> wry::Result<()> {
    let dashboard_dir = resolve_dashboard_dir();
    let config_path = dashboard_dir.join("school_sync_config.json");
    let state_path = dashboard_dir.join("academic_state.json");

    let should_auto_sync = fs::read_to_string(&config_path)
        .ok()
        .and_then(|raw| serde_json::from_str::<serde_json::Value>(&raw).ok())
        .and_then(|v| v.get("auto_sync_on_startup").and_then(|b| b.as_bool()))
        .unwrap_or(true);

    let html_content = fs::read_to_string(dashboard_dir.join("index.html"))
        .unwrap_or_else(|_| include_str!("../index.html").to_string());

    let initial_state_json = read_json_or_null(&state_path);
    let initial_config_json = read_json_or_null(&config_path);

    let init_script = format!(
        "window.__PERSISTED_ACADEMIC_STATE__ = {};\nwindow.__SCHOOL_SYNC_CONFIG__ = {};",
        initial_state_json, initial_config_json
    );

    let event_loop = EventLoopBuilder::<UserEvent>::with_user_event().build();
    let proxy = event_loop.create_proxy();

    let main_window = WindowBuilder::new()
        .with_title("Personal Workspace & Academic Record - Centennial College")
        .with_theme(None)
        .with_visible(true)
        .with_inner_size(LogicalSize::new(1280.0, 840.0))
        .with_min_inner_size(LogicalSize::new(820.0, 600.0))
        .build(&event_loop)
        .expect("Failed to create desktop window");
    let main_window_id = main_window.id();

    let dir_for_ipc = dashboard_dir.clone();
    let state_path_for_ipc = state_path.clone();
    let config_path_for_ipc = config_path.clone();
    let proxy_for_startup = proxy.clone();

    let main_webview = WebViewBuilder::new(&main_window)
        .with_initialization_script(&init_script)
        .with_ipc_handler(move |req| {
            let body = req.body();
            let Ok(msg) = serde_json::from_str::<serde_json::Value>(body) else {
                return;
            };
            match msg.get("type").and_then(|v| v.as_str()) {
                Some("save_state") => {
                    if let Some(state_val) = msg.get("state") {
                        if let Ok(pretty) = serde_json::to_string_pretty(state_val) {
                            let _ = fs::write(&state_path_for_ipc, pretty);
                        }
                    }
                }
                Some("save_sync_config") => {
                    let mut cfg = fs::read_to_string(&config_path_for_ipc)
                        .ok()
                        .and_then(|raw| serde_json::from_str::<serde_json::Value>(&raw).ok())
                        .unwrap_or_else(|| serde_json::json!({}));
                    if let Some(url) = msg.get("ics_feed_url").and_then(|v| v.as_str()) {
                        cfg["ics_feed_url"] = serde_json::Value::String(url.to_string());
                    }
                    if let Some(rss_arr) = msg.get("rss_feeds") {
                        if rss_arr.is_array() {
                            cfg["rss_feeds"] = rss_arr.clone();
                        }
                    }
                    if let Some(gh) = msg.get("github_username").and_then(|v| v.as_str()) {
                        cfg["github_username"] = serde_json::Value::String(gh.to_string());
                    }
                    if let Some(ch) = msg.get("chess_username").and_then(|v| v.as_str()) {
                        cfg["chess_username"] = serde_json::Value::String(ch.to_string());
                    }
                    if let Ok(pretty) = serde_json::to_string_pretty(&cfg) {
                        let _ = fs::write(&config_path_for_ipc, pretty);
                    }
                    spawn_background_sync(
                        dir_for_ipc.clone(),
                        state_path_for_ipc.clone(),
                        proxy.clone(),
                    );
                }
                Some("run_sync") => {
                    spawn_background_sync(
                        dir_for_ipc.clone(),
                        state_path_for_ipc.clone(),
                        proxy.clone(),
                    );
                }
                Some("stage_submission") => {
                    let artifact_path = msg.get("artifact_path").and_then(|v| v.as_str()).unwrap_or("");
                    copy_to_windows_clipboard(artifact_path);
                }
                Some("open_browser") => {
                    let url = msg.get("url").and_then(|v| v.as_str()).unwrap_or("https://luminate.centennialcollege.ca/ultra/course");
                    let browser = msg.get("browser").and_then(|v| v.as_str()).unwrap_or("chrome");
                    let artifact_path = msg.get("artifact_path").and_then(|v| v.as_str()).unwrap_or("");
                    if !artifact_path.is_empty() {
                        copy_to_windows_clipboard(artifact_path);
                    }
                    open_in_browser(url, browser);
                }
                Some("reveal_file") => {
                    if let Some(p) = msg.get("path").and_then(|v| v.as_str()) {
                        reveal_in_explorer(p);
                    }
                }
                _ => {}
            }
        })
        .with_html(html_content)
        .build()?;

    main_window.set_visible(true);
    main_window.set_focus();

    if should_auto_sync {
        spawn_background_sync(dashboard_dir, state_path, proxy_for_startup);
    }

    event_loop.run(move |event, _, control_flow| {
        *control_flow = ControlFlow::Wait;
        match event {
            Event::WindowEvent {
                window_id,
                event: WindowEvent::CloseRequested,
                ..
            } => {
                if window_id == main_window_id {
                    *control_flow = ControlFlow::Exit;
                }
            }
            Event::UserEvent(UserEvent::SyncCompleted(state_json)) => {
                let js = format!(
                    "window.__applyExternalSyncState && window.__applyExternalSyncState({});",
                    state_json
                );
                let _ = main_webview.evaluate_script(&js);
            }
            _ => {}
        }
    });
}
