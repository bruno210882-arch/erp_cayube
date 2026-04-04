@app.route("/cliente-sw.js")
def cliente_service_worker():
    js = """
const CACHE_NAME = "cayube-cliente-v1";
const URLS_TO_CACHE = [
  "/cliente/login",
  "/cliente",
  "/static/logo.png"
];

self.addEventListener("install", event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(URLS_TO_CACHE))
  );
  self.skipWaiting();
});

self.addEventListener("activate", event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.map(key => {
        if (key !== CACHE_NAME) return caches.delete(key);
      }))
    )
  );
  self.clients.claim();
});

self.addEventListener("fetch", event => {
  if (event.request.method !== "GET") return;

  event.respondWith(
    caches.match(event.request).then(response => {
      return response || fetch(event.request).catch(() => caches.match("/cliente/login"));
    })
  );
});
"""
    return app.response_class(js, mimetype="application/javascript")