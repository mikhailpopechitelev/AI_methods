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

def plot_mfcc_analysis(path_original, path_vrasmv, path_svrms):
    # Загружаем все 3 аудио файла
    y_original, sr = librosa.load(path_original, sr=None)
    y_vrasmv, _ = librosa.load(path_vrasmv, sr=None)
    y_svrms, _ = librosa.load(path_svrms, sr=None)

    plt.figure(figsize=(10, 3))
    
    # MFCC для оригинала
    mfccs_original = librosa.feature.mfcc(y=y_original, sr=sr, n_mfcc=13)
    plt.subplot(1, 3, 1)
    librosa.display.specshow(mfccs_original, sr=sr, x_axis='time')
    plt.title('MFCC - Оригинал')

    # MFCC для VRASMV
    mfccs_vrasmv = librosa.feature.mfcc(y=y_vrasmv, sr=sr, n_mfcc=13)
    plt.subplot(1, 3, 2)
    librosa.display.specshow(mfccs_vrasmv, sr=sr, x_axis='time')
    plt.title('MFCC - VRASMV')

    # MFCC для SVRMS
    mfccs_svrms = librosa.feature.mfcc(y=y_svrms, sr=sr, n_mfcc=13)
    plt.subplot(1, 3, 3)
    librosa.display.specshow(mfccs_svrms, sr=sr, x_axis='time')
    plt.title('MFCC - SVRMS')

    plt.tight_layout()
    plt.show()

def plot_signal_analysis(path_original, path_vrasmv, path_svrms):
    # Загружаем все 3 аудио файла
    y_original, _ = librosa.load(path_original, sr=None)
    y_vrasmv, _ = librosa.load(path_vrasmv, sr=None)
    y_svrms, _ = librosa.load(path_svrms, sr=None)

    plt.figure(figsize=(10, 3))

    # Сигналограмма для оригинала
    plt.subplot(1, 3, 1)
    plt.plot(y_original)
    plt.title('Сигналограмма - Оригинал')
    plt.xlabel("Время (сэмплы)")
    plt.ylabel("Амплитуда")

    # Сигналограмма для VRASMV
    plt.subplot(1, 3, 2)
    plt.plot(y_vrasmv)
    plt.title('Сигналограмма - VRASMV')
    plt.xlabel("Время (сэмплы)")
    plt.ylabel("Амплитуда")

    # Сигналограмма для SVRMS
    plt.subplot(1, 3, 3)
    plt.plot(y_svrms)
    plt.title('Сигналограмма - SVRMS')
    plt.xlabel("Время (сэмплы)")
    plt.ylabel("Амплитуда")

    plt.tight_layout()
    plt.show()

def plot_spectrogram_analysis(path_original, path_vrasmv, path_svrms):
    # Загружаем все 3 аудио файла
    y_original, sr = librosa.load(path_original, sr=None)
    y_vrasmv, _ = librosa.load(path_vrasmv, sr=None)
    y_svrms, _ = librosa.load(path_svrms, sr=None)

    plt.figure(figsize=(10, 3))

    # Спектрограмма для оригинала
    D_original = librosa.amplitude_to_db(np.abs(librosa.stft(y_original)), ref=np.max)
    plt.subplot(1, 3, 1)
    librosa.display.specshow(D_original, sr=sr, x_axis='time', y_axis='log')
    plt.colorbar(format='%+2.0f dB')
    plt.title('Спектрограмма - Оригинал')

    # Спектрограмма для VRASMV
    D_vrasmv = librosa.amplitude_to_db(np.abs(librosa.stft(y_vrasmv)), ref=np.max)
    plt.subplot(1, 3, 2)
    librosa.display.specshow(D_vrasmv, sr=sr, x_axis='time', y_axis='log')
    plt.colorbar(format='%+2.0f dB')
    plt.title('Спектрограмма - VRASMV')

    # Спектрограмма для SVRMS
    D_svrms = librosa.amplitude_to_db(np.abs(librosa.stft(y_svrms)), ref=np.max)
    plt.subplot(1, 3, 3)
    librosa.display.specshow(D_svrms, sr=sr, x_axis='time', y_axis='log')
    plt.colorbar(format='%+2.0f dB')
    plt.title('Спектрограмма - SVRMS')

    plt.tight_layout()
    plt.show()


def calculate_mfcc_correlation(path_original, path_vrasmv, path_svrms):
        # Загружаем все 3 аудиофайла
        y_original, sr_original = librosa.load(path_original, sr=None)
        y_vrasmv, _ = librosa.load(path_vrasmv, sr=None)
        y_svrms, _ = librosa.load(path_svrms, sr=None)

        # Извлекаем MFCC для каждого аудиофайла
        mfcc_original = librosa.feature.mfcc(y=y_original, sr=sr_original, n_mfcc=13)
        mfcc_vrasmv = librosa.feature.mfcc(y=y_vrasmv, sr=sr_original, n_mfcc=13)
        mfcc_svrms = librosa.feature.mfcc(y=y_svrms, sr=sr_original, n_mfcc=13)
        
        # Выравнивание длины массивов MFCC (обрезка до минимальной длины)
        min_len = min(mfcc_original.shape[1], mfcc_vrasmv.shape[1], mfcc_svrms.shape[1])

        mfcc_original = mfcc_original[:, :min_len]
        mfcc_vrasmv = mfcc_vrasmv[:, :min_len]
        mfcc_svrms = mfcc_svrms[:, :min_len]

        # Вычисляем корреляцию Пирсона между оригиналом и обработанными файлами
        correlation_vrasmv, _ = pearsonr(mfcc_original.flatten(), mfcc_vrasmv.flatten())
        correlation_svrms, _ = pearsonr(mfcc_original.flatten(), mfcc_svrms.flatten())

        # Возвращаем корреляции
        return correlation_vrasmv, correlation_svrms