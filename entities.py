from models import UserModel, UserGroupModel, TestModel
from service.db_init import db
import json


class User():
    def __init__(self, user_id=None):
        self.id = None
        self.name = None
        self.groups = []
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
            self.groups = user_data.groups
            self.email = user_data.email
            self.avatar_url = user_data.avatar_url
            self.provider = user_data.provider
            self.access_token = user_data.access_token
            self.refresh_token = user_data.refresh_token
            self.token_expiry = user_data.token_expiry
    
    def create_with_token(self, access_token):
        if not access_token:
            return None
        
        user_data = UserModel.query.filter_by(access_token=access_token).first()
        
        if user_data:
            self.id = user_data.id
            self.name = user_data.name
            self.groups = user_data.groups
            self.email = user_data.email
            self.avatar_url = user_data.avatar_url
            self.provider = user_data.provider
            self.access_token = user_data.access_token
            self.refresh_token = user_data.refresh_token
            self.token_expiry = user_data.token_expiry


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

    def create_new(self, title):
        self.title = title
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
            return True
        except:
            return False

    def create_with_id(self, id):
        new_group = UserGroupModel.query.get(id)
        self.id = id
        self.users = new_group.users

    def add_user(self, user):
        if self.size <= self.users_limit:
            self.users.append(user.id)
            self.size += 1
        else:
            # Ошибка?
            pass
    
    def add_admin(self, id, admin_id):
        print(id, admin_id)
        if len(self.admins) <= self.admins_limit and admin_id in self.admins:
            # Добавляем админа
            pass
        else:
            # Ошибка?
            pass

    def delete_user(self, user):
        print(user.id)
        if user.id in self.users:
            self.users.remove(user.id)
        else:
            # Ошибка?
            pass
    
    def delete_admin(self, id):
        print(id)
        if id in self.admins:
            self.admins.remove(id)
        else:
            # Ошибка?
            pass

    def delete_group(self, admin_id):
        print(admin_id)
        # Удалить группу из бд

    def change_title(self, admin_id, new_title):
        print(admin_id)
        if admin_id in self.admins:
            self.title = new_title
        else:
            # Ошибка?
            pass
    
    def get_test(self, id=None):
        print(id)
        if id == None:
            # Отдаем все тесты для этой группы
            pass
        elif id in self.tests:
            return self.tests[id]
        else:
            # Ошибка?
            pass
                
    def delete_test(self, admin_id, id=None):
        print(id, admin_id)
        if admin_id in self.admins:
            if id == None:
                # Удалить из бд все тесты этой группы
                self.tests = []
            elif id in self.tests:
                # Удалить из бд этот тест
                self.tests.remove(id)
            else:
                # Ошибка?
                pass
        else:
            # Ошибка?
            pass

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


class Test():
    def __init__(self):
        self.id = None
        self.title = ''
        self.description = ''
        self.groups = [] # пока список из одного элемента, задел на будущее
        self.is_visible = False
        self.questions = []
        self.answers = []
        self.users_max_score = {}
        self.users_attempts = {}

    def create_new(self, test_data: dict):
        test_in_db = TestModel(
            id=0,
            group_ids=test_data['groupID'],
            title=test_data['testName'],
            description=test_data['testDescription'],
            is_visible=True,
            questions=str(test_data['questionsAndOptions']),
            correct_answers=None,
            users_max_score=0,
            users_attempts=0
        )
        db.session.add(test_in_db)
        db.session.commit()

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
        if len(self.groups == 1):
            self.delete_test()
        else:
            self.groups.remove(group_id)

    def delete_test(self):
        # Удалять тест из бд
        pass

    def publish_test(self):
        self.is_visible = True

    def close_test(self):
        self.is_visible = False

    def update_max_score(self, user_id, max_score):
        score_now = self.users_max_score.get(user_id)
        if max_score > score_now:
            self.users_max_score[user_id] = max_score
        else:
            # Ошибка?
            pass

    def update_attempts(self, user_id):
        self.users_attempts[user_id] += 1