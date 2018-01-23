from flask import Flask, render_template, request, redirect, url_for, flash,jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Category, Item, User
import random, string

from flask import session as login_session
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError
import json
from flask import make_response
import httplib2
import requests


app = Flask(__name__)

# Connect to DB and create session
engine = create_engine('sqlite:///recipies.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


SAVE_PIC_PRE = '/static/imgs/'


@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


# Google Signin
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter', 401))
        response.headers['Content-Type'] = 'application/json'
        return response

    # Obtain authorization code
    code = request.data

    # Upgrade the authorization code into credentials object
    try:
        oauth_flow = flow_from_clientsecrets('g_client_secret.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check the access token is valid
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user
    g_id = credentials.id_token['sub']
    if result['user_id'] != g_id:
        response = make_response(json.dumps("Token's user ID doesn't match given user id"), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    g_client_id = json.loads(open('g_client_secret.json', 'r').read())['web']['client_id']
    if result['issued_to'] != g_client_id:
        response = make_response(json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check to see if user is already logged in
    stored_access_token = login_session.get('access_token')
    stored_g_id = login_session.get('g_id')
    if stored_access_token is not None and g_id == stored_g_id:
        response = make_response(json.dumps('Current user is already connnected.'), 200)
        response.headers['Content-Type'] = 'application/json'

    # Store the access token in the session
    login_session['access_token'] = access_token
    login_session['g_id'] = g_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = answer.json()
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    login_session['provider'] = 'google'

    user_id = getUserIdByEmail(data['email'])
    if user_id is None:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, %s!</h1>' % login_session['username']
    output += '<img src="'
    output += login_session['picture']
    output += '" style="width: 300px; height: 300px; border-radius: 150px; -webkit-border_readius: 150px; -moz-border-radius: 150px;">'
    flash("You are now logged in as %s" % login_session['username'])
    return output


def createUser(login_session):
    newUser = User(name=login_session.get('username'), email=login_session.get('email'), picture=login_session.get('picture'))
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session.get('email')).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserIdByEmail(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

# Facebook login
@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data

    app_id = json.loads(open('fb_client_secret.json', 'r').read())['web']['app_id']
    app_secret = json.loads(
        open('fb_client_secret.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
        app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    url = 'https://graph.facebook.com/v2.8/me?access_token=%s&fields=name,id,email' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['fb_id'] = data["id"]
    # The token must be stored in the login_session in order to properly logout
    login_session['access_token'] = access_token

    # Get user picture
    url = 'https://graph.facebook.com/v2.8/me/picture?access_token=%s&redirect=0&height=200&width=200' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)
    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserIdByEmail(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("Now logged in as %s" % login_session['username'])
    return output


# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['g_id']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['fb_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        del login_session['access_token']
        flash("You have successfully been logged out.")
        return redirect(url_for('index'))
    else:
        flash("You were not logged in")
        return redirect(url_for('index'))


# Google disconnect
# Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

# Facebook Disconnect
# Revoke a current user's token and reset their login_session
@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['fb_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id,access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"


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
    if 'username' not in login_session:
         return redirect('/login')

    if request.method == 'POST':
        # Check data valid
        if 'category_id' not in request.form:
            return jsonify("Error, category name not selected!")
        target_category = session.query(Category).filter_by(id=request.form['category_id']).first()
        if not target_category:
            return jsonify("Error, category not existed!")
        if 'name' not in request.form or 'steps' not in request.form or 'ingredients' not in request.form:
            return jsonify("Error, required value not entered!")

        # Store uploaded image to local folder
        if 'pic' in request.files:
            pic_name = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
            pic_type = request.files['pic'].content_type.split('/')[-1]
            pic_path = SAVE_PIC_PRE + pic_name + '.' + pic_type
            request.files['pic'].save('.' + pic_path)

        # Store new data into DB
        newItem = Item(name=request.form.get('name'),
            ingredients=request.form.get('ingredients'),
            steps=request.form.get('steps'),
            category_id=target_category.id,
            pic_path=pic_path,
            user_id=login_session['user_id'])
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
    if 'username' not in login_session:
         return redirect('/login')

    # Check the item to be updated valid
    item = session.query(Item).filter_by(id=id).first()
    if item is None:
        return jsonify("Item not Existed!")
    if item.user_id != login_session['user_id']:
        return jsonify("You do not have the right to modify this item!")

    if request.method == 'POST':
        # Check data valid
        if 'category_id' not in request.form:
            return jsonify("Error, category name not selected!")
        target_category = session.query(Category).filter_by(id=request.form['category_id']).first()
        if not target_category:
            return jsonify("Error, category not existed!")
        if 'name' not in request.form or 'steps' not in request.form or 'ingredients' not in request.form:
            return jsonify("Error, required value not entered!")

        # Store uploaded image to local folder
        print("request.files['pic']: %s" % request.files['pic'])
        if 'pic' in request.files:
            if not request.files['pic'].content_type.startswith('image'):
                return jsonify("Error, not image file type!")
            pic_name = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
            pic_type = request.files['pic'].content_type.split('/')[-1]
            pic_path = SAVE_PIC_PRE + pic_name + '.' + pic_type
            request.files['pic'].save('.' + pic_path)

        # Update the data in DB
        item.name = request.form['name']
        item.ingredients = request.form['ingredients']
        item.steps = request.form['steps']
        item.category_id = target_category.id
        if request.files['pic']:
            item.pic_path = pic_path
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
    if 'username' not in login_session:
          return redirect('/login')

    # Check the item to be deleted valid
    item = session.query(Item).filter_by(id=id).first()
    if item is None:
        return jsonify("Item not Existed!")
    if item.user_id != login_session['user_id']:
        return jsonify("You do not have the right to modify this item!")

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
