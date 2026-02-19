from flask import Blueprint, jsonify, request
from sqlalchemy import select

from core.db import db
from models import Question


questions_bp = Blueprint(
    "questions",
    __name__,  # questions.py
    url_prefix="/questions"
)

# В декораторе route метод по умолчанию -- GET метод
# Если мы явно не указываем метод запроса для декоратора -- по умолчанию система будет ловить именно GET


# Read (list)
@questions_bp.route("")
def get_all_questions():
    # TODO-LIST:
    # 1. Сдкелть запрос на получения всех оъектов из базы
    stmt = select(Question)
    result = db.session.execute(stmt).scalars()

    # 2. Как-то преобразовать сложный объект ORM в простой словарик python
    response = [
        obj.to_dict()
        for obj in result
    ]

    # response = []
    #
    # for obj in result:
    #     response.append(obj.to_dict())


    # 3. вернуть данные как ответ в JSON формате с правильным status code
    return jsonify(response), 200  # 200 OK


# Read (one by ID)
@questions_bp.route("/<int:question_id>")
def get_question_by_id(question_id: int):
    return f"Retrieve one question by ID: {question_id}"


# Create
@questions_bp.route("/create", methods=["POST"])
def create_new_question():
    # https://example.com/questions?new=true => request.args -> {"new": True}
    # TODO-LIST для создания объекта
    ALLOWED_FIELDS = {"title", "description", "start_date", "end_date", "is_active"}
    # 1. Попытаться Получить сырые данные
    raw_data = request.get_json(silent=True)

    # 2. Провести проверки, что данные есть, они валидны, все требуемые колонки указаны
    if not raw_data:
        return jsonify(
            {
                "error": "Request body is missing or not valid JSON"
            }
        ), 400  # 400 BAD REQUEST

    # allowed -> {"title", "description", "start_date", "end_date", "is_active"}
    # raw -> {"title", "start_date", "end_date", "qwerty1"}
    unknown_fields = set(raw_data) - ALLOWED_FIELDS  # -> "qwerty1"

    if unknown_fields:
        return jsonify(
            {
                "error": f"Unknown fields for request: {', '.join(unknown_fields)}"
            }
        ), 400  # 400 BAD REQUEST


    # required -> {"title", "start_date", "end_date"}
    # raw -> {"title", "start_date"}
    required = {"title", "start_date", "end_date"}
    missing_fields = required - set(raw_data) # -> "end_date"

    if missing_fields:
        return jsonify(
            {
                "error": f"Missing required fields: {', '.join(missing_fields)}"
            }
        ), 400

    try:
        # 3. Попытаться создать новый объект
        new_question = Question(**raw_data)

        # 4. Добавить объект в сессию
        db.session.add(new_question)

        # 5. Применить изменения из сессии в Базу Данных
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify(
            {
                "error": "Failed to create new question",
                "detail": str(e)
            }
        ), 500  # 500 INTERNAL SERVER ERROR

    # 6. Вернуть ответ
    return jsonify(new_question.to_dict()), 201  # 201 CREATED


# Update
@questions_bp.route("/<int:question_id>/update", methods=["PUT", "PATCH"])
def update_question_by_id(question_id: int):
    return f"Update question by it's ID: {question_id}"


# Delete
@questions_bp.route("/<int:question_id>/delete", methods=["DELETE"])
def delete_question_by_id(question_id: int):
    return f"Delete question by it's ID: {question_id}"
