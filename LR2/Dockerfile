# Используем официальный Python образ как базовый
FROM python:3.8-buster

# Добавляем репозиторий для старых версий clang/llvm
RUN echo "deb http://apt.llvm.org/buster/ llvm-toolchain-buster-9 main" | tee /etc/apt/sources.list.d/llvm.list && \
    wget -qO - https://apt.llvm.org/llvm-snapshot.gpg.key | apt-key add - && \
    apt-get update && apt-get install -y \
    clang-9 \
    llvm-9 \
    llvm-9-dev \
    llvm-9-tools \
    git \
    build-essential \
    python3-dev \
    libomp-dev \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

# Устанавливаем переменную окружения LD_LIBRARY_PATH
ENV LD_LIBRARY_PATH=/usr/lib/

# Клонируем репозиторий apex и устанавливаем его
# Клонируем репозиторий apex
RUN git clone https://github.com/qywu/apex

RUN pip install torch==1.12.0

# Переходим в директорию репозитория
WORKDIR apex

# Устанавливаем apex с флагами компиляции
RUN pip install -v --no-cache-dir --global-option="--cpp_ext" --global-option="--cuda_ext" ./

# Возвращаемся в корневую директорию
WORKDIR /


# Устанавливаем Triton
RUN pip install triton

# Устанавливаем Deepspeed с необходимыми флагами
RUN DS_BUILD_CPU_ADAM=1 DS_BUILD_SPARSE_ATTN=1 pip install deepspeed

# Устанавливаем необходимые библиотеки
RUN pip install transformers \
    huggingface_hub \
    timm==0.3.2

# Клонируем репозиторий с ru-gpts
RUN git clone https://github.com/sberbank-ai/ru-gpts

# Копируем необходимые файлы в нужные директории
RUN cp ru-gpts/src_utils/trainer_pt_utils.py /usr/local/lib/python3.8/dist-packages/transformers/trainer_pt_utils.py && \
    cp ru-gpts/src_utils/_amp_state.py /usr/local/lib/python3.8/dist-packages/apex/amp/_amp_state.py

# Устанавливаем рабочую директорию
WORKDIR /app

# Запуск контейнера (по умолчанию, можно добавить другие команды для запуска приложения)
CMD ["python"]
