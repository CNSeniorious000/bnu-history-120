from functools import cache, cached_property
from os import walk
from os.path import isdir, isfile

from markdown2 import markdown, markdown_path

extras = ["header-ids"]


class University:
    universities = []

    def __new__(cls, name, *args, **kwargs):
        if not isdir(f"./data/{name}"):
            raise NotADirectoryError(f"{name} is not a valid university name")

        for university in cls.universities:
            if university.name == name:
                return university

        return object.__new__(cls)

    def __init__(self, name, categories: list[str] = (), full_name=""):
        self.name = name
        if self in self.universities:
            return
        self.full_name = full_name
        self.categories = categories
        self.path = f"./data/{name}"
        self.universities.append(self)

    @cache
    def filter_category(self, category: str):
        assert category in self.categories
        return [
            Person(path.removesuffix(".md"), self, category)
            for path in next(walk(f"{self.path}/{category}"))[2]
        ]

    @cached_property
    def people(self):
        return sum((self.filter_category(category) for category in self.categories), [])

    @cached_property
    def html(self):
        return mark_people(markdown_path(f"{self.path}/index.md", extras=extras))

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, university):
        return isinstance(university, University) and university.name == self.name

    @classmethod
    def get_all_people(cls) -> list["Person"]:
        return sum([university.people for university in cls.universities], [])


class Person:
    @cache
    def __new__(cls, name, university, category):
        if not isdir(directory := f"{university.path}/{category}"):
            raise NotADirectoryError(f"{category} is not a valid category name")
        if not isfile(f"{directory}/{name}.md"):
            raise FileNotFoundError(f"{name} is not a valid person name")
        return object.__new__(cls)

    def __init__(self, name, university: University, category):
        self.name = name
        self.university = university
        self.category = category
        self.path = f"{university.path}/{category}/{name}.md"

        with open(self.path, encoding="utf-8") as f:
            text = f.read()

        if text.startswith("![]("):
            self.portrait = text[text.index("(") + 1 : text.index(")")]
            self.content = text[text.index("\n") + 1 :]
        else:
            self.portrait = None
            self.content = text

    @cached_property
    def html(self):
        return markdown(mark_people(self.content), extras=extras)

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.path)

    def __eq__(self, person):
        return isinstance(person, Person) and person.path == self.path


University("北师大", ["教师", "校友", "校长"], "北京师范大学")
University("女高师", ["教师", "校友", "校长"], "北京女子高等师范学校")
University("辅大", ["教师", "校友", "校长", "创始人"], "辅仁大学")

all_people = University.get_all_people()


def mark_people(text: str):
    for person in all_people:
        if (name := person.name) in text and (
            button := f'<button type="button">{name}</button>'
        ) not in text:
            text = text.replace(name, button)
    return text
