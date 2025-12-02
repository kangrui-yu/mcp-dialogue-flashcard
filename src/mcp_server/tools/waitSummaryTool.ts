import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import type * as zod from "zod/v4";
import { pythonApi } from "../clients/pythonApi.js";

export function registerWaitSummaryTool(
  server: McpServer,
  z: typeof zod,
) {
  server.registerTool(
    "wait_dialogue_summary",
    {
      title: "Wait for dialogue summary completion",
      description: "Wait for a dialogue summarization task to complete. This is a long-polling operation that tracks the stage of dialogue summary progress (loop 1/2/3) and returns when complete or timeout is reached.",
      inputSchema: {
        task_id: z.string(),
        timeout: z.number().optional().default(300).describe("Timeout in seconds (default: 300, max: 600)"),
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
      timeout,
    }: {
      task_id: string;
      timeout?: number;
    }) => {
      // Limit timeout to max 600 seconds (10 minutes)
      const safeTimeout = Math.min(timeout || 300, 600);
      
      const taskStatus = await pythonApi.waitSummaryCompletion(task_id, safeTimeout);
      
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
        // Simply return the summary result when completed
        statusMessage = taskStatus.result;
      } else if (taskStatus.status === "failed" && taskStatus.error) {
        statusMessage = `Task failed with error: ${taskStatus.error}`;
      } else if (taskStatus.status === "running") {
        statusMessage = `Task is still running after ${safeTimeout} seconds. Current stage: ${taskStatus.current_stage} (${taskStatus.progress_count}/${taskStatus.total_stages})`;
        
        // Show latest progress updates
        const recentProgress = taskStatus.progress.slice(-3);
        if (recentProgress.length > 0) {
          const progressUpdate = recentProgress
            .map(p => `${p.stage}: ${p.message}`)
            .join(" → ");
          statusMessage += `\n\nRecent progress: ${progressUpdate}`;
        }
      } else {
        statusMessage = `Task status: ${taskStatus.status} after waiting ${safeTimeout} seconds`;
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
