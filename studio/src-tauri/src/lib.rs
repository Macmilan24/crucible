//! Crucible Studio — desktop backend.
//!
//! A thin native layer over the work Product 1 already ships. The web UI calls
//! these commands to inspect the machine, manage local GGUF models, and drive
//! the `crucible serve` OpenAI-compatible server. Inference itself stays in the
//! Python runtime — this is the *face*, not a second engine.

mod catalog;
mod download;
mod server;
mod system;

use server::ServerState;

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .manage(ServerState::default())
        .invoke_handler(tauri::generate_handler![
            system::get_system_info,
            catalog::get_models,
            catalog::recommend_model,
            catalog::models_dir,
            download::download_model,
            download::delete_model,
            server::crucible_available,
            server::start_server,
            server::stop_server,
            server::server_status,
        ])
        .run(tauri::generate_context!())
        .expect("error while running Crucible Studio");
}
