/* UAI Sport Bot — service worker
 *
 * Regla de oro: esta app decide reservas con datos que tienen que estar frescos.
 * Nada de api.github.com ni ntfy.sh se cachea NUNCA. El HTML va network-first
 * para que un deploy llegue de inmediato; la caché es solo la red de seguridad
 * cuando no hay señal.
 */
const VERSION = 'uai-bot-v1';
const SHELL = [
  './',
  './index.html',
  './manifest.webmanifest',
  './icon-180.png',
  './icon-192.png',
  './icon-512.png',
];

// Hosts que jamás se cachean: sus respuestas cambian el comportamiento del bot.
const NUNCA = ['api.github.com', 'ntfy.sh'];

self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(VERSION)
      // addAll falla entero si un recurso falla; individual es más tolerante.
      .then((c) => Promise.allSettled(SHELL.map((u) => c.add(u))))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys()
      .then((ks) => Promise.all(ks.filter((k) => k !== VERSION).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET') return;

  let url;
  try { url = new URL(req.url); } catch { return; }
  if (NUNCA.some((h) => url.hostname.endsWith(h))) return;   // a la red, sin tocar

  // Navegación: red primero, caché solo si no hay conexión.
  if (req.mode === 'navigate') {
    e.respondWith(
      fetch(req)
        .then((r) => {
          const copia = r.clone();
          caches.open(VERSION).then((c) => c.put('./index.html', copia));
          return r;
        })
        .catch(() => caches.match('./index.html').then((r) => r || Response.error()))
    );
    return;
  }

  // Estáticos propios y tipografías: caché primero, y se refresca de fondo.
  if (url.origin === location.origin ||
      url.hostname.endsWith('fonts.googleapis.com') ||
      url.hostname.endsWith('fonts.gstatic.com')) {
    e.respondWith(
      caches.match(req).then((hit) => {
        const red = fetch(req).then((r) => {
          if (r && r.status === 200) {
            const copia = r.clone();
            caches.open(VERSION).then((c) => c.put(req, copia));
          }
          return r;
        }).catch(() => hit);
        return hit || red;
      })
    );
  }
});
