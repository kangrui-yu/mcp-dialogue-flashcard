// Minimal JSON logger to stderr, friendly for MCP stdio servers
type LogLevel = "debug" | "info" | "warn" | "error";

function log(level: LogLevel, msg: string, meta?: Record<string, unknown>) {
  const line = JSON.stringify({
    level,
    msg,
    time: new Date().toISOString(),
    ...meta,
  });
  // stderr only
  console.error(line);
}

export const logger = {
  debug(meta: Record<string, unknown>, msg: string) {
    log("debug", msg, meta);
  },
  info(meta: Record<string, unknown>, msg: string) {
    log("info", msg, meta);
  },
  warn(meta: Record<string, unknown>, msg: string) {
    log("warn", msg, meta);
  },
  error(meta: Record<string, unknown>, msg: string) {
    log("error", msg, meta);
  },
};