from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists
from sqlalchemy.orm import Session, sessionmaker

engine = create_engine('sqlite:///bot_db.db?check_same_thread=False', echo=False, future=True)

session = Session(bind=engine)
