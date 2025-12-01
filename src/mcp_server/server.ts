import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import type * as zod from "zod/v4";
import { registerSummarizeDialogueTool } from "./tools/summarizeDialogueTool.js";
import { registerRetrieveFlashcardTool } from "./tools/retrieveFlashcardTool.js";

export function createServer(z: typeof zod): McpServer {
  const server = new McpServer({
    name: "dialogue-flashcards",
    version: "1.0.0",
  });

  registerSummarizeDialogueTool(server, z);
  registerRetrieveFlashcardTool(server, z);

  return server;
}