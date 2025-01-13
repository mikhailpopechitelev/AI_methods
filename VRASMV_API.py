
import requests
import os
from VRASMV_CONST import *

class VocalRemoverAPI:
    _instance = None  

    def __new__(cls, api_key, api_host):
        if cls._instance is None:
            cls._instance = super(VocalRemoverAPI, cls).__new__(cls)
            cls.api_key = api_key
            cls.api_host = api_host
            cls.api_url = VRASMV_URL
        return cls._instance

    def __call__(self, file_path):
        headers = {
            "x-rapidapi-key": self.api_key,
            "x-rapidapi-host": self.api_host,
        }

        # Отправляем аудиофайл на сервер
        with open(file_path, "rb") as file:
            files = {"file": file}
            response = requests.post(self.api_url, files=files, headers=headers)

        # Проверяем статус ответа и сохраняем результат
        if response.status_code == 200:
            output_file = os.path.join(os.path.dirname(file_path), "output_audio_vrasmv.mp3")
            with open(output_file, "wb") as output_file:
                output_file.write(response.content)
            return output_file 
        else:
            raise Exception(f"Ошибка при обработке файла: {response.status_code}, {response.text}")
