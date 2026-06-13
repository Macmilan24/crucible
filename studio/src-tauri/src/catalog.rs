//! The model catalog: a curated set of GGUF models, whether each is already on
//! disk, and which one best fits this machine.

use serde::Serialize;
use std::path::PathBuf;
use sysinfo::System;
use tauri::Manager;

/// Internal description of a downloadable model. Sizes are approximate; the real
/// byte count comes from the server's `Content-Length` at download time.
pub struct Spec {
    pub id: &'static str,
    pub name: &'static str,
    pub params: &'static str,
    pub quant: &'static str,
    pub approx_size_gb: f64,
    /// Heuristic floor of total system RAM to run comfortably (file + KV + overhead).
    pub min_ram_gb: f64,
    pub url: &'static str,
    pub filename: &'static str,
    pub description: &'static str,
}

/// The curated catalog. All Q4_K_M GGUFs from bartowski on Hugging Face — the
/// same source Crucible's `download-model` uses for the 3B default.
pub fn specs() -> Vec<Spec> {
    vec![
        Spec {
            id: "qwen2.5-1.5b-instruct-q4_k_m",
            name: "Qwen2.5 1.5B Instruct",
            params: "1.5B",
            quant: "Q4_K_M",
            approx_size_gb: 1.0,
            min_ram_gb: 4.0,
            url: "https://huggingface.co/bartowski/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/Qwen2.5-1.5B-Instruct-Q4_K_M.gguf",
            filename: "Qwen2.5-1.5B-Instruct-Q4_K_M.gguf",
            description: "Smallest and fastest. Great on low-RAM machines and for snappy tool-calling.",
        },
        Spec {
            id: "qwen2.5-3b-instruct-q4_k_m",
            name: "Qwen2.5 3B Instruct",
            params: "3B",
            quant: "Q4_K_M",
            approx_size_gb: 1.9,
            min_ram_gb: 6.0,
            url: "https://huggingface.co/bartowski/Qwen2.5-3B-Instruct-GGUF/resolve/main/Qwen2.5-3B-Instruct-Q4_K_M.gguf",
            filename: "Qwen2.5-3B-Instruct-Q4_K_M.gguf",
            description: "Crucible's default. The balance of speed and quality the benchmarks were run on.",
        },
        Spec {
            id: "llama-3.2-3b-instruct-q4_k_m",
            name: "Llama 3.2 3B Instruct",
            params: "3B",
            quant: "Q4_K_M",
            approx_size_gb: 2.0,
            min_ram_gb: 6.0,
            url: "https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-GGUF/resolve/main/Llama-3.2-3B-Instruct-Q4_K_M.gguf",
            filename: "Llama-3.2-3B-Instruct-Q4_K_M.gguf",
            description: "A strong 3B alternative from Meta. Good general instruction following.",
        },
        Spec {
            id: "qwen2.5-7b-instruct-q4_k_m",
            name: "Qwen2.5 7B Instruct",
            params: "7B",
            quant: "Q4_K_M",
            approx_size_gb: 4.7,
            min_ram_gb: 10.0,
            url: "https://huggingface.co/bartowski/Qwen2.5-7B-Instruct-GGUF/resolve/main/Qwen2.5-7B-Instruct-Q4_K_M.gguf",
            filename: "Qwen2.5-7B-Instruct-Q4_K_M.gguf",
            description: "Noticeably more capable on reasoning and code. Wants a roomier machine.",
        },
        Spec {
            id: "qwen2.5-14b-instruct-q4_k_m",
            name: "Qwen2.5 14B Instruct",
            params: "14B",
            quant: "Q4_K_M",
            approx_size_gb: 9.0,
            min_ram_gb: 20.0,
            url: "https://huggingface.co/bartowski/Qwen2.5-14B-Instruct-GGUF/resolve/main/Qwen2.5-14B-Instruct-Q4_K_M.gguf",
            filename: "Qwen2.5-14B-Instruct-Q4_K_M.gguf",
            description: "High quality for a local model. Needs 20 GB+ of RAM — best on workstations.",
        },
    ]
}

pub fn spec_by_id(id: &str) -> Option<Spec> {
    specs().into_iter().find(|s| s.id == id)
}

/// Where downloaded GGUFs live: the app's data dir, under `models/`.
pub fn models_dir_path(app: &tauri::AppHandle) -> PathBuf {
    let base = app
        .path()
        .app_data_dir()
        .unwrap_or_else(|_| PathBuf::from("."));
    base.join("models")
}

#[derive(Serialize, Clone)]
pub struct ModelEntry {
    pub id: String,
    pub name: String,
    pub params: String,
    pub quant: String,
    pub approx_size_gb: f64,
    pub min_ram_gb: f64,
    pub url: String,
    pub filename: String,
    pub description: String,
    pub downloaded: bool,
    pub fits: bool,
}

fn total_ram_gb() -> f64 {
    let sys = System::new_all();
    (sys.total_memory() as f64) / 1024.0 / 1024.0 / 1024.0
}

#[tauri::command]
pub fn models_dir(app: tauri::AppHandle) -> String {
    models_dir_path(&app).to_string_lossy().to_string()
}

#[tauri::command]
pub fn get_models(app: tauri::AppHandle) -> Vec<ModelEntry> {
    let dir = models_dir_path(&app);
    let ram = total_ram_gb();
    specs()
        .into_iter()
        .map(|s| {
            let downloaded = dir.join(s.filename).exists();
            ModelEntry {
                id: s.id.to_string(),
                name: s.name.to_string(),
                params: s.params.to_string(),
                quant: s.quant.to_string(),
                approx_size_gb: s.approx_size_gb,
                min_ram_gb: s.min_ram_gb,
                url: s.url.to_string(),
                filename: s.filename.to_string(),
                description: s.description.to_string(),
                downloaded,
                fits: s.min_ram_gb <= ram,
            }
        })
        .collect()
}

/// The most capable model that still leaves ~20% RAM headroom. Falls back to the
/// smallest model if nothing fits.
#[tauri::command]
pub fn recommend_model() -> Option<String> {
    let budget = total_ram_gb() * 0.8;
    let all = specs();
    let best_fitting = all
        .iter()
        .filter(|s| s.min_ram_gb <= budget)
        .max_by(|a, b| a.min_ram_gb.partial_cmp(&b.min_ram_gb).unwrap());
    match best_fitting {
        Some(s) => Some(s.id.to_string()),
        None => all
            .iter()
            .min_by(|a, b| a.min_ram_gb.partial_cmp(&b.min_ram_gb).unwrap())
            .map(|s| s.id.to_string()),
    }
}
