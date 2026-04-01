import os
import aiofiles
import bson
import config
from database import db_manager

async def sync_disk_to_db(state):
    """Берет скачанные файлы и загружает их в базу данных"""
    print(" Синхронизация локальных файлов с MongoDB")
    
    # Собираем список всех файлов в папке images
    files = [f for f in os.listdir(config.IMG_DIR)]
    
    # Если в стейте нет секции для базы, создадим её
    if "db_sync" not in state:
        state["db_sync"] = {}

    for file_name in files:
        # Если файл уже в базе, пропускаем
        if state["db_sync"].get(file_name) == "synced":
            continue

        file_path = os.path.join(config.IMG_DIR, file_name)
        
        try:
            # Читаем файл с диска
            async with aiofiles.open(file_path, "rb") as f:
                img_data = await f.read()

            # Готовим документ для базы
            # Имя и хэш можно вытащить из имени файла
            doc = {
                "file_name": file_name,
                "data": bson.Binary(img_data),
                "size_bytes": os.path.getsize(file_path)
            }

            # Сохраняем в MongoDB
            await db_manager.collection.update_one(
                {"file_name": file_name},
                {"$set": doc},
                upsert=True
            )

            # Отмечаем успех в стейте
            state["db_sync"][file_name] = "synced"
            print(f" [DB] Загружено: {file_name}")
            
        except Exception as e:
            print(f" Ошибка загрузки файла {file_name} в базу: {e}")