const preload_headers = new Headers()
preload_headers.append("x-bnu120-usage", "preload")
const preload_init_options = {
    method: "GET", redirect: "error", mode: "same-origin", headers: preload_headers
}
const cache = new Map()
const article = document.getElementById("article")

let current = location.href

function preload(api_url) {
    return cache.get(api_url) ?? fetch(api_url, preload_init_options).then(
        async response => cache.set(api_url, await response.json()),
        (reason) => console.warn(reason)
    ).then(() => cache.get(api_url))
}

async function get_page_data(api_url) {
    return cache.get(api_url) ?? await preload(api_url)
}

function push_state(url) {
    history.pushState({url}, null, url)
    current = location.href
}

async function load_page(url) {
    let api_url = "/api" + url
    if (!cache.has(api_url)) await get_page_data(api_url)
    let json = cache.get(api_url)
    article.innerHTML = json["div"]
    document.title = json["title"]
}

function split_hash(href) {
    let url = new URL(href)
    return {
        path: url.pathname + url.search,
        hash: url.hash
    }
}

window.onpopstate = async event => {
    let to = split_hash(location.href)
    let from = split_hash(current)
    current = location.href
    if (to.path === from.path) return console.assert(to.hash !== from.hash, [to.hash, from.hash])
    let api_url = "/api" + to.path
    await get_page_data(api_url).then(json => {
        article.innerHTML = json["div"]
        document.title = json["title"]
    }).then(patch_hash_link)
}

// patch all <a> tags

function patch(node) {
    // noinspection JSCheckFunctionSignatures
    console.assert(node.nodeName === "A", node.nodeName)
    let href = new URL(node.href)
    if (location.pathname === href.pathname && location.search === href.search && location.host === href.host) {
        node.onclick = event => history.replaceState(null, null, node.href)
    }
    let url = href.pathname
    let api_url = "/api" + url
    node.onmouseenter = event => preload(api_url)
    node.onclick = event => {
        load_page(url).then(() => {
            // noinspection JSCheckFunctionSignatures
            if (!current.includes("#")) scrollTo({top: 0, behavior: "instant"})
            return url
        }).then(push_state).then(patch_hash_link).then(() => {
            // noinspection JSCheckFunctionSignatures
            scrollTo({top: 0, behavior: "instant"})
        })
        return false
    }
}

function patch_all() {
    document.querySelectorAll("a").forEach(patch)
}

function patch_hash_link() {
    for (h of document.querySelectorAll("#markdown [id]"))
        h.innerHTML = `<a href="#${h.id}">${h.innerHTML}</a>`
}

patch_all()
