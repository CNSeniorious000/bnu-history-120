from pathlib import Path


def normalize(string: str):
    return (
        string.replace(",", "，")
        # .replace(":", "：")  # https://
        # .replace("(", "（")  # ![]()
        # .replace(")", "）")  # ![]()
        .replace("?", "？")
        .replace(";", "；")
        .replace("？)", "?)")  # (yyyy-?)
        .replace("？）", "?）")  # （yyyy-?）
        .replace("—", "-")
        .replace("--", "——")  # Chinese dash
        .replace("——-", "---")  # markdown split line
        .replace("~", "-")
        .replace("， ", "，")
        .replace("。 ", "。")
        .replace("； ", "；")
        .replace("\r\n", "\n")
    )


if __name__ == "__main__":
    for document in Path().glob("*/**/*.md"):
        with document.open("r+", encoding="utf-8") as md:
            text = md.read()
            md.seek(0)
            md.write(normalize(text))
            md.truncate()
