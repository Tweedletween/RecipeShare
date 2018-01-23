from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.dialects.sqlite import BLOB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from passlib.apps import custom_app_context as pwd_context


Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    picture = Column(String(250))
    email = Column(String(250), nullable=False)


class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, index=True)


class Item(Base):
    __tablename__ = 'item'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    pic_path = Column(String)
    ingredients = Column(String(300), nullable=False)
    steps = Column(String(2000), nullable=False)
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    # Return object data in easily serialized format
    def serialize(self):
        return {
            'name': self.name,
            'ingredients': self.ingredients,
            'steps': self.steps,
            'category': self.category.name,
        }


engine = create_engine('sqlite:///recipes.db')
Base.metadata.create_all(engine)
