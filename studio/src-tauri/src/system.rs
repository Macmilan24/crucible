//! Hardware introspection — what is this machine, and how much model can it run?

use serde::Serialize;
use sysinfo::System;

#[derive(Serialize)]
pub struct SystemInfo {
    pub os: String,
    pub os_version: String,
    pub arch: String,
    pub cpu_brand: String,
    pub cpu_cores: usize,
    pub total_ram_gb: f64,
    pub available_ram_gb: f64,
    pub apple_silicon: bool,
    pub gpu: String,
}

#[tauri::command]
pub fn get_system_info() -> SystemInfo {
    let sys = System::new_all();

    // Architecture/OS come from the compiler — reliable and dependency-free.
    let arch = std::env::consts::ARCH.to_string();
    let os = std::env::consts::OS.to_string();
    let os_version = System::os_version().unwrap_or_default();

    let cpu_brand = sys
        .cpus()
        .first()
        .map(|c| c.brand().trim().to_string())
        .filter(|s| !s.is_empty())
        .unwrap_or_else(|| "CPU".to_string());
    let cpu_cores = sys.cpus().len();

    // sysinfo reports memory in bytes.
    let total_ram_gb = bytes_to_gb(sys.total_memory());
    let available_ram_gb = bytes_to_gb(sys.available_memory());

    let apple_silicon = os == "macos" && arch == "aarch64";

    // GPU detection is intentionally best-effort: on Apple Silicon the GPU shares
    // system RAM (unified memory) and llama.cpp uses Metal automatically; elsewhere
    // the engine probes the device at load time.
    let gpu = if apple_silicon {
        "Apple integrated GPU · Metal · unified memory".to_string()
    } else if os == "macos" {
        "Integrated GPU · Metal".to_string()
    } else {
        "Detected by llama.cpp at model load (CPU / CUDA)".to_string()
    };

    SystemInfo {
        os,
        os_version,
        arch,
        cpu_brand,
        cpu_cores,
        total_ram_gb,
        available_ram_gb,
        apple_silicon,
        gpu,
    }
}

fn bytes_to_gb(bytes: u64) -> f64 {
    (bytes as f64) / 1024.0 / 1024.0 / 1024.0
}
