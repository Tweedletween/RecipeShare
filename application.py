from flask import Flask, render_template, request, redirect, url_for, flash,jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Category, Item
from base64 import b64encode

app = Flask(__name__)

# Connect to DB and create session
engine = create_engine('sqlite:///recipies.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/')
@app.route('/categories')
def index():
    categories = session.query(Category)
    com_items = session.query(Item, Category).filter(Item.category_id==Category.id).order_by(Item.id.desc()).limit(10)
    title = ''
    return render_template('index.html', categories=categories, com_items=com_items, title=title)


@app.route('/categories/<int:category_id>')
def showCategory(category_id):
    categories = session.query(Category)
    items = session.query(Item).filter_by(category_id=category_id)
    category = session.query(Category).filter_by(id=category_id).one()
    title = category.name
    return render_template('showcategory.html', categories=categories, items=items, category_id=category_id, title=title)


@app.route('/categories/items/<int:id>')
def viewItem(id):
    # Check the item whether exists
    item = session.query(Item).filter_by(id=id).first()
    if item is None:
        return jsonify("Item not Existed!")
    category = session.query(Category).filter_by(id=item.category_id).one()
    title = item.name
    return render_template('showitem.html', item=item, category=category, title=title)


@app.route('/categories/<int:category_id>/items/new', methods=['GET', 'POST'])
def newItem(category_id):
    print("In newItem, request.form: %s" % request.form)
    if request.method == 'POST':
        # Check data valid
        if 'category_id' not in request.form:
            return jsonify("Error, category name not selected!")
        target_category = session.query(Category).filter_by(id=request.form['category_id']).first()
        if not target_category:
            return jsonify("Error, category not existed!")
        if 'name' not in request.form or 'steps' not in request.form or 'ingredients' not in request.form:
            return jsonify("Error, required value not entered!")

        # Store new data into DB
        print("request.files['pic']: %s" % request.files['pic'])
        newItem = Item(name=request.form.get('name'),
            ingredients=request.form.get('ingredients'),
            steps=request.form.get('steps'),
            category_id=target_category.id,
            pic=b64encode(request.files['pic'].read()))
        session.add(newItem)
        session.commit()
        flash("New Item Created!")
        return redirect(url_for('index'))
    else:
        categories = session.query(Category)
        title = 'New A Recipe'
        return render_template('newitem.html', categories=categories, title=title, default_category_id=category_id)


@app.route('/categories/items/<int:id>/edit', methods=['GET', 'POST'])
def editItem(id):
    # Check the item to be updated valid
    item = session.query(Item).filter_by(id=id).first()
    if item is None:
        return jsonify("Item not Existed!")

    if request.method == 'POST':
        # Check data valid
        if 'category_id' not in request.form:
            return jsonify("Error, category name not selected!")
        target_category = session.query(Category).filter_by(id=request.form['category_id']).first()
        if not target_category:
            return jsonify("Error, category not existed!")
        if 'name' not in request.form or 'steps' not in request.form or 'ingredients' not in request.form:
            return jsonify("Error, required value not entered!")

        # Update the data in DB
        item.name = request.form['name']
        item.ingredients = request.form['ingredients']
        item.steps = request.form['steps']
        item.category_id = target_category.id
        item.pic = b64encode(request.files['pic'].read())
        session.add(item)
        session.commit()
        flash("Category Modified")
        return redirect(url_for('index'))
    else:
        categories = session.query(Category)
        title = 'Update A Recipe'
        return render_template('edititem.html', item=item, categories=categories, title=title)


@app.route('/categories/items/<int:id>/delete', methods=['GET', 'POST'])
def deleteItem(id):
    # Check the item to be deleted valid
    item = session.query(Item).filter_by(id=id).first()
    if item is None:
        return jsonify("Item not Existed!")

    if request.method == 'POST':
        session.delete(item)
        session.commit()
        flash("Item %s Deleted" % item.name)
        return redirect(url_for('index'))
    else:
        title = "Delete Item?"
        category = session.query(Category).filter_by(id=item.category_id).one()
        return render_template('deleteitem.html', item=item, category=category, title=title)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
