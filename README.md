Название проекта:
«Распознавание и воспроизведение нот»

Описание проекта:

Проект представляет собой веб-приложение, которое позволяет пользователям загружать изображения нотных листов, распознавать ноты и конвертировать их в аудиофайлы. Приложение включает в себя функции регистрации и авторизации пользователей, а также предоставляет личный кабинет для управления загруженными файлами и сгенерированными аудиодорожками.

Инструкция по запуску

Скачайте репозиторий на свой компьютер:

git clone https://github.com/OxXity/preproff_audio_project.git

Установите все необходимые зависимости:

pip install -r requirements.txt

Запустите веб-приложение:

python app.py

Откройте веб-браузер и перейдите по адресу:

http://localhost:5000

Наилучшим форматом загрузки является формат файла .png с качеством изображения на менее 300 dpi. Для этого изображение с нотным листом можно скачать с сайта MuseScore, блягодаря стандарту качества изображений на сайте и при необходимости конвертировать изображение из формата .svg в .png при помощи специальных конвертеров. Для этого можно использовать, например, конвертер "SVG to PNG" по ссылке: https://svgtopng.com/

Проект написан на языке Python и использует следующие библиотеки:

Music21 - для работы с нотными данными;

wave - для обработки аудиофайлов;

subprocess - для выполнения системных команд;

Flask - для создания веб-интерфейса;

SQLAlchemy - для работы с базой данных;

zipfile - для работы с архивами;

os - для взаимодействия с операционной системой.

Команда разработчиков:

Руководитель проекта:

Ремизова Елена Георгиевна

Выполнили:

Дмитрий Гаров, garov.d@sch2009.net

Игорь Стрижаков, strizhakov.i@sch2009.net

Вячеслав Антонцев, antontsev.v@sch2009.net

Артемий Гусев, gusev.a@sch2009.net
