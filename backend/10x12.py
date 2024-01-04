import sqlite3
import random

from flask import Flask, render_template, send_from_directory
from flask_socketio import SocketIO, emit

app = Flask(__name__, template_folder='../website/')
socketio = SocketIO(app, async_mode='eventlet')


def connect_to_db():
    conn = None
    try:
        conn = sqlite3.connect('10x12_lite.db')
    except Exception as e:
        print(e)
    return conn


@app.route('/')
def main():
    return render_template('main.html')


@app.route('/mode.html')
def mode():
    return render_template('mode.html')


@app.route('/game.html')
def game():
    return render_template('game.html')


# TODO check if possible to combine these (until skript.js) in one static folder or something
@app.route('/favicon.ico')
def favicon():
    return send_from_directory("../website", "logo.ico")


@app.route('/Logo_name.png')
def logo():
    return send_from_directory("../website", "Logo_name.png")


@app.route('/js/skript.js')
def js():
    return send_from_directory("../website/js", 'skript.js')


# function on main.html to safe user with uuid
@socketio.on('save_name')
def save_name(data):
    username = data['username']
    uuid = data['uuid']
    if len(uuid) == 36 and len(username) <= 20:
        conn = connect_to_db()
        cursor = conn.cursor()
        if cursor.execute("Select * FROM Users where UserID = ? ", (uuid,)).fetchone() is None:
            cursor.execute("INSERT INTO Users (UserID, UserName, last_used) VALUES (?, ?, DATE('now'))",
                           [uuid, username])
        else:
            cursor.execute("UPDATE Users set UserName = ?, last_used = DATE('now') where UserID = ?",
                           [username, uuid])
        conn.commit()


# function on mode.html to create a room
@socketio.on('create_room')
def create_room(data):
    uuid = data['uuid']

    # Raumnummer generieren (6-stellig)
    room_number = random.randrange(100000, 1000000)

    conn = connect_to_db()
    cursor = conn.cursor()

    # check if room_number is already in use
    while cursor.execute("SELECT * FROM Sessions WHERE SessionID = ?", (room_number,)).fetchone() is not None:
        room_number = random.randrange(100000, 1000000)

    # write into database
    cursor.execute("INSERT INTO Sessions (SessionID, Users, last_used) VALUES (?, ?, DATE('now'))",
                   (room_number, uuid))
    conn.commit()

    # Socket-Event to Client for forwarding
    emit("room_created", {'roomNumber': room_number})


# function on mode.html to check if a user could join a room or not
@app.route('/check_room')
def check_room(room):
    # TODO make database request
    if room == 123456:
        return True  # User should be able to join
    else:
        return False  # User should not be able to join


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8080)
