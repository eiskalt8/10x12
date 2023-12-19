from flask import Flask, render_template, send_from_directory

app = Flask(__name__, template_folder='../website/')


@app.route('/')
def main():
    return render_template('main.html')


@app.route('/mode.html')
def mode():
    return render_template('mode.html')


@app.route('/game.html')
def game():
    return render_template('game.html')


# function on mode.html to check if a user could join a room or not
@app.route('/check_room')
def check_room(room):
    # TODO make database request
    if room == 123456:
        return True  # User should be able to join
    else:
        return False  # User should not be able to join


#TODO check if possible to combine these (until 44) in one static folder or something
@app.route('/favicon.ico')
def favicon():
    return send_from_directory("../website", "logo.ico")


@app.route('/Logo_name.png')
def logo():
    return send_from_directory("../website", "Logo_name.png")


@app.route('/js/skript.js')
def js():
    return send_from_directory("../website/js", 'skript.js')

if __name__ == '__main__':
    app.run(debug=True)
