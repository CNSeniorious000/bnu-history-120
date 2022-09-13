const preload_headers = new Headers()
preload_headers.append("x-bnu120-usage", "preload")
const preload_init_options = {
    method: "GET", redirect: "error", mode: "same-origin", headers: preload_headers
}

const cache = new Map()

const article = document.getElementById("article")

function preload(url) {
    console.assert(!cache.has(url))
    return fetch(url, preload_init_options).then(
        async (response) => cache.set(url, await response.json()),
        (reason) => console.warn(reason)
    )
}

async function load_page(url) {
    let api_url = "/api" + url
    if (!cache.has(api_url)) await preload(api_url)
    let json = cache.get(api_url)
    window.history.pushState(null, null, url)
    article.innerHTML = json["div"]
    document.title = json["title"]
}

window.onpopstate = async (event) => {
    let url = location.pathname + location.search
    let api_url = "/api" + url
    if (!cache.has(api_url)) await preload(api_url)
    article.innerHTML = cache.get(api_url)["div"]
}
