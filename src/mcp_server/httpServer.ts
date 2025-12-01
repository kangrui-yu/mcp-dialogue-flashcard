// src/mcp_server/httpServer.ts
import express from "express";
import * as z from "zod/v4";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import { createServer } from "./server.js"; // your existing factory

const app = express();
app.use(express.json());

// Create a single MCP server instance re-used across requests
const mcpServer: McpServer = createServer(z);

app.post("/mcp", async (req, res) => {
  // Create a new transport per request (stateless, no session IDs)
  const transport = new StreamableHTTPServerTransport({
    sessionIdGenerator: undefined,
    enableJsonResponse: true,
  });

  // Clean up when the HTTP response ends
  res.on("close", () => {
    transport.close();
  });

  try {
    // Attach transport to the MCP server for this request
    await mcpServer.connect(transport);
    // Handle the MCP JSON-RPC payload
    await transport.handleRequest(req, res, req.body);
  } catch (err) {
    console.error("Error handling /mcp request:", err);
    if (!res.headersSent) {
      res.status(500).json({ error: "Internal MCP server error" });
    }
  }
});

const port = parseInt(process.env.PORT || "3000", 10);
app.listen(port, () => {
  console.log(`HTTP MCP server listening on http://localhost:${port}/mcp`);
});