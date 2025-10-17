from collections import defaultdict
from functools import cache
from pathlib import Path
from urllib.parse import quote

from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

from .data import Person, people, universities
from .models import Categories, Names, Universities

router = APIRouter()


@router.get("/sitemap.xml")
@cache
def get_sitemap():
    from xml.etree.ElementTree import Element, SubElement, tostring

    base_url = "https://bnu.muspimerol.site"
    urlset = Element("urlset")
    urlset.set("xmlns", "http://www.sitemaps.org/schemas/sitemap/0.9")

    # Home page
    url = SubElement(urlset, "url")
    SubElement(url, "loc").text = base_url
    SubElement(url, "priority").text = "1.0"

    # About page
    url = SubElement(urlset, "url")
    SubElement(url, "loc").text = f"{base_url}/about"
    SubElement(url, "priority").text = "0.8"

    # Swagger Docs
    url = SubElement(urlset, "url")
    SubElement(url, "loc").text = f"{base_url}/docs"
    SubElement(url, "priority").text = "0.6"

    # Redoc Docs
    url = SubElement(urlset, "url")
    SubElement(url, "loc").text = f"{base_url}/redoc"
    SubElement(url, "priority").text = "0.6"

    # Universities
    for uni_name in universities.keys():
        url = SubElement(urlset, "url")
        SubElement(url, "loc").text = f"{base_url}/{uni_name}"
        SubElement(url, "priority").text = "0.9"

    # People
    for person in people:
        url = SubElement(urlset, "url")
        SubElement(url, "loc").text = f"{base_url}{person.url}"
        SubElement(url, "priority").text = "0.7"

    return PlainTextResponse(tostring(urlset, encoding="unicode"), media_type="application/xml")


def linkify(text: str, from_whom: Person | None = None):
    related = [p for p in people if p != from_whom and p.name in text]

    print(related)

    if not related:
        return text

    title_map: dict[str, list[tuple[str, str]]] = defaultdict(list)

    for p in related:
        title_map[p.name].append((p.university.name, p.category))

    return (
        text.rstrip()
        + "\n\n---\n\n相关人物：\n\n"
        + "\n".join(
            f"{name}（{'、'.join(f'[{u}{c}](/{quote(u)}/{quote(c)}/{quote(name)}.md)' for u, c in titles)}）"
            for name, titles in title_map.items()
        )
    )


@router.get("/{university}.md", response_class=PlainTextResponse)
def get_university_note(university: Universities):
    u = universities[university]
    return linkify(f"# {u.full_name}\n\n{(u.path / 'index.md').read_text('utf-8')}")


@router.get("/{university}/{category}/{name}.md", response_class=PlainTextResponse)
def get_person_note(university: Universities, category: Categories, name: Names):
    p = Person(name, universities[university], category)
    return linkify(f"# {name} - {university}{category}\n\n{p.content.lstrip()}", p)


@router.get("/llms.txt", response_class=PlainTextResponse)
def get_llms_txt():
    preface = "北京师范大学作为中国最高师范学府，前身为1902年成立的京师大学堂师范馆，距今已有接近120年历史。北京师范大学身处北京地区，经历了清末改革、辛亥革命清帝退位、国民政府北伐初步统一、北平和平解放等重大事件，积极参与了五四运动、一二九运动等学生运动，具有经历的丰富性和思想的先进性，是近代时期中国救亡图存运动的见证者；北京师范大学是全国最高等级的师范院校，从北师大出版社出版的众多中小学教辅和教材，到培养出的各式各样的中小学基础教育教师，以“学为人师，行为世范”为校训的北师大是全国基础教育发展和改革的积极推动者；北京师范大学积极投身国家事业，发起“四有”好老师启航计划、“志远计划”推动中西部贫困地区教育事业发展，是中国扶贫减贫事业重要的教育支柱。北师大近120周年的历史，既是中国近代仁人志士和有识之士救亡图存的历程，也是中国高等教育发展壮大的过程，更是中华民族从危急时刻转危为安，踏上中华民族伟大复兴征程的见证。"

    return "\n\n".join(
        (
            "# BNU 120 校史百科 https://bnu.muspimerol.site/",
            f"> {preface}",
            Path("readme.md").read_text("utf-8"),
            "## 校史",
            "\n".join(f"- [{u.full_name}](/{quote(u.name)}.md)" for u in universities.values()),
            "## 人物",
            "\n".join(
                f"- [{p.name} - {p.university.name}{p.category}](/{quote(p.university.name)}/{quote(p.category)}/{quote(p.name)}.md)"
                for p in people
            ),
        )
    )
