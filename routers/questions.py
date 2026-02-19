from flask import Blueprint, jsonify, request
from sqlalchemy import select
from pydantic import ValidationError

from core.db import db
from models import Question
from schemas.questions import (
    QuestionList,
    QuestionRetrieve,
    QuestionCreateRequest,
    QuestionCreateResponse,
    QuestionUpdateRequest
)


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
        QuestionList.model_validate(obj).model_dump()
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
    # 1. Получить один объект
    stmt = select(Question).where(Question.id == question_id)
    question = db.session.execute(stmt).scalars().one_or_none()

    # 2. Проверить, что объект есть в БД
    if not question:
        return jsonify({"error": f"Question with ID {question_id} not found"}), 404  # 404 NOT FOUND


    # 3. Преобразовать в простой словарь и вернуть ответ
    return jsonify(QuestionRetrieve.model_validate(question).model_dump()), 200


# Create
@questions_bp.route("/create", methods=["POST"])
def create_new_question():
    # https://example.com/questions?new=true => request.args -> {"new": True}
    # TODO-LIST для создания объекта
    # 1. Попытаться Получить сырые данные
    raw_data = request.get_json(silent=True)

    # 2. Провести проверки, что данные есть, они валидны, все требуемые колонки указаны
    if not raw_data:
        return jsonify(
            {
                "error": "Request body is missing or not valid JSON"
            }
        ), 400  # 400 BAD REQUEST

    try:
        validated_data = QuestionCreateRequest.model_validate(raw_data)
    except ValidationError as e:
        return jsonify(
            {
                "error": e.errors()
            }
        ), 400

    try:
        # 3. Попытаться создать новый объект
        new_question = Question(**validated_data.model_dump())

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
    return jsonify(QuestionCreateResponse.model_validate(new_question).model_dump()), 201  # 201 CREATED


# Update
@questions_bp.route("/<int:question_id>/update", methods=["PUT", "PATCH"])
def update_question_by_id(question_id: int):
    # 1. Попытаться Получить сырые данные
    raw_data = request.get_json(silent=True)

    # 2. Провести проверки, что данные есть, они валидны, все требуемые колонки указаны
    if not raw_data:
        return jsonify(
            {
                "error": "Request body is missing or not valid JSON"
            }
        ), 400  # 400 BAD REQUEST

    try:
        validated_data = QuestionUpdateRequest.model_validate(raw_data)
    except ValidationError as e:
        return jsonify(
            {
                "error": e.errors()
            }
        ), 400

    stmt = select(Question).where(Question.id == question_id)
    question = db.session.execute(stmt).scalars().one_or_none()

    if not question:
        return jsonify({"error": f"Question with ID {question_id} not found"}), 404

    try:
        for key, value in validated_data.model_dump().items():
            setattr(question, key, value)

        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": f"Failed to update question with ID {question_id}",
            "detail": str(e)
        }), 500  # 500 INTERNAL SERVER ERROR

    return jsonify(QuestionRetrieve.model_validate(question).model_dump()), 200


# Delete
@questions_bp.route("/<int:question_id>/delete", methods=["DELETE"])
def delete_question_by_id(question_id: int):
    stmt = select(Question).where(Question.id == question_id)
    question = db.session.execute(stmt).scalars().one_or_none()

    if not question:
        return jsonify({"error": f"Question with ID {question_id} not found"}), 404

    try:
        db.session.delete(question)
        db.session.commit()
    except Exception as e:
        db.session.rollback()

        return jsonify({
            "error": f"Failed to delete Question with ID {question_id}",
            "detail": str(e)
        }), 500

    return jsonify({"message": f"Question with ID {question_id} deleted successfully"}), 204  # 204 NO CONTENT
