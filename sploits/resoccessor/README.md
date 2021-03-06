## resoccessor
resoccessor (RESOurce aCCESSOR) -- сервис для разграничения доступа между
пользователями и ресурсами. Сервис предоставляет возможность регистрироваться, выдавать токены на
ресурсы, загружать сами ресурсы и распределять доступы между пользователями к ресурсам.
Для фиксации доступа к одному ресурсу используется схема.

### Формат схемы
Схема содержит в себе несколько сущностей: пользователь, группа, правило, триггер, условие
и действие.  Пользователи имеют идентификаторы, начиная с 1. Аналогично, каждая группа имеет идентификатор,
только начиная с 0. В схеме фиксируется распределение пользователей по группам и цепочка правил,
по которой определяется возможность доступа.

* Цепочка правил -- это список правил;
* Правило -- это тройка из идентификатора группы, условия и действия;
  * Условие -- это предикат, означающий, принадлежит ли пользователь к идентификатору группы из этого же правила;
  * Действие может быть ALLOW или DENY -- соответственно разрешить или запретить доступ.

Проверка доступа для данного пользователя с помощью схемы происходит следующий образом: для каждого 
правила если, выполняется ли предикат условия, проверка завершается с заданным действием.

Сам формат схемы -- это подмножество формата json: полностью отсутствуют пробелы,
а первая группа всегда пустая. В словаре в `groups` хранится список-отображение идентификатора пользователя
в список групп, в которых он состоит. В `rules` хранится список троек-чисел, где первое число -- это
идентификатор группы, второе -- это условие принадлежит (1) / не принадлежит (0), третье -- это
действие ALLOW (1) / DENY (0).

(для удобства пробельные символы есть в примере)

```json
{
  "groups": [[], [1, 2, 3], [1, 2]],
  "rules":[[1, 1, 1]]
}
```

### Уязвимость
#### Атака
Парсинг схемы происходит с использованием [буфера фиксированного размера](https://github.com/HackerDom/ctfcup-2021-AD/blob/main/services/resoccessor/src/schema/bin/schema.cpp#L195),
который выделяется в памяти на стеке. Он используется для хранения временных
значений списков правил и групп. Значит, всё что окажется в одном из списков, который описывает
группы пользователя будет записываться на стек без проверки размера списка. Каждый идентификатор
группы в списке интерпретируется как unsigned int -- можно положить на стек любые данные,
размер которых кратен размеру unsigned int. Исполняемый файл для парсинга был скомпилирован с
флагами: `g++ -std=c++2a -fPIC -z execstack -fno-stack-protector schema.cpp -o schema`
(стек исполняемый, стековой канарейки нет), а ASLR на игровых машинах был отключён. Поэтому можно перезатереть адрес возврата на стек,
положив до этого туда шеллкод.

После получения шеллкода можно рекурсивно скопировать все флаги в директорию, откуда раздаётся статика
для фронтенда (например, в`/static/css/flags`), и флаги станут публично доступны.

####Защита
Переписать парсинг схемы без переполнения буфера.
