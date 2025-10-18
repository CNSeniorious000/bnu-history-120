importScripts("https://storage.googleapis.com/workbox-cdn/releases/6.4.1/workbox-sw.js");

const cacheName = "bnu120";

const options = { cacheName };

workbox.routing.registerRoute(({ sameOrigin }) => sameOrigin, new workbox.strategies.CacheFirst(options));
workbox.routing.registerRoute(({ request: { destination }, sameOrigin }) => !sameOrigin && !["image", "font"].includes(destination), new workbox.strategies.StaleWhileRevalidate(options));

async function sleep(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
}

const semaphore = {
    count: 3,
    waitingList: [],

    async acquire() {
        if (this.count > 0) {
            this.count--;
        } else {
            await new Promise((resolve) => {
                this.waitingList.push(resolve);
            });
        }
    },

    release() {
        if (this.waitingList.length > 0) {
            const resolve = this.waitingList.shift();
            resolve();
        } else {
            this.count++;
        }
    },
};

async function cacheAll() {
    const cache = await caches.open(cacheName);
    let throttle = false;

    const haveBeenCached = await cache.keys().then((request) => request.map(({ url }) => decodeURI(new URL(url).pathname)));
    console.log({ haveBeenCached });

    async function cacheOne(url) {
        if (!haveBeenCached.includes(url)) {
            if (throttle) {
                await semaphore.acquire();
                await cache.add(url);
                semaphore.release();
            } else {
                await cache.add(url);
            }
            console.log(`caching: ${url}`);
        }
    }

    async function cacheAll(urls) {
        return await Promise.all(urls.map(cacheOne));
    }

    await cacheAll(["/about", "/北师大", "/辅大", "/女高师"]);
    console.log("landing pages cached");

    await cacheAll(["/api/people/dict", "/api/people/list", "/common.css", "/static/tooltip.css", "/static/uno.css", "/static/patches.js"]);
    console.log("vital assets cached");

    const promises = [];

    promises.push(cacheAll(["https://unpkg.com/@popperjs/core@2/dist/umd/popper.js", "/api/北师大", "/api/辅大", "/api/女高师"]));

    const peopleUrls = await fetch("/api/people/dict")
        .then((res) => res.json())
        .then(Object.values)
        .then((urlLists) => [].concat(...urlLists, "/about"));

    throttle = true;

    for (const url of peopleUrls) promises.push(cacheAll([url, `/api${url}`]));

    await Promise.all(promises);
}

cacheAll();
