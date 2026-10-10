# UML Диаграммы классов: SettingsManager, StorageManager и модели рецептов

## 1. Архитектура SettingsManager (Менеджер настроек)

Диаграмма показывает иерархию наследования от `abstract_manager`, реализацию шаблона **Singleton**, а также агрегацию модели настроек `settings_model` и реквизитов организации `organization_model`.

```mermaid
classDiagram
    direction TB

    class abstract_manager {
        <<abstract>>
        -str __file_name
        -bool __is_loaded
        -list __data
        +load(file_name: str) void
        +convert() bool
        +is_loaded() bool
    }

    class settings_manager {
        -str __default_file_name
        -settings_model __settings
        -dict __data
        -bool __is_loaded
        +instance$ settings_manager
        +__new__() settings_manager
        +load(file_name: str) void
        +convert() bool
        +settings() settings_model
        +is_loaded() bool
    }

    class settings_model {
        -organization_model __company
        -str __boss_name
        -str __account_name
        -bool __is_first_start
        +is_first_start() bool
        +company() organization_model
        +boss_name() str
        +account_name() str
    }

    class organization_model {
        -str _inn
        -str _bik
        -str _account
        -str _ownership_type
        +inn() str
        +bik() str
        +account() str
        +ownership_type() str
    }

    abstract_manager <|-- settings_manager : Наследование
    settings_manager o-- settings_model : Содержит (Singleton)
    settings_model o-- organization_model : Включает реквизиты
```

---

## 2. Архитектура StorageManager (Хранилище данных)

Диаграмма показывает структуру хранилища `storage_manager` (Singleton), наследование от `abstract_manager`, связь с `settings_model`, а также хранение коллекций уникальных доменных моделей (`range_model`, `nomenclature_group_model`, `storage_model`, `nomenclature_model`, `recipe_model`).

```mermaid
classDiagram
    direction TB

    class abstract_manager {
        <<abstract>>
        +load(file_name: str) void
        +convert() bool
        +is_loaded() bool
    }

    class storage_manager {
        -settings_model __settings
        -list __ranges
        -list __groups
        -list __storages
        -list __nomenclatures
        -list __recipes
        +instance$ storage_manager
        +__new__() storage_manager
        +settings() settings_model
        +ranges() list
        +groups() list
        +storages() list
        +nomenclatures() list
        +recipes() list
        +add_range(item) bool
        +add_group(item) bool
        +add_storage(item) bool
        +add_nomenclature(item) bool
        +add_recipe(item) bool
        +convert() bool
        +clear() void
    }

    class range_model {
        -float _conversion_factor
        -range_model _base_range
        +conversion_factor() float
        +base_range() range_model
        +create_kilogramm()$ range_model
        +create_gram()$ range_model
        +create_piece()$ range_model
    }

    class nomenclature_group_model {
        -str _name
        +create_raw()$ nomenclature_group_model
        +create_ingredients()$ nomenclature_group_model
        +create_semi_finished()$ nomenclature_group_model
        +create_products()$ nomenclature_group_model
        +create_packaging()$ nomenclature_group_model
    }

    class storage_model {
        -str _name
        +create_main()$ storage_model
        +create_cold()$ storage_model
    }

    class nomenclature_model {
        -str _full_name
        -nomenclature_group_model _group
        -range_model _range
        +full_name() str
        +group() nomenclature_group_model
        +range() range_model
        +create_flour(group, unit)$ nomenclature_model
        +create_sugar(group, unit)$ nomenclature_model
        +create_butter(group, unit)$ nomenclature_model
        +create_egg(group, unit)$ nomenclature_model
        +create_dough(group, unit)$ nomenclature_model
        +create_cookie(group, unit)$ nomenclature_model
        +create_packaging_box(group, unit)$ nomenclature_model
    }

    class recipe_model {
        -nomenclature_model __dish
        -list __rows
        +brutto() float
        +netto() float
    }

    abstract_manager <|-- storage_manager : Наследование
    storage_manager o-- range_model : Хранит единицы
    storage_manager o-- nomenclature_group_model : Хранит группы
    storage_manager o-- storage_model : Хранит склады
    storage_manager o-- nomenclature_model : Хранит номенклатуру
    storage_manager o-- recipe_model : Хранит рецепты
    nomenclature_model --> nomenclature_group_model : Группа
    nomenclature_model --> range_model : Единица
```

---

## 3. Архитектура технологических карт (Рецепты, полуфабрикаты и упаковка)

Диаграмма иллюстрирует структуру моделей `recipe_model` и `recipe_row_model`, вычисление веса Брутто и Нетто, а также **рекурсивную связь полуфабриката («блюдо в блюде»)** через свойство `sub_recipe`.

```mermaid
classDiagram
    direction TB

    class recipe_model {
        -str _name
        -nomenclature_model __dish
        -list __rows
        -int __cooking_time
        -list __instructions
        -int __portions
        +dish() nomenclature_model
        +rows() list
        +cooking_time() int
        +instructions() list
        +portions() int
        +brutto() float
        +netto() float
        +add_row(row: recipe_row_model) bool
        +remove_row(row_or_id) bool
        +create_dough_recipe(...)$ recipe_model
        +create_cookie_recipe(...)$ recipe_model
    }

    class recipe_row_model {
        -nomenclature_model __nomenclature
        -range_model __range
        -float __brutto
        -float __netto
        -recipe_model __sub_recipe
        +nomenclature() nomenclature_model
        +range() range_model
        +sub_recipe() recipe_model
        +brutto() float
        +netto() float
        +create_ingredient(...)$ recipe_row_model
        +create_semi_finished(...)$ recipe_row_model
    }

    class nomenclature_model {
        -str _name
        -str _full_name
        -nomenclature_group_model _group
        -range_model _range
    }

    class range_model {
        -str _name
        -float _conversion_factor
    }

    recipe_model *-- "*" recipe_row_model : Содержит строки
    recipe_model --> "1" nomenclature_model : Целевое блюдо (dish)
    recipe_row_model --> "1" nomenclature_model : Ингредиент (nomenclature)
    recipe_row_model --> "0..1" range_model : Единица измерения
    recipe_row_model o-- "0..1" recipe_model : Вложенный полуфабрикат (блюдо в блюде)
```