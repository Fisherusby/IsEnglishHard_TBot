from bs4 import BeautifulSoup as BS
from googletrans import Translator
import requests
import os
import os.path
from gtts import gTTS
import re

from db import session
from models.base_models import User, Word, Sentence

VOICE_BASE = './voice_base/'
WORDS_DICT = {}


def bolt_word(sentence, word):
    return re.sub(fr'\b{word}\b', f'*{word}*', sentence)


def clear_sentence(string):
    """
    Delete .,;:-?-! and multy space from spring
    """
    string = re.sub(r'[.,;:-?-!]', '', string.lower())
    return re.sub(" +", " ", string)


def get_word(word):
    """
    Return word from database
    """
    query_word = session.query(Word).filter_by(en=word).first()
    return query_word


def get_user_dictionary(user_id):
    """
    Return user's word dictionary
    """
    user = session.query(User).filter(User.chat_id == user_id).first()
    res = []
    if user is not None:
        for w in user.dictionary:
            res.append(w.en)
    return res


def create_user(user_id):
    """
    Create user and his setting in database
    """
    user_query = session.query(User).filter(User.chat_id == user_id).first()
    if user_query is None:
        user_query = User(chat_id=user_id)
        session.add(user_query)
        session.commit()
    return user_query


def add_word_dictionary(user_id, word):
    """
    Add word in user dictionary
    """
    user_query = session.query(User).filter(User.chat_id == user_id).first()
    if user_query is not None:
        user_query.dictionary.append(word)
        session.commit()


def add_links_words_sentence(sentence):
    """
    Create relationship to sentence and words in this sentences
    """
    words = set(clear_sentence(sentence.en).split())
    # print(f'{words = }')
    for w in words:
        word = session.query(Word).filter_by(en=w).first()
        if word is None:
            word = Word(en=w)
            session.add(word)
        # print(f'{word = } , {word.id = } {word.en = }')
        # print(f'{sentence.words = }')
        sentence.words.append(word)
    # print(f'{sentence.words = }')
    session.commit()


def add_sentence(sentence_en, sentence_ru):
    """
    Add sentence in database. After it create relationship words
    """
    sentence_en = re.sub(" +", " ", sentence_en)
    # print(f'{sentence_en = } / {sentence_ru = } ')
    sentence = session.query(Sentence).filter(Sentence.en == sentence_en).first()
    if sentence is None:
        sentence = Sentence(en=sentence_en, ru=sentence_ru)
        session.add(sentence)
        add_links_words_sentence(sentence)
        session.commit()


def get_translate(word):
    """
    Get information about word from database. If there isn't word in database get word information from sources.
    Sources is https://englishlib.org/ (for transcription) and Translator (for translate)
    """
    query_word = session.query(Word).filter(Word.en == word, Word.is_translate is True).first()
    print(f'Get word: {word}')
    if query_word is None:
        try:
            print(f'   word not exist in base. try to get word from sources')
            translator = Translator()
            translate_text = translator.translate(word, src='en', dest='ru')
        except Exception as e:
            print(e)
            return False
        src_url = f'https://englishlib.org/dictionary/en-ru/{word}.html'
        r = requests.get(src_url)
        html = BS(r.text, 'html.parser')
        body = html
        div_tr = body.find('div', {"id": "uk_tr_sound"})

        if not div_tr:
            print(body)
            print(f'   WARNING!!! Word not found in the sources')
            print(f'https://englishlib.org/dictionary/en-ru/{word}.html')
            return False
        transcription = div_tr.find('big')
        section = body.find_all('section', {'class': 'phrases_t'})
        tbl_sent = section[1].find_all('p')
        print(f'   word found and has {int(len(tbl_sent)/2)} sentences')
        for i in range(0, len(tbl_sent), 2):
            # sentences = tr.find_all('p')
            # print(f'{sentences = }')
            add_sentence(tbl_sent[i].text, tbl_sent[i+1].text)
        print(f'   sentences add in base')
        query_word = session.query(Word).filter(Word.en == word).first()
        # print(query_word)
        if query_word is None:
            query_word = Word(en=word, ru=translate_text.text, transcription=transcription.text[1:])
            session.add(query_word)
        elif query_word.is_translate is False:
            query_word.ru = translate_text.text
            query_word.transcription = transcription.text[1:]
            query_word.is_translate = True

        session.commit()
    return query_word


def get_voice_word(word):
    """
    Get audio file for word from local folder. If there isn't file in local folder get his from source
    """
    if len(word) > 1:
        file_name = f'{VOICE_BASE}/{word[0]}/{word[1]}/{word}.mp3'
    else:
        file_name = f'{VOICE_BASE}/{word[0]}/{word}.mp3'
    if not os.path.exists(file_name):
        s = gTTS(word)
        os.makedirs(os.path.dirname(file_name), exist_ok=True)
        s.save(file_name)
    audio = open(file_name, 'rb')
    return audio

