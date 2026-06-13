//! Streaming GGUF downloads with progress events.
//!
//! Writes to a `.part` file and renames on success, so a partial file is never
//! mistaken for a complete model. Progress is pushed to the UI via the
//! `download-progress` event (throttled to keep the bridge quiet).

use futures_util::StreamExt;
use serde::Serialize;
use tauri::{AppHandle, Emitter};
use tokio::io::AsyncWriteExt;

#[derive(Serialize, Clone)]
struct Progress {
    id: String,
    downloaded: u64,
    total: u64,
    pct: f64,
    done: bool,
    error: Option<String>,
}

#[tauri::command]
pub async fn download_model(app: AppHandle, id: String) -> Result<(), String> {
    let spec = crate::catalog::spec_by_id(&id).ok_or_else(|| "unknown model id".to_string())?;
    let dir = crate::catalog::models_dir_path(&app);
    tokio::fs::create_dir_all(&dir)
        .await
        .map_err(|e| e.to_string())?;
    let final_path = dir.join(spec.filename);
    let part_path = dir.join(format!("{}.part", spec.filename));

    let result = stream_to_file(&app, &id, spec.url, &part_path).await;

    match result {
        Ok(downloaded) => {
            tokio::fs::rename(&part_path, &final_path)
                .await
                .map_err(|e| e.to_string())?;
            let _ = app.emit(
                "download-progress",
                Progress {
                    id,
                    downloaded,
                    total: downloaded,
                    pct: 100.0,
                    done: true,
                    error: None,
                },
            );
            Ok(())
        }
        Err(e) => {
            // Leave no half-file behind on failure.
            let _ = tokio::fs::remove_file(&part_path).await;
            let _ = app.emit(
                "download-progress",
                Progress {
                    id,
                    downloaded: 0,
                    total: 0,
                    pct: 0.0,
                    done: true,
                    error: Some(e.clone()),
                },
            );
            Err(e)
        }
    }
}

async fn stream_to_file(
    app: &AppHandle,
    id: &str,
    url: &str,
    part_path: &std::path::Path,
) -> Result<u64, String> {
    let client = reqwest::Client::builder()
        .user_agent("crucible-studio")
        .build()
        .map_err(|e| e.to_string())?;
    let resp = client.get(url).send().await.map_err(|e| e.to_string())?;
    if !resp.status().is_success() {
        return Err(format!("download failed: HTTP {}", resp.status()));
    }
    let total = resp.content_length().unwrap_or(0);

    let mut file = tokio::fs::File::create(part_path)
        .await
        .map_err(|e| e.to_string())?;
    let mut downloaded: u64 = 0;
    let mut last_emit: u64 = 0;
    let mut stream = resp.bytes_stream();

    while let Some(chunk) = stream.next().await {
        let chunk = chunk.map_err(|e| e.to_string())?;
        file.write_all(&chunk).await.map_err(|e| e.to_string())?;
        downloaded += chunk.len() as u64;

        // Emit at most every ~3 MB to avoid flooding the IPC bridge.
        if downloaded - last_emit >= 3_000_000 {
            last_emit = downloaded;
            let pct = if total > 0 {
                (downloaded as f64 / total as f64) * 100.0
            } else {
                0.0
            };
            let _ = app.emit(
                "download-progress",
                Progress {
                    id: id.to_string(),
                    downloaded,
                    total,
                    pct,
                    done: false,
                    error: None,
                },
            );
        }
    }
    file.flush().await.map_err(|e| e.to_string())?;
    Ok(downloaded)
}

#[tauri::command]
pub async fn delete_model(app: AppHandle, id: String) -> Result<(), String> {
    let spec = crate::catalog::spec_by_id(&id).ok_or_else(|| "unknown model id".to_string())?;
    let path = crate::catalog::models_dir_path(&app).join(spec.filename);
    if path.exists() {
        tokio::fs::remove_file(path)
            .await
            .map_err(|e| e.to_string())?;
    }
    Ok(())
}
