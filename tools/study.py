from tools.translate import get_user_dictionary
import random
from tools.translate import get_word, get_voice_word
from telebot import types
from tools.markups import main_menu_markups, empty_markups


class StudyBot:
    __STUDY = {}

    def __init__(self, bot):
        self.__bot = bot

    @staticmethod
    def text_fix(text: str):
        return text.replace('-', '\-').replace('_', '\_')

    def start_study(self, user_id):
        self.__STUDY[user_id] = StudyWords(user_id)

        markups = types.ReplyKeyboardMarkup(row_width=2)
        btn_stat = types.KeyboardButton('/study_stat 📈')
        btn_stop = types.KeyboardButton('/study_stop 😴')
        markups.row(btn_stat)
        markups.row(btn_stop)

        self.__bot.send_message(user_id, f'Study is start! Good luck!', reply_markup=markups)
        self.send_next_word(user_id)

    def stop_study(self, user_id):
        self.__bot.send_message(user_id, 'Your study is over!', reply_markup=main_menu_markups)
        if self.__STUDY.get(user_id) is None:
            return
        self.send_stats(user_id)
        del self.__STUDY[user_id]

    def send_stats(self, user_id):
        total, in_dict, total_fails, fails_by_words = self.__STUDY[user_id].get_stats()
        stats_text = '📈 Statistics:\n'
        stats_text += f'📝 total word count - {total}\n'
        stats_text += f'✅ passed - {total - in_dict}\n'
        stats_text += f'❌ mistakes - {total_fails}\n'
        stats_text += f'🔴 words with mistakes - {len(fails_by_words)}\n'
        self.__bot.send_message(user_id, stats_text)

    def send_next_word(self, user_id, fail=False):
        study_dict = self.__STUDY.get(user_id)
        if study_dict is None:
            self.__bot.send_message(user_id, 'Study haven`t start')
            return

        if fail:
            study_dict.answer_is_fail()

        word = next(study_dict)

        if word is None:
            self.stop_study(user_id)
            return

        next_word = get_word(word)
        audio = get_voice_word(next_word.en)
        self.__bot.send_voice(user_id, audio, caption=f'{next_word.en} {next_word.transcription}')
        self.__bot.send_message(
            user_id,
            f'Right answer: ||{self.text_fix(next_word.ru.center(20, "_"))}||',
            parse_mode='MarkdownV2'
        )

        markups2 = types.InlineKeyboardMarkup()
        btn_right = types.InlineKeyboardButton('✅ right', callback_data='study_right')
        btn_incorrect = types.InlineKeyboardButton('❌ incorrect', callback_data='study_incorrect')
        markups2.add(btn_right, btn_incorrect)

        self.__bot.send_message(user_id, f'Your answer was', parse_mode='MarkdownV2', reply_markup=markups2)


class StudyWords:
    """
    Generator words for study. Also count statistics.
    """
    __dictionary = []
    __last_word = None
    __fails_count = {}
    __total_fails = 0
    __total_words = 0

    def __init__(self, user_id):
        self.__user_id = user_id
        self.__dictionary = get_user_dictionary(user_id)
        self.__total_words = len(self.__dictionary)
        random.shuffle(self.__dictionary)

    def __last_fail(self):
        """
        Count haw many answers ware failure.
        """
        if self.__fails_count.get(self.__last_word) is None:
            self.__fails_count[self.__last_word] = 1
        else:
            self.__fails_count[self.__last_word] += 1
        self.__total_fails += 1

    def answer_is_fail(self):
        """
        Set last answer as failure and add this word in end __dictionary
        """
        if self.__last_word is not None:
            self.__dictionary.append(self.__last_word)
            self.__last_fail()
            self.__last_word = None

    def __next__(self):
        """
        Generate words from __dictionary for study
        :return: first place word from __dictionary
        """
        if len(self.__dictionary) == 0:
            return None
        self.__last_word = self.__dictionary.pop(0)
        return self.__last_word

    def get_stats(self):
        """
        Return study's statistics
        :return:
        """
        in_dict = len(self.__dictionary)
        if self.__last_word is not None:
            in_dict += 1
        return self.__total_words, in_dict, self.__total_fails, self.__fails_count

    def count(self):
        """
        Return length words in __dictionary
        """
        return len(self.__dictionary)
