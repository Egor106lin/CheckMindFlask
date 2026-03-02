from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import List, Optional, Dict
from collections import OrderedDict

class OptionSchema(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    correct: bool = Field(...)

class QuestionInputSchema(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    options: List[OptionSchema] = Field(..., min_length=2, max_length=10)
    singleCorrect: bool = Field(False, description="Если true, должен быть ровно один правильный ответ")

    @field_validator('options', mode='after')
    @classmethod
    def validate_and_deduplicate_options(cls, v, info):
        seen = OrderedDict()
        for idx, opt in enumerate(v):
            norm = opt.title.strip().lower()
            if norm in seen:
                if opt.correct:
                    seen[norm] = (seen[norm][0], True)
            else:
                seen[norm] = (idx, opt.correct)
        new_options = []
        for norm, (first_idx, correct_flag) in seen.items():
            original_opt = v[first_idx]
            new_options.append(
                OptionSchema(
                    title=original_opt.title,
                    correct=correct_flag
                )
            )
        if len(new_options) < 2:
            raise ValueError("После удаления дубликатов осталось менее 2 вариантов ответа")
        single_correct = info.data.get('singleCorrect', False)
        correct_options = [opt for opt in new_options if opt.correct]
        if single_correct:
            if len(correct_options) != 1:
                raise ValueError("При включённой опции «гарантировать один верный ответ» должен быть ровно один правильный вариант")
        else:
            if len(correct_options) == 0:
                raise ValueError("Вопрос должен иметь хотя бы один правильный вариант ответа")

        return new_options

class TestCreateInputSchema(BaseModel):
    groupID: str = Field(...)
    questionsQuantity: int = Field(..., ge=1, le=100)
    testName: str = Field(..., min_length=1, max_length=200)
    testDescription: Optional[str] = Field(None, max_length=1000)
    questionsAndOptions: List[QuestionInputSchema] = Field(..., min_length=1, max_length=100)

    @field_validator('questionsAndOptions')
    @classmethod
    def validate_questions_count(cls, v, info):
        if 'questionsQuantity' in info.data and len(v) != info.data['questionsQuantity']:
            raise ValueError(f"Количество вопросов ({len(v)}) не совпадает с указанным ({info.data['questionsQuantity']})")
        return v

    @field_validator('groupID')
    @classmethod
    def validate_group_id(cls, v):
        if not v.isdigit():
            raise ValueError("groupID должен быть числом")
        return int(v)

class ProcessedQuestionSchema(BaseModel):
    text: str
    options: List[str]
    correct_options: List[int]
    points: int = 1
    single_correct: bool = False
    model_config = ConfigDict(from_attributes=True)

class TestResponseSchema(BaseModel):
    id: int
    title: str
    description: Optional[str]
    group_ids: str
    is_visible: bool
    users_max_score: int
    users_attempts: int
    question_count: int
    model_config = ConfigDict(from_attributes=True)

class TestStatisticsSchema(BaseModel):
    total_questions: int
    total_points: int
    questions_with_multiple_correct: int
    average_options_per_question: float
    correct_options_per_question: Dict[int, int]
    
    @field_validator('correct_options_per_question', mode='before')
    @classmethod
    def process_correct_options(cls, v):
        if isinstance(v, dict):
            return v
        return {f"questions_with_{k}_correct": v for k, v in v.items()}