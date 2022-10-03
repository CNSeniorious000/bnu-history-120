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

window.onpopstate = async () => {
    let to = split_hash(location.href)
    let from = split_hash(current)
    current = location.href
    if (to.path === from.path) return console.assert(to.hash !== from.hash, [to.hash, from.hash])
    let api_url = "/api" + to.path
    await get_page_data(api_url).then(json => {
        article.innerHTML = json["div"]
        document.title = json["title"]
    }).then(patch_hash_link).then(() => document.querySelectorAll("span").forEach(add_tooltip_creator))
}

// patch all <a> tags

function enable_preloading(node) {
    // noinspection JSCheckFunctionSignatures
    console.assert(node.nodeName === "A", node.nodeName)
    let href = new URL(node.href)
    if (location.host !== href.host) return console.warn({from: location.host, to: href.host})
    if (location.pathname === href.pathname && location.search === href.search && location.host === href.host) {
        node.onclick = () => {
            history.replaceState(null, null, node.href)
            return false
        }
        return
    }
    let url = href.pathname
    let api_url = "/api" + url
    node.onmouseenter = () => preload(api_url)  // BUG: can't enable preloading features
    node.onclick = () => {
        load_page(url).then(() => {
            if (!current.includes("#"))
                // noinspection JSCheckFunctionSignatures
                scrollTo({top: 0, behavior: "instant"})
            return url
        }).then(push_state).then(patch_hash_link).then(() => {
            // noinspection JSCheckFunctionSignatures
            scrollTo({top: 0, behavior: "instant"})
        }).then(patch_person_info).then(() => {
            tip_hovered = span_hovered = false
        })
        return false
    }
}

function patch_all_preloading() {
    document.querySelectorAll("a").forEach(enable_preloading)
}

function patch_hash_link() {
    for (let h of document.querySelectorAll("#markdown [id]"))
        h.innerHTML = `<a href="#${h.id}">${h.innerHTML}</a>`
}

let person_info_map = null

async function get_person_links(name) {
    if (person_info_map === null) person_info_map = await (await fetch("/api/people/dict")).json()
    return person_info_map[name]
}

let tip_hovered = false
let span_hovered = false

function on_span_focus() {
    span_hovered = true
    tooltip.setAttribute("data-show", "")
    switchPopper(true)
    if (popperInstance !== null) popperInstance.update()
}

function on_span_blur() {
    span_hovered = false
    setTimeout(() => {
        if (span_hovered) return

        let taskId = setInterval(() => {
            if (!tip_hovered && !span_hovered) {
                tooltip.removeAttribute("data-show")
                switchPopper(false)
                clearInterval(taskId)
            }
        }, 1000 / 60)
    }, 200)
}

function add_tooltip_creator(span) {
    ["mouseenter", "focus"].forEach(e => span.addEventListener(e, on_span_focus));
    ["mouseleave", "blur"].forEach(e => span.addEventListener(e, on_span_blur));
    span.onmouseenter = () => get_person_links(span.innerText).then(
        links => createPopper(span, links)
    ).then(
        () => tips.childNodes.forEach(enable_preloading)
    )
}

function patch_person_info() {
    document.querySelectorAll("span").forEach(add_tooltip_creator);
    ["mouseenter", "focus"].forEach(e => tooltip.addEventListener(e, () => tip_hovered = true));
    ["mouseleave", "blur"].forEach(e => tooltip.addEventListener(e, () => tip_hovered = false));
}

patch_all_preloading()
patch_person_info()
