import { z } from "zod";
import { env } from "../config/env.js";
import { logger } from "../logging/logger.js";

const SummarizeReq = z.object({
  dialogue: z.array(z.object({ role: z.string(), message: z.string() })),
});
const SummarizeRes = z.object({
  summary: z.string(),
});

const FlashcardRes = z.object({
  found: z.boolean(),
  card: z
    .object({
      concept: z.string(),
      question: z.string(),
      answer: z.string(),
    })
    .nullable()
    .optional(),
});

async function http(
  path: string,
  init: RequestInit & { timeoutMs?: number } = {},
) {
  const ctrl = new AbortController();
  const timeoutMs = init.timeoutMs ?? Number(env.HTTP_TIMEOUT_MS);
  const timeoutId = setTimeout(() => ctrl.abort(), timeoutMs);

  try {
    const url = `${env.PY_API_BASE_URL}${path}`;
    const res = await fetch(url, {
      ...init,
      headers: {
        "content-type": "application/json",
        ...(env.PY_API_TOKEN
          ? { authorization: `Bearer ${env.PY_API_TOKEN}` }
          : {}),
        ...(init.headers || {}),
      },
      signal: ctrl.signal,
    });
    return res;
  } finally {
    clearTimeout(timeoutId);
  }
}

async function withRetries<T>(
  fn: () => Promise<T>,
  retries = Number(env.HTTP_RETRIES),
) {
  let attempt = 0;
  // jittered backoff
  while (true) {
    try {
      return await fn();
    } catch (err) {
      if (attempt >= retries) throw err;
      const delay =
        Math.min(2000, 300 * Math.pow(2, attempt)) + Math.random() * 100;
      logger.warn({ attempt, delay, err }, "HTTP call failed, retrying");
      await new Promise((r) => setTimeout(r, delay));
      attempt++;
    }
  }
}

export const pythonApi = {
  summarizeDialogue: async (
    dialogue: { role: string; message: string }[],
  ) => {
    const body = SummarizeReq.parse({ dialogue });
    const res = await withRetries(() =>
      http("/summarize-dialogue", {
        method: "POST",
        body: JSON.stringify(body),
      }),
    );
    if (!res.ok) {
      throw new Error(`summarize-dialogue failed: ${res.status}`);
    }
    const json = await res.json();
    return SummarizeRes.parse(json);
  },

  retrieveFlashcard: async (concept: string) => {
    const res = await withRetries(() =>
      http(`/flashcards?concept=${encodeURIComponent(concept)}`, {
        method: "GET",
      }),
    );
    if (res.status === 404) {
      // 👇 just return null, no const assertion
      return { found: false, card: null };
    }
    if (!res.ok) {
      throw new Error(`flashcards failed: ${res.status}`);
    }
    const json = await res.json();
    return FlashcardRes.parse(json);
  },
};