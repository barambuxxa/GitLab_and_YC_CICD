# Создаём наш Container Registry

resource "yandex_container_registry" "docker-container" {
  name      = "docker-container"
  folder_id = "b1g0kf7k1illsg896mh4"
  labels = {
    environment = "development"
    managed-by  = "terraform"
  }
}

# Сервисный аккаунт для контейнеров (если не создан ранее)
resource "yandex_iam_service_account" "container-sa" {
  name        = "container-execution-sa"
  description = "Service account for serverless containers execution"
  folder_id   = "b1g0kf7k1illsg896mh4"
}

# Назначение прав сервисному аккаунту
resource "yandex_resourcemanager_folder_iam_member" "container-registry-puller" {
  folder_id = "b1g0kf7k1illsg896mh4"
  role      = "container-registry.images.puller"
  member    = "serviceAccount:${yandex_iam_service_account.container-sa.id}"
}

# Назначение прав на вызов контейнера самому себе
resource "yandex_resourcemanager_folder_iam_member" "container-invoker" {
  folder_id = "b1g0kf7k1illsg896mh4"
  role      = "serverless-containers.containerInvoker"
  member    = "serviceAccount:${yandex_iam_service_account.container-sa.id}"
}

# Serverless Container для разработки
resource "yandex_serverless_container" "app-from-image-dev" {
  name               = "my-app-from-image-dev"
  description        = "Development container for testing"
  folder_id          = "b1g0kf7k1illsg896mh4"
  memory             = 256
  service_account_id = yandex_iam_service_account.container-sa.id
  execution_timeout  = "10s"

  image {
    # Используем ID реестра через ссылку на создаваемый ресурс
    url = "cr.yandex/${yandex_container_registry.docker-container.id}/my-app:http"
    environment = {
      ENVIRONMENT = "development"
      LOG_LEVEL   = "debug"
    }
  }

  concurrency = 1

  labels = {
    environment = "development"
    managed-by  = "terraform"
  }

  depends_on = [yandex_container_registry.docker-container]
}

# Serverless Container для продакшена
resource "yandex_serverless_container" "app-from-image-prod" {
  name               = "my-app-from-image-prod"
  description        = "Production container for live environment"
  folder_id          = "b1g0kf7k1illsg896mh4"
  memory             = 512
  service_account_id = yandex_iam_service_account.container-sa.id
  execution_timeout  = "30s"

  image {
    url = "cr.yandex/${yandex_container_registry.docker-container.id}/my-app:http"
    environment = {
      ENVIRONMENT = "production"
      LOG_LEVEL   = "info"
    }
  }

  concurrency = 5

  labels = {
    environment = "production"
    managed-by  = "terraform"
  }

  depends_on = [yandex_container_registry.docker-container]
}

# Выводы
output "registry_id" {
  value = yandex_container_registry.docker-container.id
}

output "registry_name" {
  value = yandex_container_registry.docker-container.name
}

output "dev_container_url" {
  value = "https://${yandex_serverless_container.app-from-image-dev.id}.serverless.yandexcloud.net"
}

output "prod_container_url" {
  value = "https://${yandex_serverless_container.app-from-image-prod.id}.serverless.yandexcloud.net"
}
