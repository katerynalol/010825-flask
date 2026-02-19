from datetime import datetime

from pydantic import (
    BaseModel,
    Field,
    model_validator,
    ConfigDict
)


class BaseSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        str_strip_whitespace=True,
        extra="forbid"
    )


class QuestionBase(BaseSchema):
    title: str = Field(..., min_length=15, max_length=150)
    description: str | None = Field(default=None, min_length=20, max_length=750)
    start_date: datetime
    end_date: datetime


    @model_validator(mode="after")
    def validate_dates(self):
        if self.start_date > self.end_date:
            raise ValueError("start date must be before end date")

        return self


class QuestionCreateRequest(QuestionBase):
    ...


class QuestionUpdateRequest(BaseSchema):
    title: str | None = Field(default=None, min_length=15, max_length=150)
    description: str | None = Field(default=None, min_length=20, max_length=750)
    start_date: datetime | None
    end_date: datetime | None
    is_active: bool | None


    @model_validator(mode="after")
    def validate_dates(self):
        if self.start_date is not None and self.end_date is not None:
            if self.start_date > self.end_date:
                raise ValueError("Start date must be before end date")

        return self


# Как мы хотим получать один конкретный объект Question
class QuestionRetrieve(QuestionBase):
    id: int
    is_active: bool


# Как мы хотим получать список всех Question
class QuestionList(BaseSchema):
    id: int
    title: str
    start_date: datetime
    is_active: bool


class QuestionCreateResponse(QuestionRetrieve):
    ...
