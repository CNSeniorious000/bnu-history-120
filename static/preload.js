const preload_headers = new Headers()
preload_headers.append("x-bnu120-usage", "preload")
const preload_init_options = {
    method: "GET", redirect: "error", mode: "same-origin", headers: preload_headers
}

const cache = new Map()

const article = document.getElementById("article")

function preload(api_url) {
    return cache.get(api_url) ?? fetch(api_url, preload_init_options).then(
        async (response) => cache.set(api_url, await response.json()),
        (reason) => console.warn(reason)
    ).then(() => cache.get(api_url))
}

async function get_page_data(api_url) {
    return cache.get(api_url) ?? await preload(api_url)
}

async function load_page(url) {
    let api_url = "/api" + url
    if (!cache.has(api_url)) await get_page_data(api_url)
    let json = cache.get(api_url)
    history.pushState(null, null, url)
    article.innerHTML = json["div"]
    document.title = json["title"]
}

window.onpopstate = async (event) => {
    let api_url = "/api" + location.pathname + location.search
    await get_page_data(api_url).then((json) => article.innerHTML = json["div"])
}

// patch all <a> tags

function patch(node) {
    console.assert(node.nodeName === "A", node.nodeName)
    let url = new URL(node.href).pathname
    let api_url = "/api" + url
    node.onmouseenter = (event) => preload(api_url)
    node.onclick = (event) => {
        load_page(url).then(() => scrollTo({top: 0, behavior: "smooth"}))
        return false
    }
}

document.querySelectorAll("a").forEach(patch)
