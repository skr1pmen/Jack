# Jack

Телеграмм бот для рассылки расписания занятий студентам колледжа СРМК.

***❕ Не шаришь не лезь, оно тебя сожрёт ❕***

---

### Принцип работы:

Раз в какой-то временной промежуток бот заходит на сайт с расписанием, собирает данные, преобразует их в удобный формат.
После чего сохраняет расписание в базе данных, если новое расписание отличается от старого, происходит рассылка нового
расписания всем участникам бота.

---

### Технические характеристики:
* Python 3.10 и выше
* Pip 21.3.1 и выше
* SQLite3
* Дополнительные пакеты:
  * aiogram 2.22.1
  * aioschedule 0.5.2
  * beautifulsoup4 4.11.1
  * lxml 4.9.2
  * python-dotenv 0.21.0
  * requests 2.28.1

---

### Установка:

* Все необходимые пакеты можно установить через `requirements.txt`.

    pip install -r requirements.txt

* Для успешного подключения бота к API телеграмма и сайту колледжа необходимо создать файл `.env`.
Открыть его и прописать следующее:
    
      url=https://rmk.stavedu.ru:8010/moodle/eioswork/timetable/watchstudent.php?group=
      accept= # Здесь прописать свой Accept
      useragent= # Здесь прописать свой UserAgent
      token= # Здесь прописать свой токен телеграмм бота
      database= # Здесь прописать название своей базы данных
      admin= # Здесь прописать свой id телеграмма

* Создание базы данных. Всего в базе 3 таблицы `users`, `schedules` и `bot_settings`.
Код для создания таблиц:
  * **users:**

        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            chat_id INTEGER UNIQUE NOT NULL,
            first_name STRING NOT NULL,
            group INTEGER DEFAULT (0),
            prem BOOLEAN DEFAULT (False) 
        );
  * **schedules:**
  
         CREATE TABLE schedules (
             groups INTEGER,
             new_schedule STRING,
             old_schedule STRING
         );
  * **bot_settings:**
  
        CREATE TABLE bot_settings (
            mailing BOOLEAN DEFAULT (1) 
        );
