import random
import sqlite3

from flask import Flask, render_template, send_from_directory
from flask_socketio import SocketIO, emit, rooms, join_room, leave_room

app = Flask(__name__, template_folder='../website/')
socketio = SocketIO(app, async_mode='eventlet', ping_interval=20, ping_timeout=60)  # timeout from sockets in sec


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


@app.route('/game/<int:room_number>')
def game(room_number):
    return render_template('game.html', room_number=room_number)


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
        cursor.close()


# function on mode.html to create a room
@socketio.on('create_room')
def create_room(data):
    uuid = data['uuid']

    # create room_number (6-digits)
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
    join_room(room_number)  # join websocket room which is SessionID
    # Socket-Event to Client for forwarding
    emit("to_room", {'room_number': room_number})

    conn.close()


# function on mode.html to check if a user could join a room or not
@socketio.on('join_room')
def check_room(data):
    room_number = data['room_number']
    uuid = data['uuid']

    conn = connect_to_db()
    cursor = conn.cursor()

    if cursor.execute("SELECT * FROM Sessions WHERE SessionID = ?", (room_number,)).fetchone() is not None:
        result = cursor.execute("SELECT Users FROM Sessions WHERE SessionID = ?", (room_number,)).fetchone()
        if result:
            users = result[0]  # result is tupel (uuids,)
            user_list = users.split(",")

            if uuid not in user_list:
                locked = cursor.execute("SELECT locked FROM Sessions WHERE SessionID = ?", (room_number,)).fetchone()
                if locked[0] == 0:  # 0 not locked 1 locked
                    uuids = "," + uuid  # add user uuid to uuid list
                    cursor.execute(
                        "UPDATE Sessions set Users = Users || ?, last_used = DATE('now') where SessionID = ?",
                        [uuids, room_number])
                    conn.commit()
                    join_room(room_number)  # join websocket room which is SessionID
                    emit("to_room", {'room_number': room_number})

                    # TODO create numplayers and userlist
                    numplayers = 4
                    user_list = ["Ben, Kevin, Horst, Mike"]
                    emit("update_amount_tables", {'numPlayers': numplayers, 'users': user_list}, broadcast=True,
                         include_self=True, to=room_number)

                else:
                    emit("error_message", {'message': 'Der Raum ist gesperrt'})
                    return
            else:
                emit("to_room", {'room_number': room_number})
    else:
        emit("error_message", {'message': 'Der Raum existiert nicht'})
    conn.close()


@socketio.on('lock_room')
def lock_room(data):
    room_number = data['room_number']

    conn = connect_to_db()
    cursor = conn.cursor()

    if cursor.execute("SELECT * FROM Sessions WHERE SessionID = ?", (room_number,)).fetchone() is not None:
        locked = cursor.execute("SELECT locked FROM Sessions WHERE SessionID = ?", (room_number,)).fetchone()
        if locked[0] == 0:
            cursor.execute("UPDATE Sessions SET locked = 1, last_used = DATE('now') WHERE SessionID = ?",
                           (room_number,))
            conn.commit()
            emit("room_locked", {'message': 'Raum: ' + room_number + ' wurde für andere Spieler gesperrt!'},
                 broadcast=True, include_self=True, to=room_number)
    conn.close()


@socketio.on('join_webroom')
def handle_join_room(data):
    room_number = data['room_number']
    join_room(room_number)
    emit('room_joined', {'room': room_number}, room=room_number)


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8080)
