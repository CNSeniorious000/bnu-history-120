from os import system
from re import DOTALL, search
from typing import Dict

content = open("./pyproject.toml").read()
if match := search(
    r'\[tool.poetry.dependencies\]\npython = "[^"]+"\n(.+?)\n\n',
    content,
    DOTALL,
):
    dependencies = match.group(1)
else:
    raise ValueError("No match found.")

dependencies_dict: Dict[str, str] = {}
for line in dependencies.split("\n"):
    key, value = search(r"([\w-]+) = (.+)", line).groups()  # type: ignore
    dependencies_dict[key] = value

print(dependencies_dict)

install_str_parts = ["python3 -m pip install"]

for k, v in dependencies_dict.items():
    if "{" in v:
        extras, version = search(r'extras = \["(.+)"\], version = "(.+)"', v).groups()  # type: ignore
        install_str_parts.append(f"{k}[{extras}]={version}")
    else:
        install_str_parts.append(f"{k}=" + v.strip('" '))

install_command = " ".join(install_str_parts).replace("=^", "==")

print(install_command)

system(install_command)
