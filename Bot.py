import os
import telebot
from telebot import types
from dotenv import load_dotenv
from Analazer import detect_objects
from Configuration import models, synonyms
from valid_test import bot_token
from Parser import *
from keyboards_for_messages import *


# Создание экземпляра бота
bot = telebot.TeleBot(bot_token)

# Приветственное сообщение
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Приветствую, я бот по подбору рецептов на основе фото. Отправьте изображение, чтобы я мог обработать его и выдать доступные вам рецепты.")

# Ожидание отправки фото от пользователя
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    try:
        # Получаем id фото
        file_id = message.photo[-1].file_id
        
        # Получаем информацию о файле
        file_info = bot.get_file(file_id)
        
        # Формируем прямую ссылку на файл
        file_url = f"https://api.telegram.org/file/bot{bot.token}/{file_info.file_path}"

        bot.send_message(message.chat.id, "Веду обработку изображения, ожидайте...")
        # Распознавание объектов с фото
        objects = detect_objects(file_url, models, synonyms)
        # objects = ["огурец", "помидор"]

        if objects:
            objects_str = "\n".join(objects) 
            bot.send_message(message.chat.id, f"Обнаруженные объекты:\n{objects_str}")
            
            # Запрашиваем, хочет ли пользователь изменить набор ингредиентов
            ask_to_edit_ingredients(message, objects)

        else:
            bot.send_message(message.chat.id, "На изображении не обнаружено объектов")

    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка: {e}")

def ask_to_edit_ingredients(message, objects):
    
    
    bot.send_message(
        message.chat.id,
        "Хотите ли изменить набор ингредиентов?",
        reply_markup=yes_no_keyboard
    )
    
    # Сохраняем текущие объекты в контексте пользователя
    user_states[message.chat.id] = {"action": None, "objects": objects}

# Словарь для хранения состояния пользователей
user_states = {}

@bot.callback_query_handler(func=lambda call: True)
def handle_choice(call):
    chat_id = call.message.chat.id
    bot.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=call.message.message_id,
            reply_markup=None
        )
    if call.data == "yes":
        # Пользователь хочет изменить ингредиенты
        
        
        bot.send_message(chat_id, "Введите ингредиенты для удаления через запятую:")
        # Устанавливаем состояние "удаление"
        user_states[chat_id]["action"] = "removal"
    
    elif call.data == "no":
        # Пользователь не хочет изменять ингредиенты
        
        objects = user_states[chat_id]["objects"]
        send_recipes(chat_id, objects)

    elif call.data == "continue":
    # Извлечение ссылки из подписи сообщения
        try:
            link = call.message.caption.split("Ссылка: ")[1].strip()
            show_recept(link, chat_id)
            
        except Exception as e:
            bot.send_message(chat_id, "Не удалось извлечь ссылку из рецепта.")
            print(f"Ошибка: {e}")
        

@bot.message_handler(func=lambda message: True)
def process_user_input(message):
    """
    Обрабатывает ввод пользователя в зависимости от состояния.
    """
    chat_id = message.chat.id
    user_text = message.text.strip()
    
    if chat_id in user_states:
        state = user_states[chat_id]
        objects = state["objects"]
        
        if state["action"] == "removal":
            
            if(without_changes(message)):
                bot.send_message(message.chat.id, "Изменения отсутсвуют.")
            else:
                # Обработка удаления
                remove_items = [item.strip() for item in user_text.split(",") if item.strip()]
            
                # Удаляем указанные ингредиенты
                for item in remove_items:
                    if item not in objects:
                        bot.send_message(chat_id, "Данного продукта нет в списке:")
                        return
                    else:
                        objects.remove(item)
            
            # Переходим к добавлению
            bot.send_message(chat_id, "Введите ингредиенты для добавления через запятую в единственном числе или не добавлять ничего, введя минус:")
            user_states[chat_id]["action"] = "addition"
        
        elif state["action"] == "addition":

            
            if(without_changes(message)):
                bot.send_message(message.chat.id, "Изменения отсутсвуют.")
            else:
                # Обработка добавления
                add_items = [item.strip() for item in user_text.split(",") if item.strip()]
            
                # Добавляем новые ингредиенты
                objects.extend(add_items)
            
                # Убираем дубликаты
                objects = list(set(objects))
            
                # Удаляем состояние
                del user_states[chat_id]
            
                # Отправляем обновленный список
                updated_ingredients_str = ", ".join(objects)
                bot.send_message(chat_id, f"Обновленные ингредиенты: {updated_ingredients_str}")
            
            # Переходим к поиску рецептов
            bot.send_message(chat_id, "Начинаю поиск рецептов:")
            send_recipes(chat_id, objects)

        
    else:
        # Если непредвиденный ввод данных от пользователя
        bot.reply_to(message, "Незапланированный ввод информации")

def without_changes(message):
    user_input = message.text.strip()
    if user_input == "-" or user_input.lower() == "ничего":
        return True
    else:
        return False

def send_recipes(chat_id, objects):
    """
    Ищет рецепты по списку объектов и отправляет их пользователю.
    """
    try:
        bot.send_message(chat_id, "Веду поиск рецептов, ожидайте...")
        
        # Поиск рецептов
        recipes = search_recipes(objects)
        
        if not recipes:
            bot.send_message(chat_id, "Рецепты не найдены.")
            return
        
        # Отправка рецептов
        bot.send_message(chat_id, "Найденные рецепты:")
        for i, recipe in enumerate(recipes, 1):
            # Получаем ингредиенты и очищаем от лишних пробелов/переносов
            ingredients_text = recipe['ingredients'].strip()
    
            # Удаляем все переносы строк и лишние пробелы между словами
            ingredients_text = ' '.join(ingredients_text.split())
    
            # Формируем caption
            caption = (
                f"{i}. {recipe['title']}\n"
                f"Требуемые {ingredients_text}\n"
                f"Ссылка: {recipe['link']}"

            )
    
            bot.send_photo(
                chat_id,
                photo=recipe['image'],
                caption=caption,
                reply_markup=continue_keyboard
            )
    
    except Exception as e:
        bot.send_message(chat_id, f"Произошла ошибка: {e}")

def show_recept(link, chat_id):
            # Получение данных рецепта
            recipe_data = parse_recipe(link)
        
            if not recipe_data:
                bot.send_message(chat_id, "Не удалось получить данные о рецепте.")
            else:
                # Отправка ингредиентов
                ingredients_text = "\n".join([f"- {ing}" for ing in recipe_data["ingredients"]])
                bot.send_message(chat_id, f"Ингредиенты:\n{ingredients_text}")
            
                # Отправка шагов приготовления
                for i, step in enumerate(recipe_data["steps"], 1):
                    caption = f"{i}. {step['text']}"
                    bot.send_photo(
                        chat_id,
                        photo=step["image"],
                        caption=caption
                    )

# Запуск бота
bot.polling(none_stop=True)