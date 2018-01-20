from flask import Flask, render_template, request, redirect, url_for, flash,jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Category, Item


app = Flask(__name__)

# Connect to DB and create session
engine = create_engine('sqlite:///recipies.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/')
def index():
    categories = session.query(Category)
    print(categories[0])
    #lastest-items = session.query(Item)
    title = "Recipe Share"
    return render_template('index.html', categories=categories, title=title)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
