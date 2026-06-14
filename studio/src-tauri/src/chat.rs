//! A thin proxy to the local `crucible serve` chat endpoint.
//!
//! The webview runs on a `tauri://` origin, so a browser `fetch` to
//! `http://127.0.0.1:<port>` is cross-origin and would need CORS on the server.
//! Routing the request through Rust sidesteps that entirely and keeps the chat
//! request on-device — Studio never talks to anything but the local server.

use serde::{Deserialize, Serialize};
use std::time::Instant;

#[derive(Deserialize)]
pub struct ChatMessage {
    pub role: String,
    pub content: String,
}

#[derive(Serialize)]
pub struct ChatReply {
    pub content: String,
    pub prompt_tokens: u64,
    pub completion_tokens: u64,
    pub total_tokens: u64,
    pub latency_ms: u64,
}

#[tauri::command]
pub async fn chat_completion(
    port: u16,
    model: Option<String>,
    messages: Vec<ChatMessage>,
) -> Result<ChatReply, String> {
    let url = format!("http://127.0.0.1:{port}/v1/chat/completions");
    let body = serde_json::json!({
        "model": model.unwrap_or_else(|| "crucible-local".to_string()),
        "messages": messages
            .iter()
            .map(|m| serde_json::json!({ "role": m.role, "content": m.content }))
            .collect::<Vec<_>>(),
        "stream": false,
    });

    let client = reqwest::Client::new();
    let started = Instant::now();
    let resp = client
        .post(&url)
        .json(&body)
        .send()
        .await
        .map_err(|e| format!("couldn't reach the local server — is it running? ({e})"))?;

    let status = resp.status();
    let text = resp.text().await.map_err(|e| e.to_string())?;
    if !status.is_success() {
        return Err(format!("server returned HTTP {status}: {text}"));
    }

    let v: serde_json::Value =
        serde_json::from_str(&text).map_err(|e| format!("malformed server response: {e}"))?;
    let content = v["choices"][0]["message"]["content"]
        .as_str()
        .unwrap_or_default()
        .to_string();
    let usage = &v["usage"];

    Ok(ChatReply {
        content,
        prompt_tokens: usage["prompt_tokens"].as_u64().unwrap_or(0),
        completion_tokens: usage["completion_tokens"].as_u64().unwrap_or(0),
        total_tokens: usage["total_tokens"].as_u64().unwrap_or(0),
        latency_ms: started.elapsed().as_millis() as u64,
    })
}
