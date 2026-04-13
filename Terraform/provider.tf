terraform {
  required_providers {
    yandex = {
      source  = "yandex-cloud/yandex"
      version = "0.187"
    }
  }
}

provider "yandex" {
  service_account_key_file = "key.json"
  cloud_id                 = "b1g8odmcmm95osagj70g"
  folder_id                = "b1g0kf7k1illsg896mh4"
  zone                     = "ru-central1-a"
}
