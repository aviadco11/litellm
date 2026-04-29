---
post_title: "LiteLLM + Ollama + Open WebUI Stack"
author1: "aviadcohen"
post_slug: "litellm-ollama-open-webui-stack"
microsoft_alias: "n/a"
featured_image: "n/a"
categories:
  - "infrastructure"
tags:
  - "litellm"
  - "ollama"
  - "open-webui"
  - "docker"
  - "llm"
ai_note: "AI-assisted"
summary: "A Docker Compose stack that combines Ollama for local LLM inference, LiteLLM as a unified API gateway for multiple LLM providers, and Open WebUI as a chat interface."
post_date: "2026-04-29"
---

## Overview

This stack provides a self-hosted LLM platform that combines local model inference with cloud
LLM providers, all accessible through a single chat interface.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Docker Network                       │
│                  (evolution_network)                     │
│                                                         │
│  ┌──────────────┐    ┌──────────────┐                   │
│  │   Ollama      │    │   LiteLLM    │                   │
│  │  :11434       │◄───│   :4000      │                   │
│  │              │    │              │                   │
│  │  Local LLM   │    │  API Gateway │                   │
│  │  Inference    │    │  (Unified    │                   │
│  │              │    │   Proxy)     │                   │
│  └──────┬───────┘    └──────┬───────┘                   │
│         │                   │                           │
│         │   ┌───────────────┘                           │
│         │   │                                           │
│         ▼   ▼                                           │
│  ┌──────────────┐         Cloud LLM APIs                │
│  │  Open WebUI   │    ┌─────────────────┐               │
│  │  :3000        │    │ Gemini, Grok,   │               │
│  │              │    │ Groq, Mistral,  │               │
│  │  Chat UI      │    │ MiniMax         │               │
│  └──────────────┘    └─────────────────┘               │
└─────────────────────────────────────────────────────────┘
```

## Services

### Ollama

- **Image**: `ollama/ollama:latest`
- **Port**: `11434`
- **Purpose**: Runs LLM models locally on your machine. Models are downloaded and executed
  entirely on-premises with no external API calls.
- **Volumes**:
  - `./ollama_data` — Persists downloaded models across container restarts.
  - `./ca-certificates.crt` — Corporate CA trust bundle for pulling models behind a proxy.
- **Resource Limit**: 8 GB RAM (configurable based on your system).
- **Current Model**: `llama3.2:1b` (1.3 GB).

### LiteLLM

- **Image**: `ghcr.io/berriai/litellm:main-latest`
- **Port**: `4000`
- **Purpose**: Acts as a unified OpenAI-compatible API gateway. Routes requests to multiple
  LLM providers (both local and cloud) through a single endpoint. This allows Open WebUI to
  access all providers without needing individual integrations.
- **Config**: `litellm_config.yaml` defines the available models and their provider mappings.
- **Authentication**: Protected by a master key (`LITELLM_MASTER_KEY`).
- **SSL**: SSL verification is disabled (`SSL_VERIFY=false`) for environments behind
  corporate proxies.

### Open WebUI

- **Image**: `ghcr.io/open-webui/open-webui:main`
- **Port**: `3000`
- **Purpose**: A web-based chat interface for interacting with LLMs. Connects to both
  Ollama directly (for local models) and LiteLLM (for cloud models).
- **Volumes**: `./open_webui_data` — Persists chat history, user settings, and uploaded files.
- **Connections**:
  - Ollama at `http://ollama:11434` — Direct access to local models.
  - LiteLLM at `http://litellm:4000/v1` — OpenAI-compatible endpoint for cloud models.

## Available Models

| Model              | Provider       | Type            |
| ------------------ | -------------- | --------------- |
| `llama3.2:1b`      | Ollama (local) | Local inference |
| `gemini-2.0-flash` | Google Gemini  | Cloud API       |
| `grok-3`           | xAI            | Cloud API       |
| `MiniMax-M1`       | MiniMax        | Cloud API       |
| `llama-3.3-70b`    | Groq           | Cloud API       |
| `mistral-large`    | Mistral        | Cloud API       |

## Request Flow

1. User sends a message in **Open WebUI** (`http://localhost:3000`).
2. For local models — Open WebUI calls **Ollama** directly at `http://ollama:11434`.
3. For cloud models — Open WebUI calls **LiteLLM** at `http://litellm:4000/v1`, which
   routes the request to the appropriate cloud provider (Gemini, Grok, Groq, Mistral,
   MiniMax).
4. The response streams back through the same path to the UI.

## Quick Start

```bash
# Start all services
docker-compose up -d

# Pull a local model into Ollama
docker exec -it ollama ollama pull llama3.2:1b

# Access the chat UI
# Open http://localhost:3000 in your browser
```

## Configuration

### Adding a New Cloud Provider

1. Add the API key to the `litellm` service `environment` in `docker-compose.yml`.
2. Add the model entry in `litellm_config.yaml` with the provider prefix and
   `api_key: os.environ/YOUR_KEY_NAME`.
3. Restart LiteLLM: `docker-compose up -d --force-recreate litellm`.

### Adding a New Local Model

```bash
docker exec -it ollama ollama pull <model_name>
```

### Corporate Proxy / TLS

The `ca-certificates.crt` file mounted into Ollama contains your corporate CA certificates.
This is required to pull models from behind a corporate proxy that performs SSL inspection.
LiteLLM uses `SSL_VERIFY=false` to bypass SSL verification for outbound API calls.

## Ports Summary

| Service    | Port  | URL                      |
| ---------- | ----- | ------------------------ |
| Open WebUI | 3000  | `http://localhost:3000`  |
| LiteLLM    | 4000  | `http://localhost:4000`  |
| Ollama     | 11434 | `http://localhost:11434` |

## Network

All services communicate over the `evolution_network` Docker bridge network using container
names as hostnames (e.g., `http://ollama:11434`).


