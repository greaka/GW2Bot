from flask import Flask, redirect

from .auth.botauthentication import auth

app = Flask(__name__)

app.register_blueprint(auth)


@app.route("/")
def website():
    return redirect("https://gw2bot.info")


if __name__ == 'cogs.guildwars2.web':
    app.run('0.0.0.0', 80)