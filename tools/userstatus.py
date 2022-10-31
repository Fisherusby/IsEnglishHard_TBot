class UserStatus:
    __status = {}

    def __init__(self):
        pass

    def __check(self, user_id):
        if self.__status.get(user_id) is None:
            self.__status[user_id] = {}

    def set_value(self, user_id, arg, value):
        self.__check(user_id)
        self.__status[user_id][arg] = value

    def get_value(self, user_id, arg):
        self.__check(user_id)
        return self.__status[user_id].get(arg)
