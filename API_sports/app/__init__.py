from flask import Flask, request, jsonify, render_template
import sqlite3
from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__)
from app import views


    
SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name' : "projet"
    }
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
