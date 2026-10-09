// Study PWA: network-first reading, cache-first app assets.
// Cache Storage is shared by every app on an origin. Never search or clear it
// globally: a sibling GitHub Pages app must keep its own offline content.
const BASE = new URL('./', self.location.href).pathname;
const CACHE_PREFIX = `study:${encodeURIComponent(BASE)}:`;
const CACHE_VERSION = `${CACHE_PREFIX}v15`;
const ASSET_VERSION = '?v=14';
const RAW_ORIGIN = 'https://raw.githubusercontent.com';
const RAW_BRIEFINGS = '/bwkim1025/study/main/briefings/';

const APP_SHELL = [BASE, BASE + 'index.html'];
const VISUAL_ASSETS = ['assets/content-visuals.js', 'assets/content-visuals.css']
  .map((path) => BASE + path + '?v=15');
const PRECACHE_ASSETS = [
  'manifest.json',
  'apple-touch-icon.png',
  'icon-192.png',
  'icon-512.png',
  'icon-512-maskable.png',
  'icon.svg',
  'icon-maskable.svg',
  'favicon.ico',
].map((path) => BASE + path + ASSET_VERSION).concat(VISUAL_ASSETS);

self.addEventListener('install', (event) => {
  event.waitUntil((async () => {
    const cache = await caches.open(CACHE_VERSION);
    // Keep the previous worker if the shell or its visual renderer cannot load.
    await cache.addAll([...APP_SHELL, ...VISUAL_ASSETS]);
    await Promise.all(PRECACHE_ASSETS.filter((url) => !VISUAL_ASSETS.includes(url)).map((url) =>
      cache.add(url).catch((error) => {
        console.warn('[study sw] optional precache skipped', url, error.message);
      })
    ));
    await self.skipWaiting();
  })());
});

self.addEventListener('activate', (event) => {
  event.waitUntil((async () => {
    // v13 used an unscoped cache name. Only the actual deployed /study/ worker
    // may remove that exact legacy cache; previews and sibling apps cannot.
    const canRemoveLegacy =
      self.location.origin === 'https://bwkim1025.github.io' &&
      BASE === '/study/' &&
      self.registration.scope === 'https://bwkim1025.github.io/study/';
    const keys = await caches.keys();
    await Promise.all(keys.filter((key) =>
      (key.startsWith(CACHE_PREFIX) && key !== CACHE_VERSION) ||
      (canRemoveLegacy && key === 'study-v13')
    ).map((key) => caches.delete(key)));
    await self.clients.claim();
  })());
});

self.addEventListener('message', (event) => {
  if (event.data === 'SKIP_WAITING') self.skipWaiting();
});

async function readCache(request) {
  try {
    const cache = await caches.open(CACHE_VERSION);
    return await cache.match(request);
  } catch (_) {
    // A storage restriction must not prevent a successful network request.
    return undefined;
  }
}

async function saveResponse(request, response) {
  if (!response || !response.ok) return;
  try {
    const cache = await caches.open(CACHE_VERSION);
    await cache.put(request, response.clone());
  } catch (_) {
    // Quota/private-browsing failures are non-fatal.
  }
}

function unavailable(isMarkdown) {
  return new Response(
    isMarkdown ? 'This briefing is not available offline.' : 'This resource is not available offline.',
    { status: 503, headers: { 'Content-Type': 'text/plain; charset=utf-8', 'Cache-Control': 'no-store' } }
  );
}

async function networkFirst(request, { isNavigation, isMarkdown }) {
  try {
    const response = await fetch(request);
    // A host's SPA/404 fallback must never be cached or rendered as a briefing.
    if (isMarkdown && /text\/html/i.test(response.headers.get('Content-Type') || '')) {
      return new Response('The briefing could not be loaded as Markdown.', {
        status: 502,
        headers: { 'Content-Type': 'text/plain; charset=utf-8', 'Cache-Control': 'no-store' },
      });
    }
    await saveResponse(request, response);
    return response;
  } catch (_) {
    const cached = await readCache(request);
    if (cached) return cached;
    // Only a real page navigation can use the app shell. Markdown, images,
    // JSON and ordinary HTML fetches must never receive index.html instead.
    if (isNavigation && !isMarkdown) {
      const shell = await readCache(BASE + 'index.html') || await readCache(BASE);
      if (shell) return shell;
    }
    return unavailable(isMarkdown);
  }
}

async function cacheFirst(request) {
  const cached = await readCache(request);
  if (cached) return cached;
  try {
    const response = await fetch(request);
    await saveResponse(request, response);
    return response;
  } catch (_) {
    return unavailable(false);
  }
}

self.addEventListener('fetch', (event) => {
  const request = event.request;
  if (request.method !== 'GET') return;
  const url = new URL(request.url);
  const isOurApp = url.origin === self.location.origin && url.pathname.startsWith(BASE);
  const isBriefingRaw = url.origin === RAW_ORIGIN &&
    url.pathname.startsWith(RAW_BRIEFINGS) && url.pathname.endsWith('.md');
  if (!isOurApp && !isBriefingRaw) return;

  const isMarkdown = url.pathname.endsWith('.md');
  const isNavigation = request.mode === 'navigate' || request.destination === 'document';
  if (isNavigation || isMarkdown || url.pathname.endsWith('.html')) {
    event.respondWith(networkFirst(request, { isNavigation, isMarkdown }));
  } else {
    event.respondWith(cacheFirst(request));
  }
});
