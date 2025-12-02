import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import type * as zod from "zod/v4";
// import { registerSummarizeDialogueTool } from "./depreciated/summarizeDialogueTool.js";
import { registerRetrieveFlashcardTool } from "./tools/retrieveFlashcardTool.js";
import { registerStartDialogueSummaryTool } from "./tools/startDialogueSummaryTool.js";
import { registerQuerySummaryTool } from "./tools/querySummaryTool.js";
import { registerWaitSummaryTool } from "./tools/waitSummaryTool.js";

export function createServer(z: typeof zod): McpServer {
  const server = new McpServer({
    name: "dialogue-flashcards",
    version: "1.0.0",
  });

  registerStartDialogueSummaryTool(server, z);
  registerQuerySummaryTool(server, z);
  registerWaitSummaryTool(server, z);
  registerRetrieveFlashcardTool(server, z);

  return server;
}
