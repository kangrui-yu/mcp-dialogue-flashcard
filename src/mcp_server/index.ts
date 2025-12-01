import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import * as z from "zod/v4";
import { createServer } from "./server.js";
import { logger } from "./logging/logger.js";

async function main() {
  const server = createServer(z);
  const transport = new StdioServerTransport();

  await server.connect(transport);
}

main().catch((err) => {
  logger.error({ err }, "Fatal MCP server error");
  process.exit(1);
});