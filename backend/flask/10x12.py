from flask import Flask, render_template, send_from_directory

app = Flask(__name__)


@app.route('/')
def main():
    return render_template('../website/main.html')


@app.route('/favicon.ico')
def favicon():
    return send_from_directory("./website", "/logo.ico")


if __name__ == '__app__':
    main()
