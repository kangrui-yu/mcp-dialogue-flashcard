import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import type * as zod from "zod/v4";
import { pythonApi } from "../clients/pythonApi.js";

export function registerSummarizeDialogueTool(
  server: McpServer,
  z: typeof zod,
) {
  server.registerTool(
    "summarize_dialogue",
    {
      title: "Summarize dialogue",
      description: "Summarize a list of dialogue turns.",
      inputSchema: {
        dialogue: z.array(
          z.object({
            role: z.string(),
            message: z.string(),
          }),
        ),
      },
      outputSchema: {
        summary: z.string(),
      },
    },
    async ({
      dialogue,
    }: {
      dialogue: { role: string; message: string }[];
    }) => {
      const { summary } = await pythonApi.summarizeDialogue(dialogue);
      return {
        content: [{ type: "text", text: summary }],
        structuredContent: { summary },
      };
    },
  );
}