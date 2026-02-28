from models import UserModel, UserGroupModel, TestModel
from schemas import TestCreateInputSchema

from service.db_init import db
from service.test_data_processor import TestDataProcessor

import json
from datetime import datetime
class User():
    def __init__(self, user_id=None):
        self.id = None
        self.name = None
        self.groups_admin_of = []
        self.groups_user_of = []
        self.email = None
        self.avatar_url = None
        self.provider = None
        self.access_token = None
        self.refresh_token = None
        self.token_expiry = None
        if user_id:
            self.create_with_id(user_id)
    
    def create_with_id(self, user_id):
        user_data = UserModel.query.get(user_id)
        if user_data:
            self.id = user_data.id
            self.name = user_data.name
            self.groups_admin_of = user_data.groups_admin_of
            self.groups_user_of = user_data.groups_user_of
            self.email = user_data.email
            self.avatar_url = user_data.avatar_url
            self.provider = user_data.provider
            self.access_token = user_data.access_token
            self.refresh_token = user_data.refresh_token
            self.token_expiry = user_data.token_expiry
            return True
        else:
            return False
    
    def create_with_token(self, access_token):
        if not access_token:
            return False
        
        user_data = UserModel.query.filter_by(access_token=access_token).first()
        
        if user_data:
            self.id = user_data.id
            self.name = user_data.name
            self.groups_admin_of = user_data.groups_admin_of
            self.groups_user_of = user_data.groups_user_of
            self.email = user_data.email
            self.avatar_url = user_data.avatar_url
            self.provider = user_data.provider
            self.access_token = user_data.access_token
            self.refresh_token = user_data.refresh_token
            self.token_expiry = user_data.token_expiry
            return True
        else:
            return False

    def update_user_in_db(self):
        user_to_update = UserModel.query.get(self.id)
        user_to_update.id=self.id
        user_to_update.name=self.name
        user_to_update.email=self.email
        user_to_update.avatar_url=self.avatar_url
        user_to_update.provider=self.provider
        user_to_update.groups_admin_of=self.groups_admin_of
        user_to_update.groups_user_of=self.groups_user_of
        user_to_update.access_token=self.access_token
        user_to_update.refresh_token=self.refresh_token
        user_to_update.token_expiry=self.token_expiry
        db.session.commit()

    def delete_from_db(self):
        try:
            user_to_delete = UserModel.query.get(self.id)
            db.session.delete(user_to_delete)
            db.session.commit()
            return True
        except:
            db.session.rollback()
            return False

    def add_group_admin_of(self, group_id):
        if group_id not in self.groups_admin_of:
            self.groups_admin_of.append(group_id)
            self.update_user_in_db()

    def add_group_user_of(self, group_id):
        if group_id not in self.groups_user_of:
            self.groups_user_of.append(group_id)
            self.update_user_in_db()
            return True
        else:
            return False

    def delete_group_admin_of(self, group_id):
        if group_id in self.groups_admin_of:
            self.groups_admin_of.remove(group_id)
            self.update_user_in_db()

    def delete_group_user_of(self, group_id):
        if group_id in self.groups_user_of:
            self.groups_user_of.remove(group_id)
            self.update_user_in_db()

    def delete_group_from_lists(self, group_id):
        if group_id in self.groups_admin_of:
            self.delete_group_admin_of(group_id)
            return True
        elif group_id in self.groups_user_of:
            self.delete_group_user_of(group_id)
            return True
        else:
            return False
        
    def change_group_user_admin(self, group_id):
        if group_id in self.groups_admin_of:
            self.groups_admin_of.remove(group_id)
            self.groups_user_of.append(group_id)
            self.update_user_in_db()
            return True
        elif group_id in self.groups_user_of:
            self.groups_user_of.remove(group_id)
            self.groups_admin_of.append(group_id)
            self.update_user_in_db()
            return True
        else:
            return False
        
    def get_groups_for_creating_test(self):
        result = []
        for i in self.groups_admin_of:
            group = Group()
            if group.create_with_id(i):
                result.append({
                    "name": group.title,
                    "id": group.id
                })
        return result


class Group():
    def __init__(self):
        self.id = None
        self.title = ''
        self.size = 0
        self.tests = []
        self.admins = []
        self.users = []
        self.users_limit = 100
        self.admins_limit = 10

    def create_new(self, title, first_admin_id):
        self.title = title
        self.admins.append(first_admin_id)
        self.size += 1
        try:
            new_group = UserGroupModel(
                id = self.id,
                title = self.title,
                size = self.size,
                admins = self.admins,
                users = self.users,
                tests = self.tests,
                users_limit = self.users_limit,
                admins_limit = self.admins_limit,
            )
            db.session.add(new_group)
            db.session.commit()
            return True, new_group.id
        except:
            return False

    def create_with_id(self, id):
        new_group = UserGroupModel.query.get(id)
        if not new_group:
            return False
        self.id = new_group.id
        self.title = new_group.title
        self.size = new_group.size
        self.admins = new_group.admins
        self.users = new_group.users
        self.tests = new_group.tests
        self.users_limit = new_group.users_limit
        self.admins_limit = new_group.admins_limit
        return True

    def update_group_in_db(self):
        group_to_update = UserGroupModel.query.get(self.id)
        group_to_update.id=self.id
        group_to_update.title=self.title
        group_to_update.size=self.size
        group_to_update.tests=self.tests
        group_to_update.admins=self.admins
        group_to_update.users=self.users
        group_to_update.users_limit=self.users_limit
        group_to_update.admins_limit=self.admins_limit
        db.session.commit()

    def add_user(self, user):
        if self.size <= self.users_limit and user.id not in self.admins and user.id not in self.users:
            self.users.append(user.id)
            self.size += 1
            self.update_group_in_db()
            return True
        else:
            return False
    
    def add_admin(self, id):
        if len(self.admins) <= self.admins_limit:
            self.admins.append(id)
            self.size += 1
            self.update_group_in_db()
            return True
        else:
            return False
    
    def add_test(self, id):
        if id not in self.tests:
            self.tests.append(id)
        self.update_group_in_db()

    def delete_user(self, id):
        try:
            self.users.remove(id)
            self.size -= 1
            self.update_group_in_db()
            return True
        except:
            db.session.rollback()
            return False
    
    def delete_admin(self, id):
        try:
            self.admins.remove(id)
            self.size -= 1
            self.update_group_in_db()
            return True
        except:
            db.session.rollback()
            return False

    def delete_person(self, id):
        if id in self.admins and len(self.admins) == 1:
            self.delete_group(id)
            return True
        elif id in self.admins:
            self.delete_admin(id)
            return True
        elif id in self.users:
            self.delete_user(id)
            return True
        else:
            return False
        
    def make_user_admin(self, id):
        return self.delete_user(id) and self.add_admin(id)
    
    def make_admin_user(self, id):
        return self.delete_admin(id) and self.add_user(id)

    def delete_group(self, admin_id):
        if admin_id not in self.admins:
            return False
        else:
            try:
                for i in self.users:
                    user = User()
                    user.create_with_id(i)
                    user.delete_group_user_of(self.id)
                for j in self.admins:
                    user = User()
                    user.create_with_id(j)
                    user.delete_group_admin_of(self.id)
                for k in self.tests:
                    test = Test()
                    test.create_with_id(k)
                    test.delete_for_group(self.id)
                group_to_delete = UserGroupModel.query.get(self.id)
                db.session.delete(group_to_delete)
                db.session.commit()
                return True
            except:
                db.session.rollback()
                return False

    def change_title(self, new_title):
        if new_title is not None:
            try:
                self.title = new_title
                self.update_group_in_db()
                return True
            except:
                db.session.rollback()
                return False
        else:
            return False
    
    def get_test(self, id=None):
        if id is None:
            tests = []
            for test_id in self.tests:
                test = TestModel.query.get(test_id)
                if test:
                    tests.append(test)
            return tests
        elif id in self.tests:
            return TestModel.query.get(id)
        else:
            pass

    def get_members(self, user_id):
        users, admins = [], []
        for uid in self.users:
            user = User()
            if user.create_with_id(uid):
                users.append({
                    "name": user.name,
                    "admin": False,
                    "you": user.id == user_id,
                    "id": user.id
                })
        for aid in self.admins:
            admin = User()
            if admin.create_with_id(aid):
                admins.append({
                    "name": admin.name,
                    "admin": True,
                    "you": admin.id == user_id,
                    "id": admin.id
                })
        return users + admins

    def change_users_limit(self, admin_id, limit=40):
        print(admin_id, limit)
        if admin_id in self.admins:
            self.users_limit = limit
        else:
            # Ошибка?
            pass

    def change_admins_limit(self, admin_id, limit=40):
        print(admin_id, limit)
        if admin_id in self.admins:
            self.admins_limit = limit
        else:
            # Ошибка?
            pass

    def is_admin(self, id):
        if id in self.admins:
            return True
        else:
            return False


class Test():
    def __init__(self):
        self.id = None
        self.title = ''
        self.description = ''
        self.groups = [] # пока список из одного элемента, задел на будущее
        self.is_visible = False
        self.questions = []
        self.answers = []
        self.users_max_score = []
        self.users_attempts = []

    def create_new(self, test_data: dict):
        try:
            validated_input, processed_questions, max_score = TestDataProcessor.process_input_data(test_data)
            db_data = TestDataProcessor.prepare_for_db(
                validated_input, 
                processed_questions, 
                max_score
            )
            test_in_db = TestModel(
                group_ids=db_data['group_ids'],
                title=db_data['title'],
                description=db_data['description'],
                is_visible=db_data['is_visible'],
                questions=db_data['questions'],
                answers=db_data['answers'],
                users_max_score=db_data['users_max_score'],
                users_attempts=db_data['users_attempts']
            )
            db.session.add(test_in_db)
            db.session.commit()
            self.create_with_id(test_in_db.id)
            return True
        except Exception as e:
            db.session.rollback()
            return False

    def create_with_id(self, id):
        new_test = TestModel.query.get(id)
        if not new_test:
            return False
        self.id = new_test.id
        self.title = new_test.title
        self.description = new_test.description
        self.groups = new_test.group_ids
        self.is_visible = new_test.is_visible
        self.questions = new_test.questions
        self.answers = new_test.answers
        self.users_max_score = new_test.users_max_score
        self.users_attempts = new_test.users_attempts
        return True

    def update_test_in_db(self):
        test_to_update = TestModel.query.get(self.id)
        if test_to_update:
            test_to_update.group_ids = self.groups
            test_to_update.title = self.title
            test_to_update.description = self.description
            test_to_update.is_visible = self.is_visible
            test_to_update.questions = self.questions
            test_to_update.answers = self.answers
            test_to_update.users_max_score = self.users_max_score
            test_to_update.users_attempts = self.users_attempts
            db.session.commit()
            return True
        return False
    
    def to_frontend_format(self):
        frontend_questions = []
        for i in self.questions:
            frontend_question = {
                "question": i["text"],
                "options": [{"title": j} for j in i["options"]]
            }
            frontend_questions.append(frontend_question)
        
        test_id = self.id
        
        return {
            "testID": test_id,
            "questionsQuantity": len(frontend_questions),
            "testName": self.title,
            "testDescription": self.description or "",
            "questionsAndOptions": frontend_questions
        }
    
    def check_answers(self, user_answers: list, user_name: str):
        score = 0
        max_score = 0
        detailed_results = []
        for i in range(len(self.answers)):
            correct_data = self.answers[i]
            correct_indices = correct_data.get('correct_options')
            points_per_question = correct_data.get('points')
            max_score += points_per_question
            user_answer_data = user_answers[i]
            user_selected = user_answer_data.get('answers')
            question_data = self.questions[i]
            options = question_data.get('options')
            correct_set = set(correct_indices)
            user_set = set(user_selected)
            if correct_set == user_set:
                question_score = points_per_question
            else:
                question_score = 0   
            score += question_score
            user_answers_texts = [options[idx] for idx in user_selected if idx < len(options)]
            correct_answers_texts = [options[idx] for idx in correct_indices if idx < len(options)]
            
            detailed_results.append({
                'question': user_answer_data.get('question', f'Вопрос {i+1}'),
                'userAnswers': user_answers_texts,
                'correctAnswers': correct_answers_texts,
                'pointsEarned': question_score,
                'maxPoints': points_per_question
            })
        
        current_time = datetime.now()
        formatted_time = current_time.strftime("%d.%m.%Y %H.%M")
        self.users_attempts.append({
            "name": user_name,
            "points": score,
            "time": formatted_time
        })
        self.update_test_in_db()
        return {
            'testName': self.title,
            'userScore': score,
            'maxScore': max_score,
            'detailedResults': detailed_results
        }

    def change_title(self, new_title):
        self.title = new_title

    def change_description(self, new_description):
        self.description = new_description

    def change_test(self, questions, answers):
        self.questions = questions
        self.answers = answers
    
    def open_for_group(self, group_id):
        self.groups.append(group_id)

    def delete_for_group(self, group_id):
        if len(self.groups) == 1:
            self.delete_test()
        else:
            self.groups.remove(group_id)

    def delete_test(self):
        try:
            test_to_delete = TestModel.query.get(self.id)
            db.session.delete(test_to_delete)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            return False

    def publish_test(self):
        self.is_visible = True
        self.update_test_in_db()

    def archive_test(self):
        try:
            self.is_visible = False
            self.update_test_in_db()
            return True
        except Exception as e:
            return False
        
    def dearchive_test(self):
        try:
            self.is_visible = True
            self.update_test_in_db()
            return True
        except Exception as e:
            return False

    def update_max_score(self, user_id, max_score):
        score_now = self.users_max_score.get(user_id)
        if max_score > score_now:
            self.users_max_score[user_id] = max_score
        else:
            # Ошибка?
            pass

    def update_attempts(self, user_id):
        self.users_attempts[user_id] += 1