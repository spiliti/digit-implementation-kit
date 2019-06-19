from flask import Flask

app = Flask(__name__)

@app.route("/upload/boundary")
def boundary_update():
    return "Updated"


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=9090)