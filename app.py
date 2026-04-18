from flask import Flask, render_template
from dashboards.sales import create_sales_app
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

server = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static")
)

# Home page
@server.route("/")
def home():
    return render_template("index.html")

# Attach Dash app
create_sales_app(server)

# Required for deployment
app = server