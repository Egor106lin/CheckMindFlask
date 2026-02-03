from typing import Dict, List, Any, Tuple
from schemas import TestCreateInputSchema, ProcessedQuestionSchema

class TestDataProcessor:
    
    def process_input_data(input_data: Dict[str, Any]) -> Tuple[TestCreateInputSchema, List[ProcessedQuestionSchema], int]:
        validated_input = TestCreateInputSchema(**input_data)
        
        processed_questions = []
        max_score = 0
        
        for i, question_input in enumerate(validated_input.questionsAndOptions):
            options_texts = [opt.title for opt in question_input.options]
            correct_indices = [idx for idx, opt in enumerate(question_input.options) if opt.correct]
            points = len(correct_indices)
            
            processed_question = ProcessedQuestionSchema(
                text=question_input.question,
                options=options_texts,
                correct_options=correct_indices,
                points=points
            )
            
            processed_questions.append(processed_question)
            max_score += points
        
        return validated_input, processed_questions, max_score
    
    def prepare_for_db(
        validated_input: TestCreateInputSchema,
        processed_questions: List[ProcessedQuestionSchema],
        max_score: int
    ) -> Dict[str, Any]:
        questions_for_db = []
        for q in processed_questions:
            questions_for_db.append({
                "text": q.text,
                "options": q.options,
                "points": q.points
            })
        
        answers_for_db = []
        for q in processed_questions:
            answers_for_db.append({
                "correct_options": q.correct_options,
                "points": q.points
            })
        
        return {
            "title": validated_input.testName,
            "description": validated_input.testDescription,
            "group_ids": str(validated_input.groupID),
            "questions": questions_for_db,
            "answers": answers_for_db,
            "users_max_score": max_score,
            "users_attempts": 0,
            "is_visible": True
        }
    
    def validate_answer_format(answer_data: Dict[str, Any]) -> bool:
        if not isinstance(answer_data, dict):
            return False
        
        for key, value in answer_data.items():
            if not key.isdigit():
                return False
            if not isinstance(value, list):
                return False
            if not all(isinstance(item, int) for item in value):
                return False
        
        return True
