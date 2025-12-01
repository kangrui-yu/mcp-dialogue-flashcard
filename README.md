# Dialogue & Flashcards MCP Server

This repo provides an **MCP server** for:

- `summarize_dialogue` – summarize a chat-style dialogue
- `retrieve_flashcard` – retrieve a flashcard concept from a CSV

Architecture:

- **Node / TypeScript MCP server**  
  - Speaks MCP over **stdio** (for local Claude Desktop) and **HTTP** (for remote / ngrok).
  - Validates inputs/outputs with Zod.
  - Calls into Python over HTTP.

- **Python / Flask API**  
  - Implements the actual business logic:
    - Dialogue summarization (currently placeholder).
    - Flashcard retrieval from `data/flashcards.csv`.

---
