self.addEventListener("install", (ev) => {
    ev.waitUntil(
        caches.open("bnu120").then((cache) => {
            cache.addAll([
                "/common.css",
                "/patches.js",
                "/tooltip.css",
                "https://unpkg.com/@popperjs/core@2/dist/umd/popper.js",
                "https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@200;300;400;500;600;700;900&display=swap",
            ]).then(console.log)
        })
    )
})

self.addEventListener("fetch", (ev) => {
    ev.respondWith(caches.match(ev.request).then((response) => response ?? fetch(ev.request)))
})
