from sqlalchemy import Column, Integer, String, BLOB, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from passlib.apps import custom_app_context as pwd_context


Base = declarative_base()


class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, index=True)


class Item(Base):
    __tablename__ = 'item'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    pic = Column(BLOB)
    steps = Column(String, nullable=False)
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)


engine = create_engine('sqlite:///recipies.db')
Base.metadata.create_all(engine)
