data "yandex_resourcemanager_folder" "ctf" {
  name = "ctf"
}

data "yandex_compute_image" "ubuntu-with-docker" {
  family = "ubuntu-with-docker"
  folder_id = data.yandex_resourcemanager_folder.ctf.id
}

output "ubuntu-with-docker" {
  value = data.yandex_compute_image.ubuntu-with-docker
}

