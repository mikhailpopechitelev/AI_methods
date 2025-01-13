import sys
import os
import requests
import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel
from sklearn.metrics.pairwise import cosine_similarity
from scipy.stats import pearsonr

from colculation.colculation import plot_mfcc_analysis, plot_signal_analysis, plot_spectrogram_analysis ,calculate_mfcc_correlation

from SVRMS_CONST import SVRMS_KEY, SVRMS_HOST
from VRASMV_CONST import VRASMV_KEY, VRASMV_HOST
from SVRMS_API import AudioProcessorAPI
from VRASMV_API import VocalRemoverAPI


class AudioAnalysisApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.filePath = None
        self.config_path_v = "vrasmv.json"
        self.config_path_s = "svrms.jso"
        # Инициализация API-клиентов с ключами и хостами
        self.api_vrasmv = VocalRemoverAPI(api_key=VRASMV_KEY, api_host=VRASMV_HOST)
        self.api_svrms = AudioProcessorAPI(api_key=SVRMS_KEY, api_host=SVRMS_HOST)
        with open("output_audio_vrasmv.mp3", "rb") as file_vrasmv:
            self.output_audio_vrasmv = file_vrasmv.read()
        with open("output_audio_svrms.mp3", "rb") as file_svrms:
            self.output_audio_svrms = file_svrms.read()

    def initUI(self):
        self.setWindowTitle("Audio Analysis Tool")
        self.setGeometry(100, 100, 600, 400)
        self.setStyleSheet("""
            QWidget { background-color: #2E2E2E; color: #E0E0E0; }
            QPushButton { background-color: #4CAF50; color: white; padding: 10px; margin: 5px; }
            QPushButton:hover { background-color: #45A049; }
        """)

        layout = QVBoxLayout()

        self.selectFileButton = QPushButton("Выбрать аудиофайл")
        self.selectFileButton.clicked.connect(self.openFileDialog)
        layout.addWidget(self.selectFileButton)

        self.processFilesButton = QPushButton("Обработать аудио")
        self.processFilesButton.clicked.connect(self.process_audio)
        layout.addWidget(self.processFilesButton)

        self.analysisButton = QPushButton("Показать графики анализа")
        self.analysisButton.clicked.connect(self.show_analysis)
        layout.addWidget(self.analysisButton)
        
        self.compareApiButton = QPushButton("Сравнить API")
        self.compareApiButton.clicked.connect(self.compare_api)
        layout.addWidget(self.compareApiButton)

        self.resultLabel = QLabel("Результат сравнения API будет здесь.")
        layout.addWidget(self.resultLabel)
    
        self.setLayout(layout)

    def openFileDialog(self):
        filePath, _ = QFileDialog.getOpenFileName(self, "Выберите аудиофайл", "", "Audio Files (*.mp3)")
        if filePath:
            self.filePath = filePath

    def process_audio(self):
        if self.filePath:
            try:
                # Обработка через первый API
                self.output_audio_vrasmv = self.api_vrasmv(self.filePath)
                # Обработка через второй API
                self.output_audio_svrms = self.api_svrms(self.filePath)
                print("Файлы обработаны и сохранены.")
            except Exception as e:
                print(f"Ошибка обработки: {e}")

    def show_analysis(self):
        if self.filePath and self.output_audio_vrasmv and self.output_audio_svrms:
            # Рисуем все графики по одному
            file_path_vrasmv = os.path.join(os.getcwd(), "output_audio_vrasmv.mp3")
            file_path_svrms = os.path.join(os.getcwd(), "output_audio_svrms.mp3")
            plot_mfcc_analysis(self.filePath, file_path_vrasmv, file_path_svrms)
            plot_signal_analysis(self.filePath, file_path_vrasmv, file_path_svrms)
            plot_spectrogram_analysis(self.filePath, file_path_vrasmv, file_path_svrms)
            
    def compare_api(self):
        if self.filePath and self.output_audio_vrasmv and self.output_audio_svrms:
            # Выполняем вычисление корреляции Пирсона
            correlation_vrasmv, correlation_svrms = calculate_mfcc_correlation(
                self.filePath, 
                "output_audio_vrasmv.mp3", 
                "output_audio_svrms.mp3"
            )

            # Выводим результаты сравнения
            if correlation_vrasmv > correlation_svrms:
                better_match = "VRASMV"
                better_correlation = correlation_vrasmv
                last_correlation = correlation_svrms
            else:
                better_match = "SVRMS"
                better_correlation = correlation_svrms
                last_correlation = correlation_vrasmv

            # Выводим информацию о том, какой API более похож на оригинал
            print(better_correlation)
            print(last_correlation)
            improvement = ((better_correlation - last_correlation) / last_correlation) * 100
            result_text = f"API {better_match} более похож на оригинал на {improvement}%"
            
            # Отображаем результат на UI
            self.resultLabel.setText(result_text)
            
    
    

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AudioAnalysisApp()
    window.show()
    sys.exit(app.exec_())
