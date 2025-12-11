from models import UserModel


class User():
    def __init__(self, user_id=None):
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
        self.size = None
        self.tests = []
        self.admins = []
        self.users = []
        self.users_limit = None
        self.admins_limit = None

    def add_user(self, id):
        print(id)
        if self.size <= self.users_limit:
            # Добавляем юзера
            pass
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

    def delete_user(self, id):
        print(id)
        if id in self.users:
            self.users.remove(id)
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