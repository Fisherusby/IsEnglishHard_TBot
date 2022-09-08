from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, ForeignKey, Integer, String, Table, Boolean

Base = declarative_base()


user_dictionary = Table('user_dictionary',
                        Base.metadata, Column('user_id', Integer(), ForeignKey('user_account.id')),
                        Base.metadata, Column('word_id', Integer(), ForeignKey('word.id')),
                        )


words_sentence = Table('words_sentence',
                       Base.metadata, Column('sentence_id', Integer(), ForeignKey('sentence.id')),
                       Base.metadata, Column('word_id', Integer(), ForeignKey('word.id')),
                       )


class User(Base):
    __tablename__ = 'user_account'
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer)
    dictionary = relationship('Word', secondary=user_dictionary, backref="users")


class Word(Base):
    __tablename__ = 'word'
    id = Column(Integer, primary_key=True)
    en = Column(String(30), unique=True)
    transcription = Column(String(45), default='')
    ru = Column(String(30), default='')
    is_translate = Column(Boolean, default=False)

    def __repr__(self):
        return f'{self.en} {self.transcription} - {self.ru}'


class Sentence(Base):
    __tablename__ = 'sentence'
    id = Column(Integer, primary_key=True)
    en = Column(String(512), unique=True)
    ru = Column(String(512))

    words = relationship('Word', secondary=words_sentence, backref="sentences")
