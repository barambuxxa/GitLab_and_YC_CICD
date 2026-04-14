Тут будет документация по работе в GitLab. Дублирование проекта, который уже есть в GitLab.

У нас уже развёрнута VM с GitLab. Заходим на неё и создаём проект.

Для запуска CICD Pipeline, нам необходим runner. Мы будем использовать нашу VM для запуска pipeline. Ход настройки:
- Добавляем официальный репозиторий GitLab Runner
- curl -L "https://packages.gitlab.com/install/repositories/runner/gitlab-runner/script.deb.sh" | sudo bash

- Устанавливаем сам runner
- sudo apt-get install gitlab-runner

Готово, мы создали новый runner, теперь его надо связать с нашим GitLab-сервером. Для этого понадобятся URL вашего сервера и токен регистрации.
Где взять токен:
1.	заходим в наш проект на GitLab. CI/CD -> Runners -> Create instance Runner
2.	Скопируем токен

Возвращаемся на наш сервер и проводим регистрацию командой:

- gitlab-runner register --url http://ip-адрес_сервера_gitlab --token glrt-наш_токен

Вас спросят несколько параметров:
1.	URL нашего GitLab: http://<IP-вашего-сервера> (или домен)
2.	Токен: вставим скопированный токен
3.	Описание: например, "my-first-runner"
4.	Теги (tags): ВАЖНО! Чаще всего, необходимые определённые runnerы для сборки. С настроенным окружением.
5.	Executor: Выбираем самый простой, shell. 

При успешном завершении, мы увидим в gitLab подключенный runner, который готов собирать pipeline.

- У нас уже развёрнуты 2 Serverless Containers (dev и prod), 1 Container Registry. Между собой они привязаны. 
- Имеется Dockerfile из которого будет собираться Dockerimage
- requirements.txt c установленными зависимостями
- Lambda код (lambda_function.py)
- HTTP-обёртка нашего приложения (server.py)
- Pipeline для Gitlab CICD (.gitlab-ci.yml)

Нам нужно создать ещё 1 сервисный аккаунт, чтобы GitLab-runner мог подключаться к нашему Yandex Cloud и работать с ним.

Создаём сервисный аккаунт, который будем добавлять в GitLab, который будет иметь имя gitlab-ci-builder:
- yc iam service-account create --name gitlab-ci-builder

Далее присваиваем этому аккаунту роль, которая позволит ему пользоваться Container registry в нашей папке командой:

yc resource-manager folder add-access-binding b1g0kf7k1illsg896mh4 \
  --role container-registry.admin \
  --subject serviceAccount:ajeljscf1df8tmjn95tk

Далее создадим ключ JSON по которому мы будем авторизовываться из GitLab под сервисным аккаунтом.

Мы будем подключать gitlab runner к нашему CI/CD процессу. Но прописанные действия в stage будут запускаться от пользователя gitlab-runner. Так что, когда я захочу использовать какие то программы, мне надо дать на них разрешение. Я столкнулся с проблемой, что не могу узнать версию yc, так как yc можно запустить только от root.
Для этого мы создадим ссылку, чтобы пользователи могли запускать yc.

Создаем символическую ссылку
sudo ln -s /home/gitlab-runner/yandex-cloud/bin/yc /usr/local/bin/yc

Проверяем
sudo -u gitlab-runner yc version

После этого мы будем готовы подключиться к нашему yc.

Добавим переменные в наш GitLab (Settings -> CICD -> Variables -> Add variable

Имя переменной	Значение	Тип	Защищенная?
YC_OAUTH_TOKEN 	Полученный OAUTH TOKEN для подключения к облаку	Variable	Да
YC_FOLDER_ID	b1g0kf7k1illsg896mh4 (ID вашего каталога)	Variable	Да
YC_REGISTRY_ID	crpgl1k5ho1mqik5qn6m (ID вашего реестра)	Variable	Да
YC_CONTAINER_NAME_DEV	Имя DEV контейнера Variable	Нет
YC_CONTAINER_NAME_PROD	Имя PROD контейнера	Variable	Нет
YC_SERVICE_ACCOUNT_ID	ID сервисного аккаунта Variable	Да

Создадим вторую ветку в нашем проекте с названием dev и сделаем merge c main. Тут и самая суть. Если будет сделан коммит в ветку dev, тогда будет запущенен pipeline минуя stage_deploy_prd и мы увидим наш конейнер в среде dev.

Наш pipeline будет разбит на следующие шаги:
- stage_validate
- stage_build_push
- stage_deploy_dev
- stage_deploy_prd
- stage_finish

stage_validate
- Проверяем наше окружение для дальнейшей сборки, в нашем случаи это наш runner.

stage_build_push
- На этом этапе мы формируем наш docker контейнер и пулим его в наш Container Registry. Загружается 2 контейнера с тегом коммита, именно в каком коммите был собран контейнер. Второй контейнер делается с припиской brancha (main или dev).

job_deploy_dev
- Если делаем commit в ветку dev, то он запускается. Stage который связан с prod игнорируется через rules.

job_deploy_prd
- Если делаем commit в ветку main, то он запускается. Stage который связан с prod игнорируется через rules.

stage_finish
- Тут мы просто выводим, что CICD подошёл к концу.

Результату можно увидить в нашем публичном облаке на Yandex Cloud. В моём случаи это:
- PROD https://bba6790hqai31iic76n6.containers.yandexcloud.net/
- DEV https://bbabnrsdjpl0klmb67t6.containers.yandexcloud.net/
