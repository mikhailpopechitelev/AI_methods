import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QTextEdit, QLineEdit, QPushButton
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import html

class GPTChatApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GPT Chat")
        self.setGeometry(100, 100, 600, 800)

        # Инициализация модели GPT
        self.model_name_or_path = "sberbank-ai/rugpt3small_based_on_gpt2"
        self.tokenizer = GPT2Tokenizer.from_pretrained(self.model_name_or_path)
        self.model = GPT2LMHeadModel.from_pretrained(self.model_name_or_path).cuda()

        # Виджеты
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Поле чата
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.layout.addWidget(self.chat_display)

        # Поле ввода
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Введите сообщение...")
        self.layout.addWidget(self.input_field)

        # Кнопка отправки
        self.send_button = QPushButton("Отправить")
        self.layout.addWidget(self.send_button)

        # Привязка кнопки к обработчику
        self.send_button.clicked.connect(self.send_message)
        self.input_field.returnPressed.connect(self.send_message)

    def send_message(self):
        # Получение текста от пользователя
        user_message = self.input_field.text().strip()
        if not user_message:
            return

        # Отображение сообщения пользователя в чате
        self.chat_display.append(f"Вы: {user_message}")
        self.input_field.clear()

        # Генерация ответа от GPT
        response = self.generate_response(user_message)
        self.chat_display.append(f"GPT: {response}\n")

    def generate_response(self, text):
        # Генерация ответа с помощью модели GPT
        
        input_ids = self.tokenizer.encode(text, return_tensors="pt").cuda()
        out = self.model.generate(input_ids.cuda(), max_length=120, num_return_sequences=1, do_sample=True, top_k=10, top_p=0.98, repetition_penalty=2.5, temperature=0.6)
        generated_text = self.tokenizer.decode(out[0], skip_special_tokens=True)
        generated_text = html.unescape(generated_text)
        

        return generated_text[len(text):].strip()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GPTChatApp()
    window.show()
    sys.exit(app.exec_())
