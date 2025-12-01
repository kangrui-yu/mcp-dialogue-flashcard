export const env = {
  PY_API_BASE_URL:
    process.env.PY_API_BASE_URL || "http://127.0.0.1:8081/api/v1",
  PY_API_TOKEN: process.env.PY_API_TOKEN || "",
  HTTP_TIMEOUT_MS: process.env.HTTP_TIMEOUT_MS || "8000",
  HTTP_RETRIES: process.env.HTTP_RETRIES || "2",
};