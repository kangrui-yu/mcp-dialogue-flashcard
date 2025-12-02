# Dialogue & Flashcards MCP Server

An MCP server that analyzes educational dialogues to identify missing prerequisite concepts and provides targeted flashcard recommendations. The system performs multi-stage dialogue analysis to detect underlying knowledge gaps beyond surface-level questions.

## Demo

In the demonstration video, we show a scenario where a student asks questions about Jensen's inequality and Gaussian distributions. While these appear to be distinct topics, our dialogue analysis system identifies that both questions stem from a fundamental misunderstanding of mean and variance concepts. The latent concept detector successfully extracts this common prerequisite causing difficulties in both surface topics, and recommends relevant flashcards to address the root knowledge gap. The system is fully implemented as an MCP plugin for easy integration with existing educational chatbots.

https://github.com/user-attachments/assets/b21a7079-4e31-4207-b181-a8743d468f67

## Architecture

The system consists of two main components:

- **MCP Server (TypeScript)** - Provides MCP tools with input validation and handles communication protocols (stdio for local Claude Desktop, HTTP for remote access)
- **Python Flask API** - Implements the dialogue analysis logic, async task management, and flashcard retrieval from CSV data

## Directory Structure

```
├── src/
│   ├── mcp_server/           # TypeScript MCP server
│   │   ├── index.ts          # Main entry point
│   │   ├── server.ts         # MCP server configuration
│   │   ├── httpServer.ts     # HTTP transport for remote access with OpenAI Playground
│   │   ├── tools/            # MCP tool implementations
│   │   ├── clients/          # Python API client
│   │   ├── config/       
│   │   └── logging/     
│   └── python_api/           # Flask API backend
│       ├── app/
│       │   ├── api/          # REST API endpoints
│       │   ├── domain/     
│       │   │   ├── summarization/  # Dialogue analysis
│       │   │   └── flashcard/      # Flashcard retrieval
│       │   └── config.py
│       └── Dockerfile
├── data/
│   ├── flashcards.csv        # Educational flashcard database
│   └── dialogues.csv         # Dialogue analysis results
├── docker-compose.yml     
└── package.json     
```



## Installation & Setup


```bash
npm install
npm run build

cd src/python_api
pip install -r requirements.txt
python -m gunicorn --config gunicorn.conf.py app:app
```

### Integration with Local Client (Claude Desktop)
Add MCP server to your client's config.json
```json
{
    "dialogue-flashcards": {
      "command": "/path/to/your/node",
      "args": [
        "/path/to/your/mcp-dialogue-flashcard/dist/index.js"
      ],
      "env": {
        "PY_API_BASE_URL": "http://127.0.0.1:8081/api/v1"
      }
    }
  }
```
### Integration with Remote Client (OpenAI Playground)
Run httpserver
```bash
export PORT=3000
export PY_API_BASE_URL=http://127.0.0.1:8081/api/v1
node dist/httpServer.js
ngrok http 3000  #if NAT traversal needed
```
## MCP Tools

The server provides four MCP tools for dialogue analysis and flashcard retrieval, **to avoid chatbot timeout and retry with multiple requests, the time consuming dialogue summary tool is aided with two helpers query / wait dialogue summary**

### `start_dialogue_summary`
Initiates asynchronous dialogue analysis and returns a task ID for tracking progress.

**Input:**
```json
{
  "dialogue": [
    {"role": "student", "message": "I don't understand Jensen's inequality"},
    {"role": "tutor", "message": "Can you explain what you know about convex functions?"}
  ],
  "user_id": 0
}
```

**Output:**
```json
{
  "task_id": "uuid-string",
  "status": "started",
  "message": "Task created and processing started"
}
```

### `query/wait_summary`
Checks the current status and progress of a dialogue analysis task.

**Input:**
```json
{
  "task_id": "uuid-string",
}
```
**Output:**
```json
{
  "task_id": "uuid-string"
  "timeout": 300,
  "message": "Processing Latent Refinement Loop (2/3)"
}
```



### `retrieve_flashcard`
Retrieves educational flashcards by concept name (#TODO returns top1 match based on cosine similarity of concept embeddings if over threshold)

**Input:**
```json
{
  "concept": "mean_and_variance"
}
```

**Output:**
```json
{
  "concept": "mean_and_variance",
  "question": "What are the mean and variance of a random variable?",
  "answer": "The mean is the expected value, variance measures spread around the mean..."
}
```



### Extending Dialogue Summary Logic

The dialogue analysis pipeline is located in `src/python_api/app/domain/summarization/` and follows a multi-stage workflow:
- Generation → Judging → Refinement loops → Flashcard generation → Result saving
