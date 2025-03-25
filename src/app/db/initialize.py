from db.settings import engine
from db.models.Base import Base
from db.models.User import User
from db.models.Digests import Digest

def init_db():
    # Create all tables
    Base.metadata.create_all(bind=engine)
