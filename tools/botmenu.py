class NavigateMenu:

    back_btn = 'Back 🔙'

    menu = None
    bot = None

    __current_menu_position = {}

    def __init__(self, user_id):
        if self.menu is None:
            raise 'You need to set menu first'

        if self.bot is None:
            raise 'You need to set bot first'

        self.__user_id = user_id
        if self.__current_menu_position[user_id].get(user_id) is None:
            self.__current_menu_position[user_id] = self.menu

    def cmd(self):
        pass

    def __hello(self):
        pass

    def msg(self, message_text):



        # user send back message
        if message_text == self.back_btn:
            self.__click_back()

        # user send back message
        next_item = self.__current_menu_position[self.__user_id].is_menu_item(message_text)
        if next_item is not None:
            self.__click_item(next_item)
        else:
            self.__msg(message_text)

    def __msg(self, message_text):
        if self.__current_menu_position[self.__user_id].msg_action is not None:
            self.__current_menu_position[self.__user_id].msg_action(user_id=self.__user_id, message_text=message_text, bot=self.bot)

    def __click_back(self):
        if self.__current_menu_position[self.__user_id].back_action is not None:
            self.__current_menu_position[self.__user_id].back_action(self.__user_id)
        self.__change_position(self.__current_menu_position[self.__user_id].parrent())

    def __click_item(self, item):
        if self.__current_menu_position[self.__user_id].next_action is not None:
            self.__current_menu_position[self.__user_id].next_action(self.__user_id)

        if item.click_action is not None:
            item.click_action(self.__user_id)

        if item.has_items():
            self.__change_position(item)

    def __change_position(self, item):
        if item is not None:
            self.__current_menu_position[self.__user_id] = item


class MenuItem:
    __parent_item = None

    def __init__(self, btn_title, click_action=None, back_action=None, next_action=None, msg_action=None):
        self.title = btn_title
        self.click_action = click_action
        self.back_action = back_action
        self.next_action = next_action
        self.msg_action = msg_action
        self.__menu_items = []

    def _set_parent_item(self, parent):
        self.__parent_item = parent

    def _pop_menu_items(self, item):
        self.__menu_items.pop(self.__menu_items.index(item))

    def parent(self):
        return self.__parent_item

    def add_submenu(self, menu_items):
        for item in menu_items:
            if isinstance(item, MenuItem):
                if item.parent() is not None:
                    print(f'WARNING! Item already has parent ({item.parent()}) and parent will be replace')
                    item.parent()._pop_menu_items(item)
                self.__menu_items.append(item)
                item._set_parent_item(self)
            else:
                raise f'{item = } is not instance MenuItem'

    def __str__(self):
        return self.title

    def item_info(self):
        return f'{self.title} ( TM > {self.__parent_item} | SM > {list(map(lambda x: x.title, self.__menu_items))})'

    def menu_btns(self):
        return list(map(lambda x: x.title, self.__menu_items))

    def is_menu_item(self, item_title):
        for item in self.__menu_items:
            if item.title == item_title:
                return item

        return None