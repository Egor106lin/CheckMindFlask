from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import List, Optional, Dict

class OptionSchema(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    correct: bool = Field(...)

class QuestionInputSchema(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    options: List[OptionSchema] = Field(..., min_length=2, max_length=10)
    
    @field_validator('options')
    @classmethod
    def validate_correct_options(cls, v):
        correct_options = [opt for opt in v if opt.correct]
        if len(correct_options) == 0:
            raise ValueError("Вопрос должен иметь хотя бы один правильный вариант ответа")
        return v

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
