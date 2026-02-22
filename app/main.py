from flask import Flask

app = Flask(__name__)

@app.get("/")
def home():
    return "Strefa Sport Zdrowie-Na-Stole działa"
