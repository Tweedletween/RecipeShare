from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Category


# Connect to DB and create session
engine = create_engine('sqlite:///recipies.db')
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
