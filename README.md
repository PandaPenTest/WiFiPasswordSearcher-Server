# WiFiPasswordSearcher-Server
#### Содержание
1. **RS2SQLite.py** — конвертер отчётов CSV Router Scan в таблицу SQLite
2. **Server.py** — кэширующий сервер для 3WiFi Locator
## Установка
#### Зависимости:
- bottle
- requests
### Установка в Termux
1. Установить Termux: https://play.google.com/store/apps/details?id=com.termux
2. Выполнить команды:
```
pkg install python git
git clone https://github.com/drygdryg/WiFiPasswordSearcher-Server.git LocatorServer
cd LocatorServer/
pip install -r requirements.txt
python Server.py
```
#### Дополнительно: создание псевдонима команды
```
cd ~
echo alias lserver='"cd LocatorServer/ $$ python Server.py"' >> .bashrc
```
После перезапуска Termux:
```
lserver
```
### Настройка 3WiFi Locator
- Зайдите в настройки (иконка гаечного ключа в правом верхнем углу)
- Выберите "Locator Settings"
- Введите в поле "Server URL": http://IP:порт (по умолчанию: http://127.0.0.1:8080)
- Нажмите "Save"
## Использование
```
python Server.py [опции]
Опции:
-d [--database] имя_файла.db : файл базы данных SQLite (по умолчанию: APs.db)
-t [--table] имя_таблицы     : имя таблицы базы данных (по умолчанию:  aps)
-f [--offline]               : работать оффлайн: брать данные только из локальной БД, не обращаясь к 3WiFi
--host 127.0.0.1             : IP-адрес HTTP-сервера (по умолчанию: 127.0.0.1)
-p [--port] 8080             : порт HTTP-сервера (по умолчанию: 8080)
```
