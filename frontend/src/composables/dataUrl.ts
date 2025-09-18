// Utilities to convert URLs/blobs to data: URLs and to normalize symbol sources.

const DATA_URL_RE = /^data:[^;]+;base64,/i

export function isDataUrl(src: string): boolean {
  return DATA_URL_RE.test(src)
}

/**
 * Convert a Blob to a data: URL (base64).
 */
export function blobToDataUrl(blob: Blob): Promise<string> {
  return new Promise<string>((resolve, reject) => {
    const r = new FileReader()
    r.onload = () => resolve(String(r.result))
    r.onerror = () => reject(r.error || new Error('Failed to read blob as data URL'))
    r.readAsDataURL(blob)
  })
}

/**
 * Fetch a URL and return a data: URL string.
 *
 * - Keeps original MIME type when possible.
 * - Optional cache busting (useful in dev if you see cached responses).
 */
export async function urlToDataUrl(
  url: string,
  opts?: { cacheBust?: boolean; credentials?: RequestCredentials }
): Promise<string> {
  // Avoid double-work if the input is already a data URL
  if (isDataUrl(url)) return url

  const finalUrl =
    opts?.cacheBust
      ? appendCacheBust(url)
      : url

  const resp = await fetch(finalUrl, {
    // mode: 'cors' would be default on cross-origin; keep default and let the
    // browser decide based on origin/CORS headers. Configure credentials if needed.
    credentials: opts?.credentials ?? 'same-origin',
    cache: 'no-cache',
  })

  if (!resp.ok) {
    throw new Error(`Failed to fetch ${url}: ${resp.status} ${resp.statusText}`)
  }

  const blob = await resp.blob()
  return blobToDataUrl(blob)
}

/**
 * Ensure the given src is a data URL. If it's already one, return as-is;
 * otherwise fetch it and convert to data URL.
 */
export async function ensureDataUrl(src: string): Promise<string> {
  return isDataUrl(src) ? src : urlToDataUrl(src)
}

/**
 * Convert a list of URLs (or data URLs) to data URLs, preserving order.
 */
export async function urlsToDataUrls(urls: string[]): Promise<string[]> {
  return Promise.all(urls.map(u => ensureDataUrl(u)))
}

function appendCacheBust(url: string): string {
  try {
    const u = new URL(url, window.location.origin)
    u.searchParams.set('_cb', String(Date.now()))
    return u.toString()
  } catch {
    // Fallback for relative strings that URL constructor can't handle without base
    const sep = url.includes('?') ? '&' : '?'
    return `${url}${sep}_cb=${Date.now()}`
  }
}
