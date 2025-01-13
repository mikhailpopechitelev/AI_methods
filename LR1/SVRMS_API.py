import requests
import os
from SVRMS_CONST import *
import json

class AudioProcessorAPI:
    _instance = None

    def __new__(cls, api_key, api_host):
        if cls._instance is None:
            cls._instance = super(AudioProcessorAPI, cls).__new__(cls)
            cls.api_key = api_key
            cls.api_host = api_host
            cls.api_url = SVRMS_URL
        return cls._instance

    def __call__(self, file_path):
        """Отправляет аудиофайл на API и возвращает путь к обработанному файлу."""
        headers = {
            "x-rapidapi-key": self.api_key,
            "x-rapidapi-host": self.api_host,
        }

        # Открываем файл для отправки
        with open(file_path, "rb") as file:
            files = {"file": file}
            response = requests.post(self.api_url, files=files, headers=headers)

        # Проверка ответа от API
        if response.status_code == 200:
            # Предполагаем, что API возвращает аудиофайл
            output_file = os.path.join(os.path.dirname(file_path), "output_audio_svrms.mp3")
            with open(output_file, "wb") as f:
                f.write(response.content)
            return output_file
        else:
            raise Exception(f"Ошибка при отправке файла: {response.status_code}, {response.text}")

