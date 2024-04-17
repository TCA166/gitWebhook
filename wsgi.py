from src.webhook import webhookBlueprint
from flask import Flask
import json

app = Flask(__name__)
with open("tokens.json", "r") as f:
    token = json.load(f)["webhookGit"]
wb = webhookBlueprint(token, url_prefix="/")
app.register_blueprint(wb)

if __name__ == "__main__":
    app.run()
