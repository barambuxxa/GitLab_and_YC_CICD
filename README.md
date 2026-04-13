# GitLab_and_YC_CICD

Задача сделать олноценный pipeline, с помощью GitLab CICD.

Необходимо создать:
- Каталог Yandex Cloud с нашим проектом.
- Yandex Cloud - Container Registry. Тут будут храниться собранные контейнеры с приложением.
- Yandex Cloud - Serverless Containers. Здесь будут разворачиваться контейнеры для среды dev и prod.
- Docker Image и Docker контейнер с нашим приложением. Http сервер, который возвразает состояние.
- Развернуть GitLab сервер на VM.
- В созданном проекте на GitLab создать 2 ветки, dev и prod.
- Написать CICD pipeline по следующим пунктам:
    - Stage 1: Проверка окружения для дальнейшей сборки docker контейнера.
    - Stage 2: Сборка докер контейнера и его push в Yandex cloud - Container Registry. Контейнер будет иметь тег ветки и номер commita.
    - Stage 3: Разворачиваем Serverless Containers из нужного docker контейнера, под нужную среду.
    - Stage 4: Уведомление об успешной сборки.
 
Ход работы по развёртке инстансов в Yandex cloud можно увидеть в каталоге Terraform

Развёртка GitLab сервера и написание pipeline можно увидеть в каталоге Gitlab
