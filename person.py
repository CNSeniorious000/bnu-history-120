from functools import cached_property, cache
from os import walk


class University:
    universities = []

    @cache
    def __new__(cls, *args, **kwargs):
        self = object.__new__(cls)
        cls.universities.append(self)
        return self

    def __init__(self, name: str, categories: tuple):
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

    def __repr__(self):
        return self.name

    @classmethod
    def get_all_people(cls):
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

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.path)

    def __eq__(self, person):
        return isinstance(person, Person) and person.path == self.path


if __name__ == '__main__':
    University("北师大", ("教师", "校友", "校长"))
    University("女高师", ("教师", "校友", "校长"))
    University("辅大", ("教师", "校友", "校长", "创始人"))
    people = University.get_all_people()
    assert len(people) == len(set(people))
    print(len(people))
    print(len(set(map(Person.__repr__, people))))
