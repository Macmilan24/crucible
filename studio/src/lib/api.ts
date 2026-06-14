// Typed wrappers over the Tauri command bridge. The Rust side uses snake_case
// parameters; Tauri converts camelCase JS keys to snake_case automatically.

import { invoke } from "@tauri-apps/api/core";
import { listen } from "@tauri-apps/api/event";

export interface SystemInfo {
  os: string;
  os_version: string;
  arch: string;
  cpu_brand: string;
  cpu_cores: number;
  total_ram_gb: number;
  available_ram_gb: number;
  apple_silicon: boolean;
  gpu: string;
}

export interface ModelEntry {
  id: string;
  name: string;
  params: string;
  quant: string;
  approx_size_gb: number;
  min_ram_gb: number;
  url: string;
  filename: string;
  description: string;
  downloaded: boolean;
  fits: boolean;
}

export interface ServerStatus {
  running: boolean;
  port: number;
  base_url: string;
  model_id: string | null;
  model_label: string | null;
  uptime_secs: number;
}

export interface DownloadProgress {
  id: string;
  downloaded: number;
  total: number;
  pct: number;
  done: boolean;
  error: string | null;
}

export interface ChatMessage {
  role: "system" | "user" | "assistant";
  content: string;
}

export interface ChatReply {
  content: string;
  prompt_tokens: number;
  completion_tokens: number;
  total_tokens: number;
  latency_ms: number;
}

export const getSystemInfo = () => invoke<SystemInfo>("get_system_info");
export const getModels = () => invoke<ModelEntry[]>("get_models");
export const recommendModel = () => invoke<string | null>("recommend_model");
export const modelsDir = () => invoke<string>("models_dir");
export const downloadModel = (id: string) => invoke<void>("download_model", { id });
export const deleteModel = (id: string) => invoke<void>("delete_model", { id });
export const crucibleAvailable = () => invoke<boolean>("crucible_available");
export const startServer = (modelId: string, port?: number) =>
  invoke<string>("start_server", { modelId, port: port ?? null });
export const stopServer = () => invoke<void>("stop_server");
export const serverStatus = () => invoke<ServerStatus>("server_status");

export const chatCompletion = (port: number, model: string | null, messages: ChatMessage[]) =>
  invoke<ChatReply>("chat_completion", { port, model, messages });

export const openExternal = (target: string) => invoke<void>("open_external", { target });

export const onDownloadProgress = (cb: (p: DownloadProgress) => void) =>
  listen<DownloadProgress>("download-progress", (e) => cb(e.payload));
