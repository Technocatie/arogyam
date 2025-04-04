from flask import *
app = Flask(__name__)

@app.route("/")
def index():
    return render_template("home.html")
@app.route("/conclusion")
def con():
    return render_template("conclusion.html")
@app.route("/features")
def features():
    return render_template("features.html")

@app.route("/model")
def model():
    return render_template("index.html")

if __name__ == '__main__':
    app.run(debug=True)
