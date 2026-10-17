import flask
import connexion
from src.logic.settings_manager import settings_manager
from src.logic.storage_manager import storage_manager
from src.logic.report_factory import report_factory
from src.dtos.report_type_enum import report_type_enum


# Инициализация менеджеров и фабрики
settings_mgr = settings_manager()
if not settings_mgr.is_loaded:
    try:
        settings_mgr.load()
    except Exception:
        pass

storage_mgr = storage_manager(settings_mgr.settings)
factory = report_factory(settings_mgr.settings)

api = connexion.FlaskApp(__name__, specification_dir="./")

# Отключаем экранирование Unicode, чтобы в JSON русский текст отображался нормально
try:
    api.app.json.ensure_ascii = False
except Exception:
    api.app.config["JSON_AS_ASCII"] = False


def _find_entity(entity_type: str, entity_id: str):
    """Поиск сущности в storage_manager по типу и коду (ID)."""
    t = str(entity_type).strip().lower()
    eid = str(entity_id).strip()

    if t in ("recipe", "recipes", "рецепт", "рецепты"):
        for item in storage_mgr.recipes:
            if item.unique_code == eid or item.id == eid:
                return item
    elif t in ("nomenclature", "nomenclatures", "номенклатура"):
        for item in storage_mgr.nomenclatures:
            if item.unique_code == eid or item.id == eid:
                return item
    elif t in ("range", "ranges", "единица", "единицы", "единица_измерения"):
        for item in storage_mgr.ranges:
            if item.unique_code == eid or item.id == eid:
                return item
    return None


def _create_report_response(report_instance, report_type: report_type_enum, entity, entity_type: str, entity_id: str):
    """Формирование HTTP ответа: бинарный файл для CSV/Markdown, текст для остальных."""
    report_result = report_instance.build(entity)

    # Пункт 7 ТЗ: Для Markdown, CSV - формировать бинарные данные и выполнить скачивание файла
    if report_type == report_type_enum.CSV:
        return flask.Response(
            bytes(report_result.binary),
            mimetype="text/csv; charset=utf-8",
            headers={"Content-Disposition": f"attachment; filename=report_{entity_type}_{entity_id}.csv"},
        )
    elif report_type == report_type_enum.MARKDOWN:
        return flask.Response(
            bytes(report_result.binary),
            mimetype="text/markdown; charset=utf-8",
            headers={"Content-Disposition": f"attachment; filename=report_{entity_type}_{entity_id}.md"},
        )
    elif report_type == report_type_enum.XML:
        return flask.Response(report_result.text, mimetype="application/xml; charset=utf-8")
    elif report_type == report_type_enum.HTML:
        return flask.Response(report_result.text, mimetype="text/html; charset=utf-8")
    else:
        return flask.Response(report_result.text, mimetype="text/plain; charset=utf-8")


# Главная страница со списком прямых кликабельных ссылок на все отчеты для скриншотов
@api.route("/", methods=["GET"])
def index():
    default_fmt = factory.settings.response_format.name if factory.settings else "TXT"

    def render_links(etype, eid):
        return (
            f'<a class="btn" href="/api/report/html/{etype}/{eid}" target="_blank">HTML</a> '
            f'<a class="btn btn-info" href="/api/report/xml/{etype}/{eid}" target="_blank">XML</a> '
            f'<a class="btn btn-secondary" href="/api/report/txt/{etype}/{eid}" target="_blank">TXT</a> '
            f'<a class="btn btn-success" href="/api/report/csv/{etype}/{eid}">Скачать CSV</a> '
            f'<a class="btn btn-success" href="/api/report/markdown/{etype}/{eid}">Скачать MD</a> '
            f'<a class="btn btn-warning" href="/api/report/default/{etype}/{eid}">По умолчанию ({default_fmt})</a>'
        )

    recipe_rows = "".join(
        f'<tr><td><b>{r.name}</b></td><td><span class="badge">{r.unique_code}</span></td><td>{render_links("recipe", r.unique_code)}</td></tr>'
        for r in storage_mgr.recipes
    )
    nom_rows = "".join(
        f'<tr><td><b>{n.name}</b></td><td><span class="badge">{n.unique_code}</span></td><td>{render_links("nomenclature", n.unique_code)}</td></tr>'
        for n in storage_mgr.nomenclatures
    )
    range_rows = "".join(
        f'<tr><td><b>{rg.name}</b></td><td><span class="badge">{rg.unique_code}</span></td><td>{render_links("range", rg.unique_code)}</td></tr>'
        for rg in storage_mgr.ranges
    )

    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Система отчетов - Паттерны проектирования</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 30px; background: #f8f9fa; }}
        h1, h2 {{ color: #212529; }}
        .card {{ background: white; padding: 20px; margin-bottom: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .btn {{ display: inline-block; padding: 6px 12px; margin: 3px; font-size: 13px; text-decoration: none; border-radius: 4px; color: white; background: #0d6efd; }}
        .btn-success {{ background: #198754; }}
        .btn-warning {{ background: #ffc107; color: black; }}
        .btn-info {{ background: #0dcaf0; color: black; }}
        .btn-secondary {{ background: #6c757d; }}
        .badge {{ background: #e9ecef; padding: 3px 6px; border-radius: 3px; font-family: monospace; font-size: 12px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
        th, td {{ padding: 10px; border-bottom: 1px solid #dee2e6; text-align: left; }}
    </style>
</head>
<body>
    <h1>Панель управления отчетами (Задание № 5)</h1>
    <p>Формат ответа по умолчанию из настроек: <b>{default_fmt}</b></p>

    <div class="card">
        <h2>Рецепты (Технологические карты)</h2>
        <table>
            <thead><tr><th>Наименование</th><th>ID</th><th>Доступные отчеты</th></tr></thead>
            <tbody>
                {recipe_rows}
            </tbody>
        </table>
    </div>

    <div class="card">
        <h2>Номенклатура</h2>
        <table>
            <thead><tr><th>Наименование</th><th>ID</th><th>Доступные отчеты</th></tr></thead>
            <tbody>
                {nom_rows}
            </tbody>
        </table>
    </div>

    <div class="card">
        <h2>Единицы измерения</h2>
        <table>
            <thead><tr><th>Наименование</th><th>ID</th><th>Доступные отчеты</th></tr></thead>
            <tbody>
                {range_rows}
            </tbody>
        </table>
    </div>
</body>
</html>"""


# Метод GET формирует отчет в указанном формате и для указанного типа и кода сущности
@api.route("/api/report/<format_name>/<entity_type>/<entity_id>", methods=["GET"])
def get_report_by_format(format_name: str, entity_type: str, entity_id: str):
    entity = _find_entity(entity_type, entity_id)
    if entity is None:
        return flask.jsonify({"error": f"Сущность типа '{entity_type}' с id '{entity_id}' не найдена"}), 404

    target_format = report_type_enum.from_string(format_name)
    report_instance = factory.create(target_format)
    return _create_report_response(report_instance, target_format, entity, entity_type, entity_id)


# Метод GET формирует отчет с использованием метода create_default
@api.route("/api/report/default/<entity_type>/<entity_id>", methods=["GET"])
def get_report_default(entity_type: str, entity_id: str):
    entity = _find_entity(entity_type, entity_id)
    if entity is None:
        return flask.jsonify({"error": f"Сущность типа '{entity_type}' с id '{entity_id}' не найдена"}), 404

    report_instance = factory.create_default()
    default_format = factory.settings.response_format if factory.settings else report_type_enum.TXT
    return _create_report_response(report_instance, default_format, entity, entity_type, entity_id)


@api.route("/api/get_report", methods=["GET"])
def get_report_query():
    format_name = flask.request.args.get("format", "").strip()
    entity_type = flask.request.args.get("type", "").strip()
    entity_id = flask.request.args.get("id", "").strip()

    if not entity_type or not entity_id:
        return flask.jsonify({"error": "Необходимо указать параметры 'type' и 'id'"}), 400

    entity = _find_entity(entity_type, entity_id)
    if entity is None:
        return flask.jsonify({"error": f"Сущность типа '{entity_type}' с id '{entity_id}' не найдена"}), 404

    if format_name:
        target_format = report_type_enum.from_string(format_name)
        report_instance = factory.create(target_format)
    else:
        report_instance = factory.create_default()
        target_format = factory.settings.response_format if factory.settings else report_type_enum.TXT

    return _create_report_response(report_instance, target_format, entity, entity_type, entity_id)


@api.route("/api/entities", methods=["GET"])
def list_entities():
    return flask.jsonify({
        "recipes": [{"id": r.unique_code, "name": r.name} for r in storage_mgr.recipes],
        "nomenclatures": [{"id": n.unique_code, "name": n.name} for n in storage_mgr.nomenclatures],
        "ranges": [{"id": rg.unique_code, "name": rg.name} for rg in storage_mgr.ranges],
    })


if __name__ == "__main__":
    api.run(host="0.0.0.0", port=8000)