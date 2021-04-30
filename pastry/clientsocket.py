#import flask
from flask import Flask, render_template, request
import socket
app = Flask(__name__)


@app.route('/', methods=["GET", "POST"])
def add_key():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("127.0.0.1", 8080))
    key = request.form.get('key')
    value = request.form.get('value')
    print(key)
    message = "insert|" + str(key) + ":" + str(value)
    sock.send(message.encode('utf-8'))
    data = sock.recv(1024)
    data = str(data.decode('utf-8'))
    return render_template("add.html")


@app.route('/search', methods=["GET", "POST"])
def search_key():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('8.8.8.8', 8080))
    key = request.form.get("search_key")
    message = "search|" + str(key)
    sock.send(message.encode('utf-8'))
    data = sock.recv(1024)
    data = str(data.decode('utf-8'))
    return render_template("search.html", data=data)


@app.route('/delete', methods=["GET", "POST"])
def delete_key():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("127.0.0.1", 8080))
    key = request.form.get("delete_key")
    message = "delete|" + str(key)
    sock.send(message.encode('utf-8'))
    data = sock.recv(1024)
    data = str(data.decode('utf-8'))
    return render_template("delete.html")
    return "<p> Data Deleted Successfully </p>"


if __name__ == '__main__':
    app.run(debug=True)
