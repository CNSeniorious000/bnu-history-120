from collections import Counter
from functools import lru_cache
from pathlib import Path
from typing import List, Literal

from markdown2 import markdown, markdown_path

markdown_extensions = ["header-ids"]


class University:
    def __init__(self, name: str, full_name: str):
        self.name = name
        self.full_name = full_name
        self.path = Path(f"./data/{name}")
        if not self.path.is_dir():
            raise NotADirectoryError(f"{name} is not a valid university name")

        self.categories: List[str] = []
        for path in self.path.iterdir():
            if path.is_dir():
                self.categories.append(path.name)

    @lru_cache(maxsize=None)
    def filter_category(self, category: str):
        return [Person(path.stem, self, category) for path in (self.path / category).glob("*.md")]

    @property
    def people(self):
        return sum(map(self.filter_category, self.categories), [])

    @property
    def html(self):
        return add_links(markdown_path(self.path / "index.md", extras=markdown_extensions))

    def __repr__(self):
        return self.name


class Person:
    def __init__(self, name: str, university: University, category: str):
        self.name = name
        self.university = university
        self.category = category
        self.path = university.path / category / f"{name}.md"
        self.url = f"/{university}/{category}/{name}"

        if not self.path.is_file():
            raise FileNotFoundError(f"{name} is not a valid person name")

        text = self.path.read_text("utf-8")

        if text.startswith("![]("):
            self.portrait = text[text.index("(") + 1 : text.index(")")]
            self.content = text[text.index("\n") + 1 :]
        else:
            self.portrait = None
            self.content = text

    @property
    def html(self):
        return add_links(markdown(self.content, extras=markdown_extensions), self.name)

    def __repr__(self):
        return self.name


@lru_cache(maxsize=None)
def render_university_html(name: str, /):
    return universities[name].html


@lru_cache(maxsize=None)
def render_person_html(name: str, university_name: str, category: str, /):
    return Person(name, universities[university_name], category).html


universities = {
    "北师大": University("北师大", "北京师范大学"),
    "女高师": University("女高师", "北京女子高等师范学校"),
    "辅大": University("辅大", "辅仁大学"),
}

people: List[Person] = [
    person for university in universities.values() for person in university.people
]

name_count_map = Counter((person.name for person in people))


def add_links(text: str, exclude_name: str = None):
    for name, count in name_count_map.items():
        if (count > 1 or name != exclude_name) and name in text:
            text = text.replace(name, f'<button type="button">{name}</button>')
    return text
