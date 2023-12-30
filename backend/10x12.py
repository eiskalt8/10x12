from flask import Flask, render_template, send_from_directory, request
from flask_socketio import SocketIO, emit
import sqlite3
import subprocess

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


# function on main.html to safe user with uuid
@socketio.on('save_name')
def save_name(username, uuid):
    if uuid.length == 36 and username.length <= 20:
        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Users (UserID, UserName) VALUES (?, ?)", [uuid, username])
        conn.commit()


# function on mode.html to check if a user could join a room or not
@app.route('/check_room')
def check_room(room):
    # TODO make database request
    if room == 123456:
        return True  # User should be able to join
    else:
        return False  # User should not be able to join


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


# @socketio.on('my_event')
# def checkping():
#    for x in range(5):
#        cmd = 'ping -c 1 8.8.8.8|head -2|tail -1'
#        listing1 = subprocess.run(cmd,stdout=subprocess.PIPE,text=True,shell=True)
#        sid = request.sid
#        emit('server', {"data1":x, "data":listing1.stdout}, room=sid)
#        socketio.sleep(1)


if __name__ == '__main__':
    app.run(debug=True)
    socketio.run(app)
