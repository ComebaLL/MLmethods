import asyncio
import aiohttp
import time
from typing import List

# Количество страниц для загрузки
TOTAL_PAGES = 400
# Максимальное количество одновременных запросов 
CONCURRENT_REQUESTS = 50

# Базовый URL
BASE_URL = "https://httpbin.org/get"

def generate_urls(count: int) -> List[str]:
    """Генерирует список URL с уникальными параметрами, чтобы избежать кэширования."""
    return [f"{BASE_URL}?id={i}" for i in range(count)]

async def fetch(session: aiohttp.ClientSession, url: str, semaphore: asyncio.Semaphore) -> str:
    """Загружает одну страницу по URL с использованием менеджера контекста."""
    async with semaphore:
        try:
            async with session.get(url) as response:
                # Читаем тело ответа 
                html = await response.text()
                return html
        except Exception as e:
            print(f"Ошибка при загрузке {url}: {e}")
            return ""

async def main():
    # Генерируем список URL
    urls = generate_urls(TOTAL_PAGES)
    print(f"Начинаем загрузку {len(urls)} страниц")

    # Засекаем время начала
    start_time = time.perf_counter()

    # Создаём семафор для ограничения числа одновременных запросов
    semaphore = asyncio.Semaphore(CONCURRENT_REQUESTS)

    # Используем менеджер контекста для сессии 
    async with aiohttp.ClientSession() as session:
        # Создаём задачи для всех URL
        tasks = [fetch(session, url, semaphore) for url in urls]
        # Запускаем все задачи и ждём их завершения
        results = await asyncio.gather(*tasks)

    # Засекаем время окончания
    elapsed = time.perf_counter() - start_time

    # Подсчитываем успешные загрузки 
    successful = sum(1 for html in results if html)
    print(f"Загрузка завершена за {elapsed:.2f} секунд")
    print(f"Успешно загружено: {successful} из {TOTAL_PAGES} страниц")

if __name__ == "__main__":
    asyncio.run(main())