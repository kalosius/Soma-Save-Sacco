self.addEventListener('install', event => {
  event.waitUntil(
    caches.open('soma-cache').then(cache => {
      return cache.addAll([
        '/',
        '/static/images/img/logo.png',
        '/static/icons/icon-192x192.png',
        '/static/icons/icon-512x512.png',
        '/static/screenshots/homepage.png',
      ]);
    })
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request).then(response => {
      return response || fetch(event.request);
    })
  );
});
