//! Start / stop / inspect the `crucible serve` OpenAI-compatible server.
//!
//! Studio does not run inference itself — it supervises the Python runtime that
//! Product 1 already ships. A released app drives a bundled sidecar; a `tauri dev`
//! build falls back to the user's installed `crucible` CLI.

use serde::Serialize;
use std::path::PathBuf;
use std::process::{Child, Command, Stdio};
use std::sync::Mutex;
use std::time::Instant;
use tauri::{AppHandle, State};

/// A live server process plus the facts the UI wants to show about it.
struct Running {
    child: Child,
    model_id: String,
    model_label: String,
    port: u16,
    started_at: Instant,
}

#[derive(Default)]
pub struct ServerState {
    inner: Mutex<Option<Running>>,
}

/// Resolve the crucible runtime to launch.
///
/// 1. The **bundled sidecar** — Tauri places the frozen `crucible` binary next to
///    the app executable (via `externalBin`), so a released app needs nothing
///    installed. This is the one-download path.
/// 2. Dev fallback — a `crucible` CLI on the system, for `tauri dev` builds that
///    don't ship a sidecar. (GUI apps inherit a minimal PATH, so we check the
///    common install locations explicitly before scanning PATH.)
fn find_runtime() -> Option<PathBuf> {
    // 1. Bundled sidecar alongside the app binary.
    if let Ok(exe) = std::env::current_exe() {
        if let Some(dir) = exe.parent() {
            let name = if cfg!(windows) {
                "crucible-server.exe"
            } else {
                "crucible-server"
            };
            let p = dir.join(name);
            if p.exists() {
                return Some(p);
            }
        }
    }
    // 2. Dev fallback: a `crucible` CLI installed on the system.
    if let Ok(home) = std::env::var("HOME") {
        let home = PathBuf::from(home);
        for rel in [".local/bin/crucible", ".cargo/bin/crucible"] {
            let p = home.join(rel);
            if p.exists() {
                return Some(p);
            }
        }
    }
    for fixed in ["/opt/homebrew/bin/crucible", "/usr/local/bin/crucible"] {
        let p = PathBuf::from(fixed);
        if p.exists() {
            return Some(p);
        }
    }
    if let Ok(path) = std::env::var("PATH") {
        for dir in std::env::split_paths(&path) {
            let p = dir.join("crucible");
            if p.exists() {
                return Some(p);
            }
        }
    }
    None
}

#[tauri::command]
pub fn crucible_available() -> bool {
    find_runtime().is_some()
}

#[derive(Serialize)]
pub struct ServerStatus {
    pub running: bool,
    pub port: u16,
    pub base_url: String,
    /// Id of the model the server was started with (matches the catalog), if running.
    pub model_id: Option<String>,
    /// Human-readable model name, if running.
    pub model_label: Option<String>,
    /// Seconds since the server started, if running.
    pub uptime_secs: u64,
}

const DEFAULT_PORT: u16 = 8000;

#[tauri::command]
pub fn start_server(
    app: AppHandle,
    state: State<'_, ServerState>,
    model_id: String,
    port: Option<u16>,
) -> Result<String, String> {
    let mut guard = state.inner.lock().map_err(|e| e.to_string())?;
    if guard.is_some() {
        return Err("server is already running".to_string());
    }

    let crucible = find_runtime().ok_or_else(|| {
        "Crucible runtime not found — the bundled release ships it; for a dev build, install the crucible CLI."
            .to_string()
    })?;
    let spec =
        crate::catalog::spec_by_id(&model_id).ok_or_else(|| "unknown model id".to_string())?;
    let model_path = crate::catalog::models_dir_path(&app).join(spec.filename);
    if !model_path.exists() {
        return Err("that model isn't downloaded yet".to_string());
    }
    let port = port.unwrap_or(DEFAULT_PORT);

    let child = Command::new(&crucible)
        .arg("serve")
        .arg("--model")
        .arg(&model_path)
        .arg("--host")
        .arg("127.0.0.1")
        .arg("--port")
        .arg(port.to_string())
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .spawn()
        .map_err(|e| format!("failed to launch crucible: {e}"))?;

    *guard = Some(Running {
        child,
        model_id: spec.id.to_string(),
        model_label: spec.name.to_string(),
        port,
        started_at: Instant::now(),
    });
    Ok(base_url(port))
}

#[tauri::command]
pub fn stop_server(state: State<'_, ServerState>) -> Result<(), String> {
    let mut guard = state.inner.lock().map_err(|e| e.to_string())?;
    if let Some(mut running) = guard.take() {
        let _ = running.child.kill();
        let _ = running.child.wait();
    }
    Ok(())
}

#[tauri::command]
pub fn server_status(state: State<'_, ServerState>) -> ServerStatus {
    let mut guard = match state.inner.lock() {
        Ok(g) => g,
        Err(_) => return stopped_status(DEFAULT_PORT),
    };

    // A process that has exited on its own should no longer count as running.
    let still_running = match guard.as_mut() {
        Some(r) => matches!(r.child.try_wait(), Ok(None)),
        None => false,
    };

    if !still_running {
        *guard = None;
        return stopped_status(DEFAULT_PORT);
    }

    let r = guard.as_ref().expect("checked running");
    ServerStatus {
        running: true,
        port: r.port,
        base_url: base_url(r.port),
        model_id: Some(r.model_id.clone()),
        model_label: Some(r.model_label.clone()),
        uptime_secs: r.started_at.elapsed().as_secs(),
    }
}

fn stopped_status(port: u16) -> ServerStatus {
    ServerStatus {
        running: false,
        port,
        base_url: base_url(port),
        model_id: None,
        model_label: None,
        uptime_secs: 0,
    }
}

fn base_url(port: u16) -> String {
    format!("http://127.0.0.1:{port}/v1")
}
