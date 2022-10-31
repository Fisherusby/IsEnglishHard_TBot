from telebot import types

empty_markups = types.ReplyKeyboardRemove()

study_btn = types.KeyboardButton('/studystart 🎓')
dictionary_btn = types.KeyboardButton('/dictionary 📖')

main_menu_markups = types.ReplyKeyboardMarkup(row_width=1).add(study_btn, dictionary_btn)

dict_showall_btn = types.KeyboardButton('/showall')
dict_add_btn = types.KeyboardButton('/addwords')

dict_menu_markups = types.ReplyKeyboardMarkup(row_width=1).add(dict_showall_btn, dict_add_btn)

stop_add_btn = types.KeyboardButton('/addstop')

stop_add_menu_markups = types.ReplyKeyboardMarkup(row_width=1).add(stop_add_btn)

