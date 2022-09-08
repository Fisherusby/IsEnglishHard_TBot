from models.base_models import Base
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.orm import Session

engine = create_engine('sqlite:///bot_db.db', echo=True, future=True)

if not database_exists(engine.url):
    create_database(engine.url)
    Base.metadata.create_all(engine)
print(database_exists(engine.url))


