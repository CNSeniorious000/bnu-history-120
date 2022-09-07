from markdown2 import markdown_path, markdown
from functools import cached_property, cache
from os.path import isdir
from os import walk

extras = ["header-ids"]


class University:
    universities = []

    def __new__(cls, name, categories):
        if not isdir(directory := f"./data/{name}"):
            raise NotADirectoryError(f"{directory} is not a directory")

        for university in cls.universities:
            if university.name == name:
                return university

        self = object.__new__(cls)
        cls.universities.append(self)
        return self

    def __init__(self, name, categories: list[str]):
        self.name = name
        self.categories = categories
        self.path = f"./data/{name}"

    @cached_property
    def people(self):
        people = []
        for category in self.categories:
            people.extend([
                Person(path.removesuffix(".md"), self, category)
                for path in next(walk(f"{self.path}/{category}"))[2]
            ])

        return people

    @cached_property
    def html(self):
        return markdown_path(f"{self.path}/index.md", extras=extras)

    def __repr__(self):
        return self.name

    @classmethod
    def get_all_people(cls) -> list["Person"]:
        return sum([university.people for university in cls.universities], [])


class Person:
    @cache
    def __new__(cls, *args, **kwargs):
        return object.__new__(cls)

    def __init__(self, name, university: University, category: str):
        self.name = name
        self.university = university
        self.category = category
        self.path = f"{university.path}/{category}/{name}.md"

        with open(self.path, encoding="utf-8") as f:
            text = f.read()

        if text.startswith("![]("):
            self.portrait = text[text.index("(") + 1:text.index(")")]
            self.content = text[text.index("\n") + 1:]
        else:
            self.portrait = None
            self.content = text

    @cached_property
    def html(self):
        return markdown(self.content, extras=extras)

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.path)

    def __eq__(self, person):
        return isinstance(person, Person) and person.path == self.path


University("北师大", ["教师", "校友", "校长"])
University("女高师", ["教师", "校友", "校长"])
University("辅大", ["教师", "校友", "校长", "创始人"])

if __name__ == '__main__':
    people = University.get_all_people()
    print(University("北师大", []).html)
