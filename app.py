from connection import getConnection
from flask import Flask, jsonify, render_template, request, url_for, flash, redirect
from flask_mysqldb import MySQL

app = Flask(__name__)
app.secret_key = "mysecretkey"

@app.route("/")
def home():
    try:
        connection = getConnection(1)
        cursor = connection.cursor()
        cursor.execute("Select 1")
        return jsonify({"status": "Ok", "message": "Conectado"}), 200
    except Exception as e:
        return jsonify({"status": "Error", "message": str(e)}), 500
    finally:
        connection.close()

if __name__ == "__main__":
    app.run(port = 3000, debug = True)