## Первая уязвимость

В [классе](https://github.com/HackerDom/ctfcup-2021-AD/blob/main/services/ATM-machine/src/main/java/com/cryptojava/elephantass/keygen/DateBasedKeyGen.java) для генерации "случайного" ключа для шифрования используется случайная дата из определенного промежутка. Но из этой даты берется только год, а он всегда один и тот же. Поэтому, либо посмотрев результат выполнения метода, либо использовав целиком этот метод, есть возможность просто брать из сервиса шифротексты и расшифровывать их.


## Вторая уязвимость

Вторая уязвимость так же связана с шифрованием. Для шифрования [используется]https://github.com/HackerDom/ctfcup-2021-AD/blob/main/services/ATM-machine/src/main/java/ru/ctf/crypto/CryptoServiceImpl.java) алгоритм AES/CBC с PKCS5Padding. Данный вид шифрования при неправильной обработке ошибок подвержен атаке [PaddingOracle](https://habr.com/ru/post/247527/).
Метод [getCheckBytes](https://github.com/HackerDom/ctfcup-2021-AD/blob/main/services/ATM-machine/src/main/java/ru/ctf/tcp/MessageHandler.java) пытается расшифровать входные байты и в случае неудачи отправляет ошибку. По этой ошибке можно определить, когда паддинг некорректный, а когда все ОК. 
[Реализация атаки](paddingoracle.py).
[Сплойт](sploit.py) 
