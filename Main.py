import os
import telebot
from telebot import types
from tools.translate import get_translate, get_voice_word, create_user, add_word_dictionary, get_user_dictionary, \
    get_word, clear_sentence, bolt_word
from tools.files import dict_to_file
from tools.study import StudyBot
from tools.markups import main_menu_markups, empty_markups


API_TOKEN = os.environ.get('BOT_API_TOKEN')

# Exit if API key not exist
if API_TOKEN is None:
    print('ERROR: Can`t run Bot. Bot API_TOKEN not available.')
    exit()


# os.environ["API_TOKEN"]
bot = telebot.TeleBot(API_TOKEN, parse_mode=None)

# set study object
study_bot = StudyBot(bot)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    create_user(message.chat.id)


@bot.message_handler(commands=['wordinfo'])
def word_info(message):
    inc_str = clear_sentence(message.text)
    inc_words = inc_str.split()

    if len(inc_words) > 1:
        word = get_word(inc_words[1])
        if word is None:
            bot.send_message(message.chat.id, f'Word not found!')
            return

        audio = get_voice_word(word.en)
        bot.send_voice(message.chat.id, audio, caption=f'ADD:\n {word.en} {word.transcription} - {word.ru}')
        bot.send_message(message.chat.id, f'Found {len(word.sentences)} sentences with word - {word.en}')

        for s in word.sentences[:10]:
            bot.send_message(message.chat.id, f'{bolt_word(s.en, word.en)}', parse_mode="Markdown")

    else:
        bot.send_message(message.chat.id, f'You can look only one word`s information')


# study start
@bot.message_handler(commands=['studystart'])
def study_start(message):
    study_bot.start_study(message.chat.id)


# study. answer was right
@bot.callback_query_handler(func=lambda c: c.data == 'study_right')
def callback_study_right(callback: types.CallbackQuery):
    # answer for callback. according to the documentation it needs to be done
    bot.answer_callback_query(callback.id)

    # remove in line menu after answer
    markup = types.InlineKeyboardMarkup()
    bot.edit_message_text(f'✅ right', reply_markup=markup, chat_id=callback.message.chat.id,
                          message_id=callback.message.message_id)

    study_bot.send_next_word(callback.from_user.id)


# study. answer was incorrect
@bot.callback_query_handler(func=lambda c: c.data == 'study_incorrect')
def callback_study_incorrect(callback):
    # answer for callback. according to the documentation it needs to be done
    bot.answer_callback_query(callback.id)

    # remove in line menu after answer
    markup = types.InlineKeyboardMarkup()
    bot.edit_message_text(f'❌ incorrect', reply_markup=markup, chat_id=callback.message.chat.id,
                          message_id=callback.message.message_id)

    study_bot.send_next_word(callback.from_user.id, fail=True)


# study. Show study statistics
@bot.message_handler(commands=['study_stat'])
def study_stat(message):
    study_bot.send_stats(message.chat.id)


# study. stop study
@bot.message_handler(commands=['study_stop'])
def study_stop(message):
    study_bot.stop_study(message.chat.id)


@bot.message_handler(commands=['add'])
def add_word(message):
    inc_str = clear_sentence(message.text)
    inc_words = set(inc_str.split()[1:])

    for w in inc_words:
        tr = get_translate(w)
        if tr:
            audio = get_voice_word(w)
            bot.send_voice(message.chat.id, audio, caption=f'ADD:\n {tr.en} {tr.transcription} - {tr.ru}')

            add_word_dictionary(message.chat.id, tr)
        else:
            bot.send_message(message.chat.id, f'ERROR add word:\n {w}')


@bot.message_handler(commands=['showall'])
def show_all(message):
    all_words = get_user_dictionary(message.chat.id)
    if all_words:
        bot.send_message(message.chat.id, f'You have {len(all_words)} words in dict:')
        bot.send_message(message.chat.id, '\n'.join(all_words))
    else:
        bot.send_message(message.chat.id, 'Empty')


@bot.message_handler(commands=['menu'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Главное меню", reply_markup=main_menu_markups)


@bot.message_handler(content_types=['photo'])
def get_photo(message):
    bot.send_message(message.chat.id, 'Temporarily disabled')
    return
    # file_info = bot.get_file(message.photo[-1].file_id)
    # file_path = 'https://api.telegram.org/file/bot{0}/{1}'.format(API_TOKEN, file_info.file_path)
    # download_photo(file_path)


@bot.message_handler(commands=['getdict'])
def get_dict(message):
    dict_file = open(dict_to_file(message.chat.id), 'rb')
    # dict_file.name = 'dictionary.txt'
    bot.send_document(message.chat.id, dict_file, caption='dictionary.txt')
    pass


@bot.message_handler(func=lambda m: True)
def echo_all(message):
    markups = types.ReplyKeyboardMarkup(row_width=1)
    menu_btn = types.KeyboardButton('/menu')
    markups.row(menu_btn)
    # bot.reply_to(message, message.text, reply_markup=markups).
    print(f'{message.chat.id = } , {message.text = }')


if __name__ == '__main__':
    import db
    if db.database_exists(db.engine.url):
        print('BOT is starting')
        bot.infinity_polling()
    else:
        print('FATAL ERROR: DATABASE NOT EXIST!')
