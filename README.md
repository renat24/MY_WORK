# EXAMPLES OF MY WORK


## 1. Posctscoring sevices
Отыскал пример как у нас был реализован бустинг. Сенситив информации нет, тем более компания закрылась.
Нам подготовили саму папку, и сказали воспользоваться двумя функциями()
-get_data_from_web_db()
-insert_to_web_db()
методы уже были реализованы, остальное сами.
Возможно, не самое удачное решение по коду (+ только onehot), сейчас бы сделал лучше и компактнее.

## 2. AUTOENCODERS_CVAE_GAN - реализация условных автоэнкодоров и ганов
Тут, скажем, не ООП, должен быть единый класс, отдельный метод или файл для трейна и для вспомогательных 
функций utils, + добавить возможность лепить разные архитектуры и много чего еще. Но по отдельности какие-то классы 
есть и код рабочий.
Реализация возможно отличается от статьи, так как я подбирал разные архитектуры для моделей, способы конкатенации 
condition'a и еще подбирал коэффициенты при лоссах, чтоб лучше сходилось.
В джупайтер ноутбуке даже сохранился лог и результаты.

## 3. UNET - простенькая реализация архитектуры юнет.
Тут в основном нуджно сомтреть на класс датасета RaccoonDatasetMasks, так как пришлось модифицировать "заводской" 
класс пайторч, потому что моя разметка была не по формату. 
В остальном, сама реализация - не очень, - там все захардкожено.
