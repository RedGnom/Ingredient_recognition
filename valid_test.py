from dotenv import load_dotenv
import os
import sys

# Загрузка переменных окружения
load_dotenv()

# Чтение переменных окружения
bot_token = os.getenv("BOT_TOKEN")
api_roboflow = os.getenv("API_ROBOFLOW")
server_url = os.getenv("SERVER_URL")

# Проверка наличия api и токена
if not bot_token:
    print("Не найден токен для бота")
    sys.exit(1) 

if not api_roboflow:
    print("Укажите API с сайта Roboflow")
    sys.exit(1)

if not server_url:
    print("Не указан адрес сервера Roboflow")
    sys.exit(1) 





