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
    report_path = Path(__file__).with_name("matches_report.txt")

    if not csv_path.exists():
        print(f"Файл не найден: {csv_path}")
        return

    text = read_csv_text(csv_path)
    report_lines = []

    # Проходим по всем шаблонам и считаем количество совпадений в тексте CSV.
    for name, pattern in PATTERNS.items():
        matches_count = len(re.findall(pattern, text))
        # Формируем ту же строку, которую печатаем в консоль и сохраняем в отчет.
        line = f"{name}: {matches_count}"
        print(line)
        report_lines.append(line)

    # Собираем список строк в один текст с переносами и записываем в файл отчета.
    report_path.write_text("\n".join(report_lines), encoding="utf-8")
    print(f"\nСписок совпадений сохранен в файл: {report_path.name}")


if __name__ == "__main__":
    main()
