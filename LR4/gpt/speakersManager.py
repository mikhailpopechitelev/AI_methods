from typing import Dict
from gpt.speaker import Speaker
import os
import json

# Класс менеджера сессий
class SpeakerManager:
    def __init__(self, gptToken , cache_file: str = "sessions.json") -> None:
        self.sessions: Dict[int, Speaker] = {}
        self.gptToken = gptToken
        self.cache_file = cache_file
        
        self.load_sessions()

    def get_or_create_speaker(self, user_id) -> Speaker:
        if user_id not in self.sessions:
            self.sessions[user_id] = Speaker(user_id , self.gptToken)
            self.save_sessions()
        return self.sessions[user_id]

    def get_speaker(self, user_id) -> Speaker:
        if user_id not in self.sessions:
            raise ValueError(f"Speaker for user {user_id} not found")
        return self.sessions[user_id]

    def remove_speaker(self, user_id) -> None:
        if user_id in self.sessions:
            del self.sessions[user_id]
            self.save_sessions()

    def load_sessions(self) -> None:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, "r", encoding="utf-8") as file:
                    data = json.load(file)
                    for user_id, speaker_data in data.items():
                        self.sessions[int(user_id)] = Speaker(user_id, self.gptToken)
                        
    
    def save_sessions(self) -> None:
        data = {}
        for user_id, speaker in self.sessions.items():
            data[user_id] = {"thread_id": speaker.config["configurable"]["thread_id"]}

        with open(self.cache_file, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)