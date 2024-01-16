import random
import sqlite3
import time
import json

from flask import Flask, render_template, send_from_directory
from flask_socketio import SocketIO, emit, join_room

app = Flask(__name__, template_folder='../website/')
socketio = SocketIO(app, async_mode='eventlet', ping_interval=20)


def connect_to_db():
    conn = None
    try:
        conn = sqlite3.connect('10x12_lite.db')
    except Exception as e:
        print(e)
    return conn


def create_namelist(user_list):
    name_list = []
    conn = connect_to_db()
    cursor = conn.cursor()
    for user_uuid in user_list:
        uuid_part = user_uuid[:8]
        result = cursor.execute("SELECT UserName FROM Users WHERE UserID = ?",
                                (user_uuid,)).fetchone()
        if result:
            name_list.append([result[0], uuid_part])

    conn.commit()
    conn.close()
    return name_list


def get_current_player(room_number):
    conn = connect_to_db()
    cursor = conn.cursor()
    result = cursor.execute("SELECT current_player FROM Sessions WHERE SessionID = ?",
                            (room_number,)).fetchone()
    if result:
        current_player = result[0]
        current_player = current_player[:8]
    else:
        current_player = "nicht gefunden!"

    conn.commit()
    conn.close()
    return current_player

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
    uuid_part = uuid[:8]
    dices = {"dices": {"1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6}}
    dices_default = json.dumps(dices)
    scores = {
        uuid_part: {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "6": 0, "7": 0, "8": 0, "9": 0, "10": 0, "11": 0, "12": 0}}
    scores_start = json.dumps(scores)

    # create room_number (6-digits)
    room_number = random.randrange(100000, 1000000)

    conn = connect_to_db()
    cursor = conn.cursor()

    # check if room_number is already in use
    while cursor.execute("SELECT * FROM Sessions WHERE SessionID = ?", (room_number,)).fetchone() is not None:
        room_number = random.randrange(100000, 1000000)

    # write into database
    cursor.execute(
        "INSERT INTO Sessions (SessionID, Users, last_used, current_player, dices, scores) VALUES (?, ?, DATE('now'), "
        "?, ?, ?)",
        (room_number, uuid, uuid, dices_default, scores_start))
    conn.commit()
    join_room(room_number)  # join websocket room which is room_number / SessionID
    # Socket-Event to Client for forwarding
    emit("to_room", {'room_number': room_number})

    conn.close()


# function on mode.html to check if a user could join a room or not
@socketio.on('join_room')
def check_room(data):
    room_number = data['room_number']
    uuid = data['uuid']
    uuid_part = uuid[:8]

    conn = connect_to_db()
    cursor = conn.cursor()

    if cursor.execute("SELECT * FROM Sessions WHERE SessionID = ?", (room_number,)).fetchone() is not None:
        result = cursor.execute("SELECT Users FROM Sessions WHERE SessionID = ?", (room_number,)).fetchone()
        if result:
            users = result[0]  # result is tuple (uuids,)
            user_list = users.split(",")

            if uuid not in user_list:
                locked = cursor.execute("SELECT locked FROM Sessions WHERE SessionID = ?", (room_number,)).fetchone()
                if locked[0] == 0:  # 0 not locked, 1 locked
                    if len(user_list) < 7:
                        result = cursor.execute("SELECT scores FROM Sessions WHERE SessionID = ?",
                                                (room_number,)).fetchone()
                        if result:
                            scores = result[0]
                            scores_dict = json.loads(scores)  # convert JSON in dict
                            scores_dict[uuid_part] = {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "6": 0, "7": 0, "8": 0,
                                                      "9": 0, "10": 0, "11": 0, "12": 0}
                            updated_scores = json.dumps(scores_dict)  # convert back to JSON

                            cursor.execute(
                                "UPDATE Sessions set Users = Users || ?, last_used = DATE('now'), scores = ? where "
                                "SessionID = ?",
                                ("," + uuid, updated_scores, room_number))
                            conn.commit()

                            join_room(room_number)
                            emit("to_room", {'room_number': room_number})

                            user_list.append(uuid)

                            name_list = create_namelist(user_list)
                            current_player = get_current_player(room_number)
                            time.sleep(3)  # TODO find right way that user with request gets that emit too
                            emit("update_amount_tables", {'names': name_list, 'current_player': current_player}, broadcast=True,
                                 include_self=True, to=room_number)
                    else:
                        emit("error_message", {'message': 'Der Raum ist bereits voll'})
                else:
                    emit("error_message", {'message': 'Der Raum ist gesperrt'})
                    return  # for skipping join room and emit
            else:
                join_room(room_number)
                emit("to_room", {'room_number': room_number})

                name_list = create_namelist(user_list)
                current_player = get_current_player(room_number)
                time.sleep(3)  # TODO find right way that user with request gets that emit too
                emit("update_amount_tables", {'names': name_list, 'current_player': current_player}, broadcast=True,
                     include_self=True, to=room_number)
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
            emit("room_locked",
                 {'message': 'Raum: ' + room_number + ' wurde für andere Spieler gesperrt!'},
                 broadcast=True, include_self=True, to=room_number)
        else:
            emit("room_locked", {}, broadcast=True, include_self=True, to=room_number)
    conn.close()


if __name__ == '__main__':
    # TODO set reloader to False in prod
    socketio.run(app, host='0.0.0.0', port=8080, log_output=False, use_reloader=True)
