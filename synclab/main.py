import requests
import time
from typing import List

# Количество страниц для загрузки
TOTAL_PAGES = 400
# Базовый URL
BASE_URL = "https://httpbin.org/get"

def generate_urls(count: int) -> List[str]:
    """Генерирует список URL с уникальными параметрами."""
    return [f"{BASE_URL}?id={i}" for i in range(count)]

def fetch(session: requests.Session, url: str) -> str:
    """Загружает одну страницу синхронно с использованием менеджера контекста."""
    try:
        # Менеджер контекста для HTTP-запроса
        with session.get(url) as response:
            # Читаем текст ответа
            html = response.text
            return html
    except Exception as e:
        print(f"Ошибка при загрузке {url}: {e}")
        return ""

def main():
    urls = generate_urls(TOTAL_PAGES)
    print(f"Начинаем загрузку {len(urls)} страниц")

    start_time = time.perf_counter()

    successful = 0
    # Менеджер контекста для сессии
    with requests.Session() as session:
        for idx, url in enumerate(urls):
            result = fetch(session, url)
            if result:
                successful += 1
            # Прогресс каждые 50 запросов
            if (idx + 1) % 50 == 0:
                print(f"Загружено {idx + 1} из {TOTAL_PAGES}")

    elapsed = time.perf_counter() - start_time
    print(f"Загрузка завершена за {elapsed:.2f} секунд")
    print(f"Успешно загружено: {successful} из {TOTAL_PAGES} страниц")

if __name__ == "__main__":
    main()