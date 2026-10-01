# UML Диаграммы классов: SettingsManager и StorageManager

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

Диаграмма показывает структуру хранилища `storage_manager` (Singleton), наследование от `abstract_manager`, связь с `settings_model`, а также хранение коллекций уникальных доменных моделей (`range_model`, `nomenclature_group_model`, `storage_model`, `nomenclature_model`).

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
        +instance$ storage_manager
        +__new__() storage_manager
        +settings() settings_model
        +ranges() list
        +groups() list
        +storages() list
        +nomenclatures() list
        +add_range(item) bool
        +add_group(item) bool
        +add_storage(item) bool
        +add_nomenclature(item) bool
        +convert() bool
        +clear() void
    }

    class range_model {
        -float _conversion_factor
        -range_model _base_range
        +conversion_factor() float
        +base_range() range_model
    }

    class nomenclature_group_model {
        -str _name
    }

    class storage_model {
        -str _name
    }

    class nomenclature_model {
        -str _full_name
        -nomenclature_group_model _group
        -range_model _range
        +full_name() str
        +group() nomenclature_group_model
        +range() range_model
    }

    abstract_manager <|-- storage_manager : Наследование
    storage_manager o-- range_model : Хранит уникальные единицы
    storage_manager o-- nomenclature_group_model : Хранит уникальные группы
    storage_manager o-- storage_model : Хранит уникальные склады
    storage_manager o-- nomenclature_model : Хранит уникальную номенклатуру
    nomenclature_model --> nomenclature_group_model : Ссылается на группу
    nomenclature_model --> range_model : Ссылается на единицу
```