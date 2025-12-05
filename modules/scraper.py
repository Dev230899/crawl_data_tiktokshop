import re
import unicodedata


def decode_text(text: str):
    normal_text = ""
    for char in text:
        if unicodedata.category(char) != "So":
            normal_text += (
                unicodedata.normalize("NFKD", char)
                .encode("ascii", "ignore")
                .decode("utf-8")
            )
        else:
            normal_text += char
    return normal_text


def get_number(text):
    test = ""
    for l in text:
        if l.isnumeric():
            test += l
        else:
            test += ""
    return test


def get_phone(text):
    pat_phones = [
        r"0[\D]{0,}\d[\D]{0,}\d[\D]{0,}\d[\D]{0,}\d[\D]{0,}\d[\D]{0,}\d[\D]{0,}\d[\D]{0,}\d[\D]{0,}\d[\D]{0,}",
        r"84[\D]{0,}[\d][\D]{0,}\d[\D]{0,}\d[\D]{0,}\d[\D]{0,}\d[\D]{0,}\d[\D]{0,}\d[\D]{0,}\d[\D]{0,}\d[\D]{0,}",
        r"02[\D]{0,}\d[\D]{0,}\d[\D]{0,}\d[\D]{0,}\d[\D]{0,}\d[\D]{0,}\d[\D]{0,}\d[\D]{0,}\d[\D]{0,}\d",
    ]
    phones = []
    text = decode_text(text)
    for pat_phone in pat_phones:
        text_p = text
        for t in text_p.split("\n"):
            for phone in re.findall(pat_phone, t):
                phone = get_number(phone)
                tmp = 1 if phone[0] == "0" else 2
                if (
                    (phone[tmp] not in "01246" and 9 < len(phone) < 12)
                    or phone[:2] == "02"
                    and len(phone) == 11
                ):
                    phones.append(phone)
    return phones


def get_links(desc: str):
    desc = decode_text(desc)
    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    urls = re.findall(regex, desc)
    if urls:
        return [u[0] for u in urls if u]
    return None
