from telebot import types

empty_markups = types.ReplyKeyboardRemove()

study_btn = types.KeyboardButton('/studystart 🎓')
dictionary_btn = types.KeyboardButton('/studystart 📖')

main_menu_markups = types.ReplyKeyboardMarkup(row_width=1).add(study_btn, dictionary_btn)