# LLM API

Апи для взаимодействия с ии агентами

## Подготовка

### Install Pytorch

#### Linux + Cuda 12.6

```bash
pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cu126
```

#### Linux + Cuda 12.8

```bash
pip3 install torch torchvision
```

#### Linux + Cuda 13

```bash
pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cu130
```

#### Linux + CPU

```bash
pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

### Install other requirements

```bash
pip3 install -r requirements.txt
```

### Install models

#### Install `git xet`

```bash
curl --proto '=https' --tlsv1.2 -sSf https://raw.githubusercontent.com/huggingface/xet-core/refs/heads/main/git_xet/install.sh | sh
```

##### Check installation

```bash
git xet --version
```

#### Clone model repository

Это может занять некоторое время

##### Выбор модели

Я рекомендую взять `Qwen3-1.7B`, но если прямо не тянет компьютер, то `Qwen3-0.6B`.

###### Qwen3-0.6B: весит 1.5GB

```bash
export MODEL_REPOSITORY="https://huggingface.co/Qwen/Qwen3-0.6B"
```

###### Qwen3-1.7B: весит 4GB

```bash
export MODEL_REPOSITORY="https://huggingface.co/Qwen/Qwen3-1.7B"
```

###### Qwen3-4B: весит 8GB:

```bash
export MODEL_REPOSITORY="git clone https://huggingface.co/Qwen/Qwen3-4B"
```

###### YandexGPT-5-Lite-8B-pretrain: весит 30GB:

```bash
export MODEL_REPOSITORY="git clone https://huggingface.co/yandex/YandexGPT-5-Lite-8B-pretrain"
```

##### Загрузка модели

```bash
mkdir models/ ; cd models/
git clone $MODEL_REPOSITORY
cd ../
```

### Задать нужные переменные окружения

Пример `.env` файла:

```Properties
MODEL_PATH=./models/Qwen3-0.6B/
CHECK_CUDA=true
```

## Запуск сервиса

```bash
python -m uvicorn main:app --reload --port 8001
```

##