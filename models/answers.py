from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base


class Answer(Base):
    __tablename__ = 'answers'

    question_id: Mapped[int] = mapped_column(Integer, ForeignKey('questions.id'), nullable=False)
    option_id: Mapped[int] = mapped_column(Integer, ForeignKey('question_options.id'), nullable=False)

    question: Mapped["Question"] = relationship(back_populates="answers")
    option: Mapped["QuestionOption"] = relationship(back_populates="answers")