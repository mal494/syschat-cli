# SysChat 🖥️

A local "Chat with your Files" CLI tool.
SysChat inspects a file's metadata (and content, if safe) and uses an LLM to answer questions about it.

## Features

- **Metadata Analysis:** Reads permissions, size, and timestamps.
- **Safe Content Peeking:** Reads text files while ignoring large binaries to prevent crashes.
- **LLM Agnostic:** Works with local models (Ollama) or Cloud APIs (OpenAI).

## Setup

1. Clone the repo.
2. Install dependencies:

   pip install -r requirements.txt
