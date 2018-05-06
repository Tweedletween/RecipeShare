from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine.url import URL
from models import Base, Category


DATABASE = {
    'drivername': 'postgres',
    'host': 'localhost',
    'port': '5432',
    'username': 'recipeapp',
    'password': 'password',
    'database': 'recipes'
}

# Connect to DB and create session
engine = create_engine(URL(**DATABASE))
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


category_names = [
    'Quick & Easy',
    'Slow Cooker',
    'Low-Calorie',
    'Salad',
    'Soup',
    'Appetizer',
    'Vegetables',
    'Meat',
    'Seafood',
    'Dessert'
    ]

for name in category_names:
    category = Category(name=name)
    session.add(category)
    session.commit()

print("Added Categories into DB.")
