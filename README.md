# Подготовка среды

Настроим docker-compose файл, в котором в качестве сервисов будет: postgres и server. Настроим постоянное хранение, сетевое окружение и healthckecks. Для server настроим Dockerfile с необходимой версией питона (облегченной) и необходимыми библиотеками. В app.py находится логика приложения: при помощи Flask будет подниматься сервер, из postgres будем получать ФИО, формировать HTML страницу для возврата.

Сделаем сборку server  
   ![изображение](https://github.com/Murken-0/docker-vulnerabilities/assets/71382530/afd0e2d6-4036-46d3-a882-cfc2e132f39b)
   
С помощью команды docker-compose up -d развернем сервисы. В браузере по адресу localhost:5001 увидим результат
   ![изображение](https://github.com/Murken-0/docker-vulnerabilities/assets/71382530/2d07d648-0d35-474c-9c70-4fbc617e37c5)
   
# Trivy

Установим trivy.

![изображение](https://github.com/Murken-0/docker-vulnerabilities/assets/71382530/98dc1669-b475-44de-823b-af8c0b7579a0)

Запустим сканирование. В начале произойдет загрузка БД с уязвимостями. Далее появятся найденные уязвимости.

![изображение](https://github.com/Murken-0/docker-vulnerabilities/assets/71382530/58d6c87b-a8c9-4282-a4e1-2c5cc0b95458)

Результат сканирования:

**server:latest (alpine 3.18.6)**
  
В библиотеке libexpat (свободная потокоориентированная библиотека парсинга XML) будет найдено две уязвимости:

1. CVE-2023-52425 - Неконтроллируемое потребление ресурсов - Продукт не контролирует должным образом распределение и обслуживание ограниченного ресурса, тем самым позволяя субъекту влиять на количество потребляемых ресурсов, что в конечном итоге приводит к исчерпанию доступных ресурсов.
Решение: уязвимость существует до версии 2.5.0, необходимо использовать библиотеку, начиная с версии 2.6.0 (написать Dockerfile, где прописать обновление)

2. CVE-2023-52426 - Неправильное ограничение рекурсивных ссылок на сущности в DTD (XML Entity Expansion) - Продукт использует XML-документы и позволяет определять их структуру с помощью определения типа документа (DTD), но не контролирует должным образом количество рекурсивных определений сущностей.
Решение: уязвимость существует до версии 2.5.0, необходимо использовать библиотеку, начиная с версии 2.6.0 (написать Dockerfile, где прописать обновление)

**Python (python-pkg)**
  
В библиотеке pip (METADATA) найдена одна уязвимость:

1. CVE-2023-5752 -Неправильная нейтрализация специальных элементов, используемых в команде (внедрение в команду) - Продукт полностью или частично создает команду, используя входные данные вышестоящего компонента, но не нейтрализует или неправильно нейтрализует специальные элементы, которые могут изменить предполагаемую команду при ее отправке нижестоящему компоненту.
Решение: уязвимость существует до версии 23.3, необходимо использовать библиотеку, начиная с версии 23.3. (написать Dockerfile, где прописать обновление)

# bench-security

В отдельную папку склонируем репозиторий утилиты bench-security

![изображение](https://github.com/Murken-0/docker-vulnerabilities/assets/71382530/aba5138a-3154-4253-bdcc-3d00e82e8cdf)

Запустим ее.

Получим счет:

![изображение](https://github.com/Murken-0/docker-vulnerabilities/assets/71382530/8cc40d7c-8fd9-4463-8a4a-e1e6dc4acf35)

В результате работы программы видим следующие предупреждения:


**1.1.1 - Ensure a separate partition for containers has been created (Automated) - Убедитесь, что создан отдельный раздел для контейнеров (автоматизирован)**

![изображение](https://github.com/Murken-0/docker-vulnerabilities/assets/71382530/fdb90d71-5788-4639-b4df-cf14db250819)

Всегда рекомендуется использовать другой, кроме раздела docker по умолчанию. Большинство облачных платформ, таких как AWS или DigitalOcean, по умолчанию никогда не предоставляют максимальное свободное место под разделом /var.       Так что в этом случае вы можете столкнуться с нехваткой дискового пространства. 
Как найти раздел по умолчанию для контейнеров Docker? -> docker info -f'{{.DockerRootDir }}'

**1.1.3 - Ensure auditing is configured for the Docker daemon (Automated) - Убедитесь, что аудит настроен для демона Docker (автоматизирован)**

![изображение](https://github.com/Murken-0/docker-vulnerabilities/assets/71382530/d1fdbe81-42e1-4cc2-a1e0-4cfa4df0add1)

Аудит на linux-сервере может заключаться в настройке демона auditd. Этот демон отвечает за запись записи аудита в файл журнала аудита. Чтобы настроить аудит для файлов Docker, выполните:


**1.1.4 - Ensure auditing is configured for Docker files and directories -/run/containerd (Automated) - Убедитесь, что аудит настроен для файлов и каталогов Docker -/run/containerd (автоматический)
**
![image](https://github.com/egorvozhzhov/docker-test/assets/71019753/ba844651-decd-414e-888f-1aaeb08c16de)

![изображение](https://github.com/Murken-0/docker-vulnerabilities/assets/71382530/7800a044-9da6-4688-a1ed-a9fb3ab7217a)

Docker рекомендует использовать аудит на системном уровне для ключевых каталогов Docker. Аудит регистрирует все операции, влияющие на отслеживаемые файлы и каталоги. Это позволяет отслеживать потенциально деструктивные изменения. Убедитесь, что у вас установлен auditd. Отредактируйте файл /etc/audit/audit.rules и добавьте следующие строки в нижнюю часть файла:

![image](https://github.com/egorvozhzhov/docker-test/assets/71019753/f9826506-1701-4899-987a-f927fcd8d700)

Инструкция -p wa означает, что auditd будет регистрировать записи и изменения атрибутов, которые влияют на файлы. Если выходные данные Docker Bench предлагают использовать аудит для дополнительных каталогов, добавьте их в список. Каталоги Docker могут меняться со временем.
Чтобы изменения вступили в силу, необходимо перезапустить auditd:
sudo systemctl restart auditd

**2.2 - Ensure network traffic is restricted between containers on the default bridge (Scored) - Убедитесь, что сетевой трафик ограничен между контейнерами на мосту по умолчанию (оценено)**

![изображение](https://github.com/Murken-0/docker-vulnerabilities/assets/71382530/678595bd-a8cb-44d6-abe5-75d24dd85983)

файл конфигурации /etc/docker/daemon.json:
"icc":false — отключает обмен данными между контейнерами, чтобы избежать ненужной утечки информации.

**2.9 - Enable user namespace support (Scored) - Включить поддержку пользовательского пространства имен (оценено)**

![изображение](https://github.com/Murken-0/docker-vulnerabilities/assets/71382530/f1cb4b3b-fc79-4b0d-8922-3f2a2bece604)

User namespaces - это механизм в ядре Linux, который позволяет изолировать процессы, принадлежащие разным пользователям, даже если они используют одинаковые идентификаторы пользователя внутри и снаружи контейнера. Это обеспечивает дополнительный уровень безопасности и изоляции.
1. Убедиться, что поддержка user namespaces включена в ядре Linux на хосте. Для этого можно выполнить команду:
bash grep CONFIG_USER_NS /boot/config-uname -r
Если вывод содержит =y или =CONFIG_USER_NS=y, то поддержка включена.
2. Добавить --userns-remap в файл конфигурации Docker daemon.
Открыть файл конфигурации Docker daemon для редактирования (обычно располагается в /etc/docker/daemon.json) и добавить туда следующий параметр:
{
  "userns-remap": "default"
}
После внесения изменений нужно перезапустить сервис Docker:
sudo systemctl restart docker
3. После этого Docker будет использовать пользовательское пространство имен для изоляции контейнеров. Можно проверить текущую конфигурацию Docker с помощью команды:
docker info | grep userns

**2.12 - Ensure that authorization for Docker client commands is enabled (Scored) - Убедитесь, что авторизация для клиентских команд Docker включена (оценена)**

![изображение](https://github.com/Murken-0/docker-vulnerabilities/assets/71382530/6361f391-bb9d-4014-a9d5-0644931ed389)

 ~/.docker/config.json
  ![image](https://github.com/egorvozhzhov/docker-test/assets/71019753/b1889651-e37f-4268-9f12-037fc801dec0)

**2.13 - Ensure centralized and remote logging is configured (Scored) - Убедитесь, что настроено централизованное и удаленное ведение журнала (оценено)**

![изображение](https://github.com/Murken-0/docker-vulnerabilities/assets/71382530/6e4ce673-d163-433f-9e58-75eb5db4fb0e)

ELK Stack (Elasticsearch, Logstash, Kibana)

**2.14 - Ensure containers are restricted from acquiring new privileges (Scored) - Убедитесь, что контейнерам запрещено получать новые привилегии (оценено)**

![изображение](https://github.com/Murken-0/docker-vulnerabilities/assets/71382530/a1c18c38-474d-44d8-8d20-6c27183a2f52)

docker run --no-new-privileges my_image

**2.15 - Ensure live restore is enabled (Scored) - Убедитесь, что включено оперативное восстановление (оценено)**

![изображение](https://github.com/Murken-0/docker-vulnerabilities/assets/71382530/e86c8dd2-af82-4127-924a-839e28c001e2)

/etc/docker/daemon.json
{
  "live-restore": true
}

**2.16 - Ensure Userland Proxy is Disabled (Scored) - Убедитесь, что пользовательский прокси отключен (оценено)**

![изображение](https://github.com/Murken-0/docker-vulnerabilities/assets/71382530/670a7d24-ac0c-4839-8779-6d4eb9e411ff)

{
 "userland-proxy": false
}

**4.5 - Ensure Content trust for Docker is Enabled (Automated) - Убедитесь, что доверие к контенту для Docker включено (автоматически)**

Включение Content Trust для Docker — это отличная практика для обеспечения безопасности контейнеров. Content Trust используется для проверки подлинности и целостности образов Docker перед их загрузкой и запуском.
export DOCKER_CONTENT_TRUST=1
docker trust key generate <ИМЯ>
docker trust sign <ИМЯ_ОБРАЗА>:<ТЕГ>

**5.2 - Ensure that, if applicable, an AppArmor Profile is enabled (Automated) - Убедитесь, что, если применимо, профиль AppArmor включен (автоматически)**

**5.3 - Ensure that, if applicable, SELinux security options are set (Automated) - Убедитесь, что, если применимо, установлены параметры безопасности SELinux (автоматически)**

**5.8 - Ensure privileged ports are not mapped within containers (Automated) - Убедитесь, что привилегированные порты не отображаются внутри контейнеров (автоматически)**

**5.9 - Ensure that only needed ports are open on the container (Manual) - Убедитесь, что в контейнере открыты только необходимые порты (вручную)**

**5.11 - Ensure that the memory usage for containers is limited (Automated) - Убедитесь, что использование памяти для контейнеров ограничено (автоматизировано)**

**5.12 - Ensure that CPU priority is set appropriately on containers (Automated) - Убедитесь, что приоритет ЦП установлен правильно в контейнерах (автоматически)**

**5.13 - Ensure that the container's root filesystem is mounted as read only (Automated) - Убедитесь, что корневая файловая система контейнера смонтирована только для чтения (автоматически)**

**5.14 - Ensure that incoming container traffic is bound to a specific host interface (Automated) - Убедитесь, что входящий контейнерный трафик привязан к определенному интерфейсу хоста (автоматически)**

# docker-scout
Проверим уязвимости с помощью docker-scout. Для этого выберем образ и выполним анализ
В результате будут обнаружены те же самые уязвимости, что выявила утилита trivy

![изображение](https://github.com/Murken-0/docker-vulnerabilities/assets/71382530/377d99fa-6266-4c6b-b21e-f885d8f8d67a)
