const DEFAULT_API_BASE_URL = "http://localhost:8000";

function normalizeBaseUrl(url: string): string {
  if (!url) {
    return DEFAULT_API_BASE_URL;
  }
  return url.endsWith("/") ? url.slice(0, -1) : url;
}

export function getApiBaseUrl(): string {
  const configured = process.env.NEXT_PUBLIC_API_BASE_URL;
  return normalizeBaseUrl(configured ?? DEFAULT_API_BASE_URL);
}

function buildUrl(path: string): string {
  if (/^https?:/i.test(path)) {
    return path;
  }
  const base = getApiBaseUrl();
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  return `${base}${normalizedPath}`;
}

export async function fetchJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(buildUrl(path), {
    ...init,
    headers: {
      "content-type": "application/json",
      ...init?.headers,
    },
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(`Request failed (${response.status}): ${message || path}`);
  }

  return (await response.json()) as T;
}
