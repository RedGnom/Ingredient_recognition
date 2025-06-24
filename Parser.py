import requests
from bs4 import BeautifulSoup
import urllib.parse

def build_search_url(ingredients):
    """
    Формирует URL для поиска рецептов на основе списка ингредиентов.
    """
    base_url = "https://www.povarenok.ru/recipes/search/"
    
    # Кодируем каждый ингредиент url кодировку Windows-1251
    encoded_ingredients = ",".join(
        urllib.parse.quote(ing, encoding="windows-1251") for ing in ingredients
    )
    
    # Полный адрес страницы с рецептами
    full_url = f"{base_url}?ing={encoded_ingredients}"
    return full_url

def search_recipes(ingredients):
    """
    Ищет рецепты на сайте povarenok.ru по списку ингредиентов.
    """
    search_url = build_search_url(ingredients)
    
    try:
        
        response = requests.get(search_url)
        response.raise_for_status()  # Проверяем статус ответа
        
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        
        recipes = soup.select("article.item-bl")[:5]  # Берем первые 5 рецептов
        
        results = []
        for recipe in recipes:
            try:
                link = recipe.select_one("a")["href"]
                title = recipe.select_one("h2").text.strip()
                
                img_element = recipe.select_one("img")
                img_src = img_element["src"] if img_element else "Изображение отсутствует"
                if img_src.startswith("/"):
                    img_src = f"https://www.povarenok.ru{img_src}"

                try:
                    article_tags = recipe.select_one("div.article-tags")
                    ingredients_elements = article_tags.select("span.list")
                    ingredients = ", ".join([elem.text.strip() for elem in ingredients_elements])
                except Exception:
                    ingredients = "Ингредиенты не найдены"
                
                results.append({
                    "title": title,
                    "link": link,
                    "image": img_src,
                    "ingredients": ingredients
                })
            except Exception as e:
                print(f"Ошибка при обработке рецепта: {e}")
                continue
        
        return results
    
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return []

def parse_recipe(link):
    """
    Парсит страницу рецепта по ссылке.
    
    :param link: Ссылка на страницу рецепта.
    :return: Словарь с ингредиентами и шагами приготовления.
    """
    try:
        # Отправка GET-запроса
        response = requests.get(link)
        response.raise_for_status()  # Проверяем статус ответа
        
        # Парсинг HTML с помощью BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Извлечение названия рецепта
        title = soup.select_one("h1").text.strip() if soup.select_one("h1") else "Название не найдено"
        
        # Парсинг ингредиентов
        ingredients_bl = soup.select_one("div.ingredients-bl")
        ingredients = []
        if ingredients_bl:
            for li in ingredients_bl.select("li[itemprop='recipeIngredient']"):
                spans = li.select("span")
                ingredient_parts = [span.text.strip() for span in spans]  # Извлекаем текст из всех <span>
                
                # Формируем строку с пробелами и тире между частями
                ingredient_text = " - ".join(ingredient_parts)
                ingredients.append(ingredient_text)
        
        # Парсинг шагов приготовления
        steps = []
        recipe_instructions = soup.select_one("ul[itemprop='recipeInstructions']")
        if recipe_instructions:
            for step in recipe_instructions.select("li.cooking-bl"):
                # Извлечение изображения
                img_tag = step.select_one("a img")
                img_url = img_tag["src"] if img_tag and "src" in img_tag.attrs else "Изображение отсутствует"
                
                # Извлечение текста шага
                text = step.select_one("p").text.strip() if step.select_one("p") else "Текст шага отсутствует"
                
                steps.append({
                    "image": img_url,
                    "text": text
                })
        
        # Формирование результата
        recipe_data = {
            "title": title,
            "ingredients": ingredients,
            "steps": steps,
            "link": link
        }
        return recipe_data
    
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return None


# Пример использования
# if __name__ == "__main__":
#     ingredients = ["помидор", "огурец"]
#     recipes = search_recipes(ingredients)
#     for recipe in recipes:
#         print(recipe)