import os
from inference_sdk import InferenceHTTPClient
from Configuration import models, synonyms
from valid_test import api_roboflow, server_url
def detect_objects(image_path, models, synonyms=None):
    
    if synonyms is None:
        synonyms = {}
    
    # Доступ к docker серверу от Roboflow
    client = InferenceHTTPClient(
        api_url=server_url,
        api_key=api_roboflow
    )
    
    detected_objects = set()
    
    for model in models:
        result = client.infer(image_path, model_id=model)
        if "predictions" in result:
            for pred in result["predictions"]:
                class_name = pred["class"]
                normalized_name = synonyms.get(class_name, class_name)  # Перевод на русский предсказаний от модели
                detected_objects.add(normalized_name)
    
    return sorted(detected_objects)

# Секция для проверки моделей отдельно от бота
if __name__ == "__main__":
    
    IMAGE_PATH = "example.jpg"
    
    objects = detect_objects(IMAGE_PATH, models, synonyms)
    print(objects)  
