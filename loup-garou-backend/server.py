# pyright: ignore[type]


import json
import random

from flask import Flask, jsonify, render_template, request
from flask_socketio import SocketIO, emit

from game_state import GameState
from player import Player
from roles import roles

app = Flask(__name__)
socketio = SocketIO(app, cors_allow_origin="*")

players = {}
game_state = GameState(socketio)


def role_assignment(num_players):
    if num_players < 6:
        num_werewolves = 1
    else:
        num_werewolves = 2

    roles_to_assign = (
        ["werewolf"] * num_werewolves
        + ["seer"]
        + ["villager"] * (num_players - num_werewolves - 1)
    )

    random.shuffle(roles_to_assign)
    return roles_to_assign


@socketio.on("add_player")
def handle_add_player(data):
    player_name = data["name"]
    sid = request.sid
    new_player = Player(name=player_name, sid=sid, role=None)
    players[sid] = new_player

    if len(players) == 1:
        mock_names = ["Alice", "Bob", "Charlie", "Eve"]
        for i, name in enumerate(mock_names, start=2):
            mock_sid = str(i)
            players[mock_sid] = Player(name=name, sid=mock_sid)

    print(f"Player joined: {player_name} with SID: {sid}")
    emit("player_data", {"name": new_player.name, "sid": new_player.sid}, room=sid)
    emit("players_update", [str(player) for player in players.values()], broadcast=True)
    print("Number of players:", len(players))
    if len(players) == 6:
        handle_assign_roles()
        game_state.start_game(players)


def handle_assign_roles():
    print("Assigning roles")
    roles_to_assign = role_assignment(len(players))
    print(list(zip(players, roles_to_assign)))
    for player, role in zip(players.values(), roles_to_assign):
        if player.name == "test":
            player.assign_role("cupidon")
            game_state.setCupidonSid(player.sid)
        else:
            player.assign_role(role)
        print(f"The player {player.name} is a {player.role}")
        socketio.emit("role_assigned", {"role": player.role}, to=player.sid)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/players", methods=["GET"])
def get_players():
    all_players = [
        {"name": player.name, "sid": player.sid} for player in players.values()
    ]
    return jsonify({"players": all_players}), 200


@socketio.on("connect")
def handle_connect():
    print("Client connected")


@socketio.on("cupidon_selection")
def handle_cupidon_selection(data):
    print("Cupidon selected:", data)
    sids = [player["sid"] for player in data]
    player_names = {player.sid: player.name for player in players.values()}

    game_state.setCupidonChoice(sids)
    socketio.emit("alert_lovers", {"lover": player_names[sids[1]]}, to=sids[0])
    socketio.emit("alert_lovers", {"lover": player_names[sids[0]]}, to=sids[1])


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5001, debug=True)
