# README для разработчиков

### 1. Чекеры и hostname
Чекеры в hostname должны уметь принимать как просто hostname без порта (например "127.0.0.1"), так и с указанием порта (например "10.118.0.20:2102").
Если порт не указан - использовать дефолтный для сервиса.

### 2. Docker-compose

* Использовать `version` не более 3.7
* под каждый сервис даётся по целой виртуалке, так что можно не ограничивать ресурсы особо

### 3. Доступ к чексистем и виртуалкам команд в процессе тестирования

* В папочке `/teams` этого репозитория лежат все пароли и явки
* `/teams/for_dev.ssh_key` - ключ доступа ко всем виртуалкам. Пользователь - `ctfcup` (на командах) либо `ubuntu` (на серверах)
* `sudo openvpn ./teams/for_devs.ovpn` - подключится через OpenVPN к сети игры как разработчик (будет сетевой доступ до всего).
* `10.118.0.10` - чексистема
* пароль от неё подсмотреть можно в `./ansible/cs`, поле `cs_admin_auth`.
* текущий пользователь/пароль: `root:YswhZ2vWH7aJZl3r`
* сеть описана в `./teams/TEAM_README`, там можно подсмотреть ip виртуалок