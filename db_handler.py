from sqlalchemy import engine, create_engine, Column, String
from sqlalchemy.orm import declarative_base, sessionmaker

# Sqlalchemy
engine = create_engine("mysql+pymysql://root:Password@localhost/ez_chat",
                       echo=False, future=True)
Base = declarative_base()

# User class


class User(Base):
    __tablename__ = 'User'

    username = Column(String(50), primary_key=True)
    password = Column(String(50))

    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password

    def __repr__(self):
        return f'username: {self.username}; password: {self.password}'


# Create the database
Base.metadata.create_all(engine)

# Create a session
Session = sessionmaker(bind=engine)
