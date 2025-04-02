import re

from rake_nltk import Rake

NOT_RELEVANT_KEYWORDS_FOR_TITLE = [
    "allah",
    "salam",
    "hamdou",
]


def _contains_arabic_letters(text: str) -> bool:
    # [\u0600-\u06FF] represents the Unicode range for Arabic letters
    arabic_pattern = re.compile(r"[\u0600-\u06FF]+")
    return bool(arabic_pattern.search(text))


def _get_keywords(text: str) -> list[str]:
    # import nltk
    # nltk.download("stopwords", download_dir=".")
    # nltk.download("punkt", download_dir=".")
    with open("./corpora/stopwords/french", "r") as file:
        stopwords = {line.strip() for line in file}

    r = Rake(
        stopwords=stopwords,
        punctuations={",", ".", "?", "!"},
        language="french",
        max_length=20,
    )
    r.extract_keywords_from_text(text)
    return r.get_ranked_phrases()


def _clean_keywords(keywords: list[str], max_char: int) -> list[str]:
    words_count = 0
    keywords_to_keep = []
    for keyword in keywords:
        if _contains_arabic_letters(text=keyword):
            continue
        elif any(
            not_relevant_kw in keyword.lower()
            for not_relevant_kw in NOT_RELEVANT_KEYWORDS_FOR_TITLE
        ):
            continue
        else:
            keywords_to_keep.append(keyword)
            words_count += len(keyword)
            if words_count >= max_char:
                break
    return keywords_to_keep


def generate_title(text: str) -> str:
    try:
        keywords = _get_keywords(text=text)
        keywords = _clean_keywords(keywords=keywords, max_char=30)
        title = " | ".join(keywords)
    except Exception as exc:
        print("Error on title generation:", exc)
        title = ""

    return title[:100]  # discord does not allow more than 100 char for the title
