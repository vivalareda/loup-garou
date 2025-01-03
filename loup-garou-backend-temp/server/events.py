from flask import jsonify, request

from core.roles import PlayerRole


class GameEvents:
    def __init__(self, game, segment_manager, app, socketio):
        self.game = game
        self.segments = segment_manager
        self.app = app
        self.lover_alerts_closed = 0
        self.socketio = socketio

    def register_handlers(self):

        @self.app.route("/players", methods=["GET"])
        def get_players():
            try:
                return (
                    jsonify(
                        {"players": [p.to_dict() for p in self.game.players.values()]}
                    ),
                    200,
                )
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        @self.app.route("/get_werewolves", methods=["GET"])
        def get_werewolves():
            try:
                werewolves = self.game.get_players_by_role(PlayerRole.WEREWOLF)
                return jsonify({"werewolves": [w.to_dict() for w in werewolves]}), 200
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        # Socket Events
        @self.socketio.on("add_player")
        def handle_add_player(data):
            try:
                if "name" not in data:
                    raise ValueError("Player name required")

                player = self.game.add_player(data["name"], request.sid)

                if len(self.game.players) < 5:
                    self.game.add_mock_players(5 - len(self.game.players))

                try:
                    self.socketio.emit("player_data", player.to_dict(), to=request.sid)
                except Exception as e:
                    print("Error in socket emit:", str(e))
                try:
                    self.socketio.emit(
                        "update_players_list",
                        [p.to_dict() for p in self.game.players.values()],
                        room=None,
                    )
                except Exception as e:
                    print("Error in socket emit:", str(e))

                print("Player in game: ", len(self.game.players))

                if len(self.game.players) == 6:
                    print("Assigning roles")
                    self.game.assign_roles()
                    print("Roles assigned")
                    self.alert_player_for_roles()
                    self.segments.start_night()

            except Exception as e:
                self.socketio.emit("error", {"message": str(e)}, to=request.sid)

        @self.socketio.on("cupidon_selection_complete")
        def handle_cupidon_selection(data):
            try:
                sids = [player["sid"] for player in data]
                player1 = self.game.get_player(sids[0])
                player2 = self.game.get_player(sids[1])

                if not player1 or not player2:
                    raise ValueError("Invalid player selection")

                self.game.set_lovers(player1, player2)
                self.segments.alert_lovers(player1, player2)

            except Exception as e:
                self.socketio.emit("error", {"message": str(e)}, to=request.sid)

        @self.socketio.on("lover_alert_closed")
        def handle_lover_alert_closed():
            self.lover_alerts_closed += 1
            if self.lover_alerts_closed == 2:
                self.segments.advance_segment()

        @self.socketio.on("update_werewolf_selection_count")
        def handle_werewolf_selection(data):
            try:
                werewolves = self.game.get_players_by_role(PlayerRole.WEREWOLF)
                for werewolf in werewolves:
                    self.socketio.emit("new_selection_count", data, to=werewolf.sid)
            except Exception as e:
                self.socketio.emit("error", {"message": str(e)}, to=request.sid)

        @self.socketio.on("werewolf_kill")
        def handle_werewolf_kill(data):
            try:
                target = self.game.get_player(data)
                if not target:
                    raise ValueError("Invalid target player")

                if target.lover_sid:
                    lover = self.game.get_player(target.lover_sid)
                    if lover:
                        self.game.add_pending_death(lover)
                self.game.add_pending_death(target)

                print("Pending deaths: ", self.game.pending_deaths)
                self.segments.advance_segment()

            except Exception as e:
                self.socketio.emit("error", {"message": str(e)}, to=request.sid)

        @self.socketio.on("witch_heal_victim")
        def handle_witch_heal_victim():
            try:
                last_victim = self.game.get_player(self.game.pending_deaths[-1])
                if last_victim.lover_sid:
                    self.game.remove_pending_death(last_victim.lover_sid)
                self.game.remove_pending_death(last_victim)

                self.game.witch_heal_available = False
            except Exception as e:
                self.socketio.emit("error", {"message": str(e)}, to=request.sid)
            self.segments.advance_segment()

        @self.socketio.on("witch_kill_victim")
        def handle_witch_kill_victim(data):
            print(data)

            try:
                target_sid = data["sid"]
                target = self.game.get_player(target_sid)

                if target.lover_sid:
                    lover = self.game.get_player(target.lover_sid)
                    if lover:
                        self.game.add_pending_death(lover)
                self.game.add_pending_death(target)

                self.game.witch_kill_available = False
            except Exception as e:
                print("Can't kill witch victim", e)

            self.segments.advance_segment()

        @self.socketio.on("witch_no_heal")
        def handle_witch_no_heal():
            self.segments.advance_segment()

        @self.socketio.on("witch_no_kill")
        def handle_witch_no_kill():
            self.segments.advance_segment()

    def alert_player_for_roles(self):
        for player in self.game.players.values():
            print(player)
            try:
                self.socketio.emit(
                    "role_assigned", {"role": player.role.value}, room=player.sid
                )
            except Exception as e:
                print("Error in socket emit:", str(e))
