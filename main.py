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

try:
    api.app.json.ensure_ascii = False
except Exception:
    api.app.config["JSON_AS_ASCII"] = False


def _find_entity(entity_type: str, entity_id: str):
    """Делегирование поиска сущности в storage_manager (принцип единственной ответственности)."""
    return storage_mgr.find_by_id(entity_type, entity_id)


# Главная страница
@api.route("/", methods=["GET"])
def index():
    default_fmt = factory.settings.response_format.value if factory.settings and factory.settings.response_format else "TXT"
    return flask.render_template(
        "index.html",
        recipes=storage_mgr.recipes,
        nomenclatures=storage_mgr.nomenclatures,
        ranges=storage_mgr.ranges,
        default_format=default_fmt,
    )


# Метод GET формирует отчет в указанном формате и для указанного типа и кода сущности
@api.route("/api/report/<format_name>/<entity_type>/<entity_id>", methods=["GET"])
def get_report_by_format(format_name: str, entity_type: str, entity_id: str):
    entity = _find_entity(entity_type, entity_id)
    if entity is None:
        return flask.jsonify({"error": f"Сущность типа '{entity_type}' с id '{entity_id}' не найдена"}), 404

    target_format = report_type_enum.from_string(format_name)
    report_instance = factory.create(target_format)
    result = report_instance.build(entity)
    return report_instance.to_http_response(result, filename=f"report_{entity_type}_{entity_id}")


# Метод GET формирует отчет с использованием метода create_default
@api.route("/api/report/default/<entity_type>/<entity_id>", methods=["GET"])
def get_report_default(entity_type: str, entity_id: str):
    entity = _find_entity(entity_type, entity_id)
    if entity is None:
        return flask.jsonify({"error": f"Сущность типа '{entity_type}' с id '{entity_id}' не найдена"}), 404

    report_instance = factory.create_default()
    result = report_instance.build(entity)
    return report_instance.to_http_response(result, filename=f"report_default_{entity_type}_{entity_id}")


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

    result = report_instance.build(entity)
    return report_instance.to_http_response(result, filename=f"report_{entity_type}_{entity_id}")


@api.route("/api/entities", methods=["GET"])
def list_entities():
    return flask.jsonify({
        "recipes": [{"id": r.id, "name": r.name} for r in storage_mgr.recipes],
        "nomenclatures": [{"id": n.id, "name": n.name} for n in storage_mgr.nomenclatures],
        "ranges": [{"id": rg.id, "name": rg.name} for rg in storage_mgr.ranges],
    })


if __name__ == "__main__":
    api.run(host="0.0.0.0", port=8000)