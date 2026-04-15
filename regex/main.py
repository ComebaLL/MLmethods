from pathlib import Path
import re


# r raw string - строка, в которой нет специальных символов
# словарь с регурялным выражениями
PATTERNS = {
    # \b — граница слова, \d{2} — ровно 2 цифры, \. — символ точки, \d{4} — ровно 4 цифры.
    "дата дд.мм.гггг": r"\b\d{2}\.\d{2}\.\d{4}\b",
    # \b — границы слова, текст внутри — точное совпадение слова PlayStation.
    "слово PlayStation": r"\bPlayStation\b",
    # \b — границы слова, (|||) список искомых слов
    "слова Xiaomi|Apple|Mail.Ru": r"\b(Xiaomi|Apple|Mail.Ru)\b",

    "Телефон": r"(?:\+7|8)\s*\(?\d{3}\)?[\s-]*\d{3}[\s-]*\d{2}[\s-]*\d{2}",

    "Email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",

    "URLs": r"\bhttps?:\/\/(?:[A-Za-z0-9-]+\.)+[A-Za-z]{2,}(?:\/[^\s]*)?\b"

}


def read_csv_text(file_path: Path) -> str:
    """чтение csv файла"""
    for encoding in ("cp1251", "utf-8"):
        try:
            return file_path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    return file_path.read_text(encoding="utf-8", errors="replace")


def main() -> None:
    csv_path = Path(__file__).with_name("news (1).csv")

    if not csv_path.exists():
        print(f"Файл не найден: {csv_path}")
        return

    text = read_csv_text(csv_path)

    # Считаем, сколько раз каждый regex-шаблон встретился в файле.
    for name, pattern in PATTERNS.items():
        matches_count = len(re.findall(pattern, text))
        print(f"{name}: {matches_count}")


if __name__ == "__main__":
    main()
