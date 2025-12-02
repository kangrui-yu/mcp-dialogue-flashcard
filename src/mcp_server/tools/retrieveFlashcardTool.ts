import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import type * as zod from "zod/v4";
import { pythonApi } from "../clients/pythonApi.js";

export function registerRetrieveFlashcardTool(
  server: McpServer,
  z: typeof zod,
) {
  server.registerTool(
    "retrieve_flashcard",
    {
      title: "Retrieve flashcard",
      description: "Retrieve a flashcard by concept.",
      inputSchema: {
        concept: z.string(),
      },
      outputSchema: {
        found: z.boolean(),
        concept: z.string().nullable(),
        question: z.string().nullable(),
        answer: z.string().nullable(),
      },
    },
    async ({ concept }: { concept: string }) => {
      const res = await pythonApi.retrieveFlashcard(concept);

      if (!res.found || !res.card) {
        return {
          content: [
            { type: "text", text: `No flashcard found for "${concept}".` },
          ],
          structuredContent: {
            found: false,
            concept: null,
            question: null,
            answer: null,
          },
        };
      }

      const { card } = res;
      const text = `Flashcard for "${card.concept}":\nQ: ${card.question}\nA: ${card.answer}`;
      return {
        content: [{ type: "text", text }],
        structuredContent: {
          found: true,
          concept: card['concept'],
          question: card['question'],
          answer: card['answer'],
        },
      };
    },
  );
}
