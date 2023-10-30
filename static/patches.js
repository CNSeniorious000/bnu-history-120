const preload_headers = new Headers()
preload_headers.append("x-bnu120-usage", "preload")
const preload_init_options = {
    method: "GET", redirect: "error", mode: "same-origin", headers: preload_headers
}
const cache = new Map()
const article = document.getElementById("article")

let current = location.href

function fetch_page(preload_url) {
    return cache.get(preload_url) ?? fetch(preload_url, preload_init_options).then(
        async response => cache.set(preload_url, await response.json()),
        (reason) => console.warn(reason)
    ).then(() => cache.get(preload_url))
}

function push_state(url) {
    history.pushState({url}, null, url)
    current = location.href
}

async function load_page(url) {
    let preload_url = "/api" + url
    if (!cache.has(preload_url)) await fetch_page(preload_url)
    let json = cache.get(preload_url)
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

// back to previous page
window.onpopstate = async () => {
    let to = split_hash(location.href)
    let from = split_hash(current)
    current = location.href
    if (to.path === from.path) return console.assert(to.hash !== from.hash, [to.hash, from.hash])
    let preload_url = "/api" + to.path
    let page_json = await fetch_page(preload_url)
    article.innerHTML = page_json["div"]
    document.title = page_json["title"]
    patch_hash_link()
    document.querySelectorAll("#markdown button").forEach(add_tooltip_creator)
}

// patch <a> tags
function enable_preloading(node) {
    // noinspection JSCheckFunctionSignatures
    console.assert(node.nodeName === "A", node.nodeName)
    let href = new URL(node.href)
    if (location.host !== href.host) return console.warn({from: location.host, to: href.host})
    if (location.pathname === href.pathname && location.search === href.search && location.host === href.host) {
        node.onclick = () => history.replaceState(null, null, node.href)
    }
    let url = href.pathname
    let preload_url = "/api" + url
    node.onmouseenter = () => fetch_page(preload_url)
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
            popper_hovered = button_hovered = false
        })
        return false
    }
}

function patch_all_preloading() {
    document.querySelectorAll("a").forEach(enable_preloading)
}

// enable hash links for scrolling
function patch_hash_link() {
    for (let h of document.querySelectorAll("#markdown [id]"))
        h.innerHTML = `<a href="#${h.id}">${h.innerHTML}</a>`
}

// cache people information mapping
let person_info_map = null

async function get_person_links(name) {
    if (person_info_map === null) person_info_map = await (await fetch("/api/people/dict")).json()
    return person_info_map[name]
}

// current situation
let popper_hovered = false
let button_hovered = false

function on_button_focus() {
    button_hovered = true
    tooltip.setAttribute("data-show", "")
    switchPopper(true)
    if (popperInstance !== null) popperInstance.update()
}

function on_button_blur() {
    button_hovered = false
    setTimeout(() => {
        if (button_hovered) return

        let taskId = setInterval(() => {
            if (!popper_hovered && !button_hovered) {
                tooltip.removeAttribute("data-show")
                switchPopper(false)
                clearInterval(taskId)
            }
        }, 1000 / 60)
    }, 200)
}

// patch tooltip popper to <button> tags
function add_tooltip_creator(button) {
    ["mouseenter", "focus"].forEach(e => button.addEventListener(e, on_button_focus));
    ["mouseleave", "blur"].forEach(e => button.addEventListener(e, on_button_blur));
    ["mouseenter", "focus"].forEach(e => button.addEventListener(e,
        () => get_person_links(button.innerText).then(links => {
            createPopper(button, links)
            return links
        }).then(links => {
            for (let url of links) fetch_page("/api" + new URL(url, current).pathname)  // force url-encode
            tips.childNodes.forEach(enable_preloading)
        })));
}

// make tooltips maintain themselves
function patch_person_info() {
    document.querySelectorAll("#markdown button").forEach(add_tooltip_creator);
    ["mouseenter", "focus"].forEach(e => tooltip.addEventListener(e, () => popper_hovered = true));
    ["mouseleave", "blur"].forEach(e => tooltip.addEventListener(e, () => popper_hovered = false));
}

// initialize popper.js
const tooltip = document.getElementById("tooltip")
const tips = document.getElementById("tips")

let popperInstance = null

function createPopper(button, links) {
    tips.innerHTML = ""
    for (let url of links) {
        let a = document.createElement("A")
        a.href = url
        a.innerText = url
        if (current.includes(encodeURI(url))) a.classList.add("current")
        tips.appendChild(a)
    }

    popperInstance = Popper.createPopper(button, tooltip, {
        placement: "top",
        modifiers: [
            {name: "offset", options: {offset: [0, 4]}},
            {name: "flip", enabled: true}
        ],
    })
}

function switchPopper(enable) {
    if (popperInstance === null) return
    popperInstance.setOptions(options => {
        return {
            ...options,
            modifiers: [
                ...options.modifiers,
                {name: 'eventListeners', enabled: enable},
            ],
        };
    })
}


patch_all_preloading()
patch_person_info()
patch_hash_link()
