// Study PWA Service Worker
// Cache strategy:
//   - HTML / Markdown: Network-first (always latest briefings, fall back to cache offline)
//   - Icons / manifest / static images: Cache-first
//
// BASE is auto-detected from the worker's own location.
const CACHE_VERSION = 'study-v8';

// /repo-name/sw.js  ->  /repo-name/
const BASE = new URL('./', self.location).pathname;

const PRECACHE = [
  BASE,
  BASE + 'index.html',
  BASE + 'manifest.json',
  BASE + 'apple-touch-icon.png',
  BASE + 'icon-192.png',
  BASE + 'icon-512.png',
  BASE + 'icon-512-maskable.png',
  BASE + 'icon.svg',
  BASE + 'icon-maskable.svg',
  BASE + 'favicon.ico',
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_VERSION).then((cache) =>
      // Add each URL individually so a single missing optional asset
      // (e.g. a category not yet built) doesn't fail the entire install.
      Promise.all(
        PRECACHE.map((url) =>
          cache.add(url).catch((err) => {
            console.warn('[sw] precache skip', url, err && err.message);
          })
        )
      )
    ).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE_VERSION).map((k) => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('message', (event) => {
  if (event.data === 'SKIP_WAITING') self.skipWaiting();
});

self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);

  // Only handle our own origin (within BASE) + raw briefing fetches from GitHub
  const isOurApp = url.origin === self.location.origin && url.pathname.startsWith(BASE);
  const isBriefingRaw = url.hostname === 'raw.githubusercontent.com';
  if (!isOurApp && !isBriefingRaw) return;

  // Network-first for HTML and markdown (always latest)
  if (
    req.destination === 'document' ||
    url.pathname.endsWith('.html') ||
    url.pathname.endsWith('.md') ||
    isBriefingRaw
  ) {
    event.respondWith(
      fetch(req)
        .then((res) => {
          if (res && res.ok) {
            const copy = res.clone();
            caches.open(CACHE_VERSION).then((c) => c.put(req, copy)).catch(() => {});
          }
          return res;
        })
        .catch(() =>
          caches.match(req).then((c) => c || caches.match(BASE + 'index.html'))
        )
    );
    return;
  }

  // Cache-first for icons / manifest / static
  event.respondWith(
    caches.match(req).then((cached) =>
      cached ||
      fetch(req).then((res) => {
        if (res && res.ok) {
          const copy = res.clone();
          caches.open(CACHE_VERSION).then((c) => c.put(req, copy)).catch(() => {});
        }
        return res;
      })
    )
  );
});
