from flask import Flask, render_template
from dashboards.sales import create_sales_app

server = Flask(__name__)

# Home page
@server.route("/")
def home():
    return render_template("index.html")

# Attach Dash app
create_sales_app(server)

# Required for deployment
app = server