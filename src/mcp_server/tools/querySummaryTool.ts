import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import type * as zod from "zod/v4";
import { pythonApi } from "../clients/pythonApi.js";

export function registerQuerySummaryTool(
  server: McpServer,
  z: typeof zod,
) {
  server.registerTool(
    "query_dialogue_summary",
    {
      title: "Query dialogue summary status",
      description: "Query the current status and progress of a dialogue summarization task using its task_id.",
      inputSchema: {
        task_id: z.string(),
      },
      outputSchema: {
        task_id: z.string(),
        status: z.enum(["pending", "running", "completed", "failed"]),
        current_stage: z.string(),
        progress_count: z.number(),
        total_stages: z.number(),
        result: z.string().nullable(),
        error: z.string().nullable(),
        created_at: z.number(),
        started_at: z.number().nullable(),
        completed_at: z.number().nullable(),
        progress: z.array(z.object({
          stage: z.string(),
          message: z.string(),
          timestamp: z.number(),
        })),
      },
    },
    async ({
      task_id,
    }: {
      task_id: string;
    }) => {
      const taskStatus = await pythonApi.querySummaryStatus(task_id);
      
      if (!taskStatus) {
        return {
          content: [
            {
              type: "text",
              text: `Task ${task_id} not found. It may have expired or never existed.`,
            },
          ],
          structuredContent: {
            task_id,
            status: "failed" as const,
            current_stage: "not_found",
            progress_count: 0,
            total_stages: 0,
            result: null,
            error: "Task not found",
            created_at: 0,
            started_at: null,
            completed_at: null,
            progress: [],
          },
        };
      }

      let statusMessage = "";
      if (taskStatus.status === "completed" && taskStatus.result) {
        statusMessage = `Task completed successfully. Summary: ${taskStatus.result}`;
      } else if (taskStatus.status === "failed" && taskStatus.error) {
        statusMessage = `Task failed with error: ${taskStatus.error}`;
      } else if (taskStatus.status === "running") {
        statusMessage = `Task is running. Current stage: ${taskStatus.current_stage} (${taskStatus.progress_count}/${taskStatus.total_stages})`;
      } else {
        statusMessage = `Task status: ${taskStatus.status}`;
      }

      return {
        content: [
          {
            type: "text",
            text: statusMessage,
          },
        ],
        structuredContent: taskStatus,
      };
    },
  );
}
