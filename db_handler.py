from sqlalchemy import engine, create_engine, Column, String
from sqlalchemy.orm import declarative_base, sessionmaker

# Sqlalchemy
# ://username:password@host/db_name
# engine = create_engine("mysql+pymysql://root:Password@localhost/ez_chat",
#                        echo=False, future=True)

engine = create_engine("postgresql+psycopg2://vsggyadxaqinab:0ca7e9fe334e50369eeb67d2365bc3f3203afd5f6b4c8720c00b71dff921a534@ec2-34-248-169-69.eu-west-1.compute.amazonaws.com/dc20hofmu13lal",
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
