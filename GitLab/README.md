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
