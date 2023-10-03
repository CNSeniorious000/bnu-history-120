"""static site generation"""

from asyncio import run
from collections import namedtuple
from pathlib import Path

from httpx import AsyncClient

from main import app

Entry = namedtuple("Entry", "path slug")


def api_entry(slug: str):
    """shortcut for constructing an JSON endpoint"""

    return Entry(f"{slug}.json", slug)


def page_entry(slug: str):
    """shortcut for constructing an HTML endpoint"""
    return Entry(f"{slug}.html", slug)


def normal_entry(slug: str):
    """shortcut for constructing a ordinary endpoint"""
    return Entry(slug, slug)


def find_entries():
    """get all the urls to scrap"""

    entries = [
        Entry("index.html", ""),
        page_entry("about"),
        normal_entry("robots.txt"),
        normal_entry("common.css"),
        normal_entry("api/people/list"),
        normal_entry("api/people/dict"),
        # FastAPI
        page_entry("docs"),
        page_entry("redoc"),
        normal_entry("openapi.json"),
    ]

    root = Path("data")

    for path in root.glob("**/*.md"):
        if path.stem == "index":  # university page
            slug = str(path.relative_to(root).parent)
            entries.append(page_entry(slug))
            entries.append(api_entry(f"api/{slug}"))
        else:
            slug = str(path.relative_to(root).with_suffix(""))
            entries.append(page_entry(slug))
            entries.append(api_entry(f"api/{slug}"))

    return entries


client = AsyncClient(
    app=app,
    base_url="https://<SSG>",
    headers={"accept-encoding": "identity"},
)


def save_one(path: Path, content: bytes, /):
    """save a file after ensuring its directory exists"""

    if not path.parent.is_dir():
        path.parent.mkdir(parents=True)

    path.write_bytes(content)


static = Path("static")


async def scrap_one(entry: Entry):
    """save a response"""

    response = await client.get(entry.slug)
    save_one(static / entry.path, response.content)


async def scrap_all():
    """save all the responses"""

    for entry in find_entries():
        await scrap_one(entry)


if __name__ == "__main__":
    from time import perf_counter

    t = perf_counter()
    run(scrap_all())
    print(f"finished SSG in {perf_counter() - t :.2f}s")