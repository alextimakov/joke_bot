# joke_bot
Определятор профессии

## Структура
### models
Сериализированные модели в формате .pkl + засинхроненные с jupytext модели .py

### data
Пустая папка, в которую не нужно выкладывать никакие приватные данные

### app
Telegram бот в качестве пользовательского интерфейса

### converter.py
Конвертер из экспорта чатов Telegram и превращения их в .csv

### setup.py
Перечисление зависимостей и нужных пакетов для работы с pip-tools

### .gitignore
Чтобы не вылить приватные данные

### README.md \ LICENSE
Без них никуда


## Для работы над проектом:

1. Склонируйте проект в нужную папку: 

```bash
git clone https://github.com/alextimakov/joke_bot.git
```


2. Создайте в папке виртуальное окружение:

```bash
cd ./joke_bot
python -m venv venv -- для windows
python3 -m venv venv -- для ubuntu
```

3. Активируйте окружение и установите в нём pip-tools:

```bash
.\venv\Scripts\activate -- для windows
source venv/bin/activate -- для ubuntu
pip install pip-tools
```

4. Установите в окружение необходимые зависимости:

```bash
pip-sync
```
