# nmap-collector

Сервис для хранения отчетов [Nmap](https://nmap.org/) с использованием [Sanic](https://sanic.readthedocs.io/en/stable/).

## Содержание

- [nmap-collector](#nmap-collector)
  - [Содержание](#содержание)
    - [1. Запуск сервиса](#1-запуск-сервиса)
    - [2. Используемые инструменты](#2-используемые-инструменты)
    - [3. Реализованное API](#3-реализованное-api)
      - [3.1 `POST ​/scan`](#31-post-scan)

### 1. Запуск сервиса

Для запуска сервиса необходим установленный [Docker](https://docs.docker.com/engine/install/) и [Docker-compose](https://docs.docker.com/compose/install/).

Команда запуска сервиса:

```bash
docker-compose up
```

Команда запуска сервиса в фоновом режиме:

```bash
docker-compose up -d
```

После запуска работу сервиса можно проверить, открыв в браузере <http://127.0.0.1:8000/swagger/#/Nmap/post_scan>.

### 2. Используемые инструменты

Сервис работает с использованием [Sanic](https://sanic.readthedocs.io/en/stable/).

Данные отчетов [Nmap](https://nmap.org/) хранятся в [MongoDB](https://www.mongodb.com/).

Возможность тестового взаимодействия с API реализованно через [Swagger](https://swagger.io/) с помощью [Sanic OpenAPI 2](https://sanic-openapi.readthedocs.io/en/stable/sanic_openapi2/index.html).

### 3. Реализованное API

#### 3.1 `POST ​/scan`

Метод проивзодит сканирование указанного в теле запроса `host`, выдает ответ в виде JSON с полями `data` и `objectIds`.
Если `save_xml` было истинно, то отчет будет сохранен в файл `XML`.

Информация о теле запроса:
| Название поля | Тип данных | Обязательное поле? | Описание                                  |
| ------------- | :--------: | :----------------: | ----------------------------------------- |
| `host`        |  `string`  |       **+**        | `Hostname` для сканирования               |
| `save_xml`    |   `bool`   |       **+**        | Необходимо ли сохранить отчет в XML файл? |

Пример тела запроса:

```json
{
  "host": "1.1.1.1",
  "save_xml": true
}
```

Информация о теле ответа:
| Название поля | Тип данных | Описание                                                     |
| ------------- | :--------: | ------------------------------------------------------------ |
| `data`        |   `list`   | Информация о сканируемом `Hostname`                          |
| `objectIds`   |   `list`   | Список `objectId`, полученные при добавлении информации в БД |

Пример тела ответа:

```json
{
  "data": [
    {
      "ip": "1.1.1.1",
      "time_scan": 1651494082,
      "hostnames": [
        {
          "name": "one.one.one.one",
          "type": "PTR"
        }
      ],
      "ports": {
        "53": {
          "state": "open",
          "protocol": "tcp",
          "service": "domain",
          "version": null
        },
        "80": {
          "state": "open",
          "protocol": "tcp",
          "service": "http",
          "version": null
        },
        "443": {
          "state": "open",
          "protocol": "tcp",
          "service": "http",
          "version": null
        },
        "853": {
          "state": "open",
          "protocol": "tcp",
          "service": "domain",
          "version": null
        }
      },
      "os_info": {},
      "_id": "626fccc2cf30fc6742d519a8"
    }
  ],
  "objectIds": [
    "626fccc2cf30fc6742d519a8"
  ]
}
```
