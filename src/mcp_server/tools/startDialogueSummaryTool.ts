import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import type * as zod from "zod/v4";
import { pythonApi } from "../clients/pythonApi.js";

export function registerStartDialogueSummaryTool(
  server: McpServer,
  z: typeof zod,
) {
  server.registerTool(
    "start_dialogue_summary",
    {
      title: "Start dialogue summary",
      description: "Start asynchronous dialogue summarization process. Returns a task_id immediately for tracking progress.",
      inputSchema: {
        dialogue: z.array(
          z.object({
            role: z.string(),
            message: z.string(),
          }),
        ),
        user_id: z.number().optional().default(0),
      },
      outputSchema: {
        task_id: z.string(),
        status: z.literal("started"),
        message: z.string(),
      },
    },
    async ({
      dialogue,
      user_id,
    }: {
      dialogue: { role: string; message: string }[];
      user_id?: number;
    }) => {
      const { task_id } = await pythonApi.startDialogueSummary(dialogue, user_id);
      
      return {
        content: [
          {
            type: "text",
            text: `Dialogue summarization started with task ID: ${task_id}. Use query_summary or wait_summary to track progress.`,
          },
        ],
        structuredContent: {
          task_id,
          status: "started" as const,
          message: "Task created and processing started",
        },
      };
    },
  );
}
