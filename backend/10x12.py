import json
import random
import sqlite3
import time

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
    if result and len(result[0]) == 36:
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
                            time.sleep(1.5)  # TODO find right way that user with request gets that emit too
                            emit("update_amount_tables", {'names': name_list, 'current_player': current_player},
                                 broadcast=True, include_self=True, to=room_number)
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
                time.sleep(1.5)  # TODO find right way that user with request gets that emit too
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
                 {'message': 'Raum: ' + room_number + ' wurde für andere Spieler gesperrt!'}, broadcast=True,
                 include_self=True, to=room_number)
        else:
            emit("room_locked", {}, broadcast=True, include_self=True, to=room_number)
    conn.close()


@socketio.on('next_player')
def next_player(data):
    room_number = data['room_number']
    uuid = data['uuid']

    conn = connect_to_db()
    cursor = conn.cursor()

    if cursor.execute("SELECT * FROM Sessions WHERE SessionID = ?", (room_number,)).fetchone() is not None:
        result = cursor.execute("Select Users, current_player FROM Sessions WHERE SessionID = ?",
                                (room_number,)).fetchone()
        if result:
            user = result[0]
            user_list = user.split(",")
            current_player = result[1]
            if uuid == current_player:
                index = user_list.index(current_player)
                if index == len(user_list) - 1:
                    next_player_index = 0
                else:
                    next_player_index = index + 1
                next_player_uuid = user_list[next_player_index]
                cursor.execute("UPDATE Sessions SET last_used = DATE('now'), current_player = ? WHERE SessionID = ?",
                               (next_player_uuid, room_number))
                conn.commit()
                current_player = next_player_uuid[:8]
                user_list.remove(next_player_uuid)
                userlist = [user[:8] for user in user_list]

                emit("new_next_player", {'current_player': current_player, 'userlist': userlist}, broadcast=True,
                     include_self=True,
                     to=room_number)
            else:
                return False  # requester is not current_player and therefore can not end turn
    conn.close()


@socketio.on('dices')
def player_dices(data):
    room_number = data['room_number']
    uuid = data['uuid']
    new_dices = data['dices']
    locked_dices = data['locked_dices']

    conn = connect_to_db()
    cursor = conn.cursor()

    if cursor.execute("SELECT * FROM Sessions WHERE SessionID = ?", (room_number,)).fetchone() is not None:
        result = cursor.execute("Select dices FROM Sessions WHERE SessionID = ?",
                                (room_number,)).fetchone()
        if result:
            dices = result[0]
            dices_dict = json.loads(dices)['dices']
            if new_dices and locked_dices is not False:  # for only get current dices at reload (dices is false)
                # is current user and allow to change?
                result = cursor.execute("Select current_player FROM Sessions WHERE SessionID = ?",
                                        (room_number,)).fetchone()
                if result and uuid == result[0]:
                    dices_dict.update(new_dices)

                    cursor.execute("UPDATE Sessions SET dices = ? WHERE SessionID = ?",
                                   (json.dumps({'dices': dices_dict}), room_number))
                    conn.commit()
                    # TODO also emit locked status for other players
                    emit('new_dices', {'new_dices': dices_dict, 'locked_dices': locked_dices}, broadcast=True,
                         include_self=False, to=room_number)
            else:
                emit('new_dices', {'new_dices': dices_dict})

    conn.close()


@socketio.on('new_score')
def new_score(data):
    room_number = data['room_number']
    uuid = data['uuid']
    score = data['score']
    uuid_part = uuid[:8]

    conn = connect_to_db()
    cursor = conn.cursor()

    if cursor.execute("SELECT * FROM Sessions WHERE SessionID = ?", (room_number,)).fetchone() is not None:
        result = cursor.execute("Select scores FROM Sessions WHERE SessionID = ?", (room_number,)).fetchone()
        if result:
            old_scores = json.loads(result[0])
            if score is not False:
                result = cursor.execute("Select current_player FROM Sessions WHERE SessionID = ?",
                                        (room_number,)).fetchone()
                if result and uuid == result[0]:
                    player_score = old_scores.get(uuid_part, {})
                    player_score.update(score)
                    old_scores[uuid_part] = player_score

                    cursor.execute("Update Sessions set scores = ? where SessionID = ?",
                                   (json.dumps(old_scores), room_number))
                    conn.commit()

                    emit("new_scores", {'new_scores': json.dumps(old_scores)}, broadcast=True, include_self=True,
                         to=room_number)
            else:
                emit("new_scores", {'new_scores': json.dumps(old_scores)})
    conn.close()


if __name__ == '__main__':
    # TODO set reloader to False in prod
    socketio.run(app, host='0.0.0.0', port=8080, log_output=False, use_reloader=True)
