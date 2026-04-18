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
    import os
    return {
        "cwd": os.getcwd(),
        "template_folder": server.template_folder,
        "index_exists": os.path.exists(
            os.path.join(BASE_DIR, "templates", "index.html")
        )
    }

# Attach Dash app
create_sales_app(server)

# Required for deployment
app = server