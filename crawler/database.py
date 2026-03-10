from motor.motor_asyncio import AsyncIOMotorClient
import config

class MongoDB:
    def __init__(self):
        self.client = None
        self.db = None
        self.collection = None

    def connect(self):
        """Инициализирует подключение к MongoDB"""
        self.client = AsyncIOMotorClient(config.MONGO_URI)
        self.db = self.client[config.DB_NAME]
        self.collection = self.db[config.COLLECTION_NAME]

    def close(self):
        """Закрывает подключение"""
        if self.client:
            self.client.close()

# Создаем экземпляр для импорта в другие модули
db_manager = MongoDB()