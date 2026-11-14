import flask
import connexion

from src.core.exception import arguments_exception
from src.dtos.report_type_enum import report_type_enum
from src.logic.entity_service import entity_service
from src.logic.report_factory import report_factory
from src.logic.report_format_service import report_format_service
from src.logic.settings_manager import settings_manager
from src.logic.storage_manager import storage_manager


settings_mgr = settings_manager()

if not settings_mgr.is_loaded:
    try:
        settings_mgr.load()
    except Exception:
        pass

storage_mgr = storage_manager(settings_mgr.settings)
factory = report_factory(settings_mgr.settings)
crud_service = entity_service(storage_mgr)
format_service = report_format_service()

api = connexion.FlaskApp(__name__, specification_dir="./")

try:
    api.app.json.ensure_ascii = False
except AttributeError:
    api.app.config["JSON_AS_ASCII"] = False


def _error(message: str, status: int):
    return flask.jsonify({"detail": message}), status


def _report_error(message: str, status: int):
    return flask.jsonify({"error": message}), status


def _get_json_body() -> dict:
    body = flask.request.get_json(silent=True)

    if not isinstance(body, dict):
        raise ValueError(
            "Тело запроса должно быть JSON-объектом"
        )

    return body


def _find_entity(entity_type: str, entity_id: str):
    return storage_mgr.find_by_id(entity_type, entity_id)


def index():
    default_fmt = (
        factory.settings.response_format.value
        if factory.settings and factory.settings.response_format
        else "TXT"
    )

    return flask.render_template(
        "index.html",
        recipes=storage_mgr.recipes,
        nomenclatures=storage_mgr.nomenclatures,
        ranges=storage_mgr.ranges,
        default_format=default_fmt,
    )


@api.route("/api/report-formats", methods=["GET"])
def get_report_formats():
    return flask.jsonify(format_service.get_formats()), 200


@api.route("/api/entities", methods=["GET"])
def list_entities():
    return flask.jsonify(
        {
            "groups": [
                {"id": group.id, "name": group.name}
                for group in storage_mgr.groups
            ],
            "storages": [
                {"id": storage.id, "name": storage.name}
                for storage in storage_mgr.storages
            ],
            "recipes": [
                {"id": recipe.id, "name": recipe.name}
                for recipe in storage_mgr.recipes
            ],
            "nomenclatures": [
                {"id": nomenclature.id, "name": nomenclature.name}
                for nomenclature in storage_mgr.nomenclatures
            ],
            "ranges": [
                {"id": range_item.id, "name": range_item.name}
                for range_item in storage_mgr.ranges
            ],
        }
    ), 200


@api.route(
    "/api/entities/<entity_type>/<entity_id>",
    methods=["PUT"],
)
def put_entity(entity_type: str, entity_id: str):
    try:
        body = _get_json_body()
        result = crud_service.create(entity_type, entity_id, body)
        return flask.jsonify(result), 201

    except FileExistsError as exception:
        return _error(str(exception), 409)

    except LookupError as exception:
        return _error(str(exception), 500)

    except (ValueError, arguments_exception) as exception:
        return _error(str(exception), 400)


@api.route(
    "/api/entities/<entity_type>/<entity_id>",
    methods=["GET"],
)
def get_entity(entity_type: str, entity_id: str):
    try:
        result = crud_service.get(entity_type, entity_id)
        return flask.jsonify(result), 200

    except LookupError as exception:
        return _error(str(exception), 404)

    except (ValueError, arguments_exception) as exception:
        return _error(str(exception), 400)


@api.route(
    "/api/entities/<entity_type>/<entity_id>",
    methods=["PATCH"],
)
def patch_entity(entity_type: str, entity_id: str):
    if storage_mgr.find_by_id(entity_type, entity_id) is None:
        return _error(
            f"Сущность '{entity_type}' с ID '{entity_id}' не найдена",
            404,
        )

    try:
        body = _get_json_body()
        result = crud_service.update(entity_type, entity_id, body)
        return flask.jsonify(result), 200

    except LookupError as exception:
        return _error(str(exception), 500)

    except (ValueError, arguments_exception) as exception:
        return _error(str(exception), 400)


@api.route(
    "/api/entities/<entity_type>/<entity_id>",
    methods=["DELETE"],
)
def delete_entity(entity_type: str, entity_id: str):
    try:
        result = crud_service.delete(entity_type, entity_id)
        return flask.jsonify(result), 200

    except LookupError as exception:
        return _error(str(exception), 404)

    except PermissionError as exception:
        return _error(str(exception), 409)

    except (ValueError, arguments_exception) as exception:
        return _error(str(exception), 400)


@api.route(
    "/api/report/<format_name>/<entity_type>/<entity_id>",
    methods=["GET"],
)
def get_report_by_format(
    format_name: str,
    entity_type: str,
    entity_id: str,
):
    entity = _find_entity(entity_type, entity_id)

    if entity is None:
        return _report_error(
            f"Сущность типа '{entity_type}' "
            f"с ID '{entity_id}' не найдена",
            404,
        )

    target_format = report_type_enum.from_string(format_name)
    report_instance = factory.create(target_format)
    result = report_instance.build(entity)

    return report_instance.to_http_response(
        result,
        filename=f"report_{entity_type}_{entity_id}",
    )


@api.route(
    "/api/report/default/<entity_type>/<entity_id>",
    methods=["GET"],
)
def get_report_default(entity_type: str, entity_id: str):
    entity = _find_entity(entity_type, entity_id)

    if entity is None:
        return _report_error(
            f"Сущность типа '{entity_type}' "
            f"с ID '{entity_id}' не найдена",
            404,
        )

    report_instance = factory.create_default()
    result = report_instance.build(entity)

    return report_instance.to_http_response(
        result,
        filename=f"report_default_{entity_type}_{entity_id}",
    )


@api.route("/api/get_report", methods=["GET"])
def get_report_query():
    format_name = flask.request.args.get("format", "").strip()
    entity_type = flask.request.args.get("type", "").strip()
    entity_id = flask.request.args.get("id", "").strip()

    if not entity_type or not entity_id:
        return _report_error(
            "Необходимо указать параметры 'type' и 'id'",
            400,
        )

    entity = _find_entity(entity_type, entity_id)

    if entity is None:
        return _report_error(
            f"Сущность типа '{entity_type}' "
            f"с ID '{entity_id}' не найдена",
            404,
        )

    if format_name:
        target_format = report_type_enum.from_string(format_name)
        report_instance = factory.create(target_format)
    else:
        report_instance = factory.create_default()

    result = report_instance.build(entity)

    return report_instance.to_http_response(
        result,
        filename=f"report_{entity_type}_{entity_id}",
    )


@api.route("/", methods=["GET"])
def index_route():
    return index()


api.add_api(
    "openapi.yaml",
    strict_validation=True,
)


if __name__ == "__main__":
    api.run(
        host="0.0.0.0",
        port=8080,
    )
