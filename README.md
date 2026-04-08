# field-captain

> The Jetson field agent system — power up, connect, talk. The AI captain is ready.

A local web server that runs on a Jetson Super Orin Nano 8GB, providing a voice/text chat interface through a phone or laptop browser. The phone provides mic/speaker, the Jetson provides the brain.

## Quick Start

```bash
cd /opt/captain
git clone https://github.com/Lucineer/field-captain.git
pip install -r requirements.txt
python -m field_captain.main
# Open on phone: http://captain.local:8080
```

## Architecture

```
Phone/Laptop (mic/speaker)  ◄──WiFi──►  Jetson (brain)
   Web Browser                         Starlette :8080
   Chat / Config / Projects           Model Manager (lazy load)
                                       Whisper STT → Phi-3 LLM → Piper TTS
                                       Git-Agent repos on NVMe
                                       Cloudflare tunnel → API services
```

## Key Design Decisions

1. **Phone as I/O, Jetson as brain** — mic/speaker on mobile, compute on edge
2. **One GPU model at a time** — 8GB shared means pipeline: STT → unload → LLM → unload → TTS
3. **Local-first** — cold models on NVMe, cloud is enhancement not requirement
4. **Git-native memory** — every conversation becomes a git commit
5. **Vibe-coding** — voice ideas into working code
6. **Privacy-first** — no data leaves boat unless Captain allows
7. **Technician handoff** — guided setup then Captain self-services

## Memory Budget (8GB shared)

| Component | VRAM | Notes |
|-----------|------|-------|
| OS + Python | ~2GB | Fixed overhead |
| Whisper medium | ~1.5GB | STT, load on demand |
| Phi-3-mini Q4 | ~2GB | Text gen, load on demand |
| Piper TTS | ~50MB | TTS, trivial |
| JEPA v2 | ~2GB | Vision, load on demand |

**Rule: Only ONE GPU model active at a time. Pipeline sequentially.**

## Connectivity Priority

1. Starlink (best) → 2. Boat WiFi → 3. Phone hotspot (USB tether) → 4. Air-gapped (full local)

## Model Pipeline

```
User speaks → [Load Whisper] → STT → [Unload] 
  → [Load Phi-3] → Generate → [Unload]
  → [Load TTS] → Speak → [Unload] → Ready
```

## File Layout

```
/opt/captain/
├── models/           # Cold model storage
├── repos/            # Git-agent fleet repos
├── data/
│   ├── config/       # captain.yaml + encrypted secrets
│   ├── transcripts/  # Conversation history
│   └── projects/     # Active project data
├── field-captain/    # This repo
└── scripts/          # Network setup, backup, model manager
```

## Config (captain.yaml)

```yaml
models:
  stt: {engine: "whisper", model: "medium", device: "cuda"}
  tts: {engine: "piper", model: "en_US-lessac-medium"}
  llm:
    local: {engine: "llama-cpp", model: "/opt/captain/models/phi-3-mini/q4.gguf"}
    cloud:
      enabled: true
      providers: [deepseek, zai, deepinfra, siliconflow, moonshot]

network:
  priority: [starlink, boat_wifi, phone_hotspot]
  cloudflare_tunnel: true

privacy:
  local_first: true
  safety_bot_vetting: true
```

## The Flow

**Technician arrives with pre-loaded Jetson** → powers on → Jetson auto-connects → web interface at captain.local:8080 → tech helps Captain create GitHub + Cloudflare accounts → set up API keys → Captain talks to their AI → ideas stored in git → Captain riffing and vibe-coding → tech departs when Captain is self-sufficient

**Captain's daily use** → phone connects to Jetson WiFi → talks through web app → local LLM handles most conversations → cloud APIs for heavy tasks → AI is first-line tech support → ideas become git commits → code becomes agents → orders become BOMs

## Requirements

```
starlette>=0.27.0
uvicorn>=0.24.0
websockets>=12.0
pyyaml>=6.0
llama-cpp-python>=0.2.0
openai-whisper>=20231117
gitpython>=3.1.40
httpx>=0.25.0
```

## Service Plans

When on a Lucineer service plan:
- Jetson output streams to Lucineer's tech team
- Human monitoring for complex issues
- Captain controls what's shared
- Safety bot vetting for all pulled repos
- Priority support via the chatbot → human escalation

---

<i>Built by [Superinstance](https://github.com/superinstance) & [Lucineer](https://github.com/Lucineer) (DiGennaro et al.)</i>

<i>Powered by [Cocapn](https://github.com/Lucineer/cocapn-ai) — The sovereign agent runtime</i>
