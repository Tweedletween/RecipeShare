# RecipeShare

This is a Python MVC web application which lets user share their own recipes, with RESTful services.

### What this app does:
- Serves dynamic web content according to URI
- Used Google Sign-In, Facebook Login for authentication and authorization.
- Performed server-side rate-limiting for RESTful APIs.
- Used Python, data-driven application design pattern, Redis, JavaScirpt, jQuery, AJAX, Bootstrap, HTML, CSS.

### Demo
<img width="1280" alt="screen shot 2018-01-23 at 3 56 50 pm" src="https://user-images.githubusercontent.com/22652894/35308353-275de05e-005c-11e8-8aca-ec457a094390.png">

### Environment requirements:
- Python2
- Libraries: python-sqlalchemy, flask, oauth2client, requests, httplib2, redis

### How to run this app:
1. Download this project;
2. Set up a Redis service:
```
redis-server
```
3. Enter into the folder of this project, run
```
python category_seeds.py
python application.py
```
4. Try on the browser:
```
localhost:8000
```
