from flask import jsonify, request

from core.roles import PlayerRole


class GameEvents:
    def __init__(self, game, segment_manager, app, socketio):
        self.game = game
        self.segments = segment_manager
        self.app = app
        self.lover_alerts_closed = 0
        self.kill_votes_count = 2
        self.alive_players_count = 0
        self.socketio = socketio
        self.mock_controllers = {}

    def register_handlers(self):

        @self.socketio.on("add_mock_players")
        def handle_add_mock_players(data):
            try:
                mock_players = data.get("players", [])
                controller_sid = data.get("controllerSid")

                if not controller_sid:
                    raise ValueError("Controller SID required")

                # Store the relationship between controller and mock players
                self.mock_controllers[controller_sid] = [p["sid"] for p in mock_players]

                # Add all mock players to the game
                for player_data in mock_players:
                    player = self.game.add_player(
                        name=player_data["name"], sid=player_data["sid"]
                    )

                    # Send player data back to controller
                    self.socketio.emit(
                        "player_data",
                        {"playerId": player.sid, "data": player.to_dict()},
                        to=controller_sid,
                    )

                # Update all clients with new player list
                self.socketio.emit(
                    "update_players_list",
                    [p.to_dict() for p in self.game.players.values()],
                )

                # Start game if enough players
                if len(self.game.players) >= 6:
                    self.game.assign_roles()
                    self.alert_player_for_roles()
                    self.segments.start_night()

            except Exception as e:
                self.socketio.emit("error", {"message": str(e)}, to=request.sid)

        @self.socketio.on("mock_player_action")
        def handle_mock_player_action(data):
            try:
                player_id = data.get("playerId")
                action = data.get("action")
                choice = data.get("choice")
                controller_sid = data.get("controllerSid")

                # Verify this is a valid mock player action
                if not controller_sid in self.mock_controllers:
                    raise ValueError("Invalid controller")
                if not player_id in self.mock_controllers[controller_sid]:
                    raise ValueError("Invalid mock player")

                # Handle the action based on type
                if action == "vote":
                    self.game.set_player_vote(choice)
                elif action == "werewolf_kill":
                    target = self.game.get_player(choice)
                    if target.lover_sid:
                        lover = self.game.get_player(target.lover_sid)
                        if lover:
                            self.game.add_pending_death(lover)
                    self.game.add_pending_death(target)
                elif action == "witch_heal":
                    last_victim = self.game.get_player(self.game.pending_deaths[-1])
                    if last_victim.lover_sid:
                        self.game.remove_pending_death(last_victim.lover_sid)
                    self.game.remove_pending_death(last_victim)
                    self.game.witch_heal_available = False
                elif action == "witch_kill":
                    target = self.game.get_player(choice)
                    if target.lover_sid:
                        lover = self.game.get_player(target.lover_sid)
                        if lover:
                            self.game.add_pending_death(lover)
                    self.game.add_pending_death(target)
                    self.game.witch_kill_available = False

                # Advance game state if needed
                self.segments.advance_segment()

            except Exception as e:
                self.socketio.emit("error", {"message": str(e)}, to=controller_sid)

        @self.app.route("/players", methods=["GET"])
        def get_players():
            try:
                print("Players: ", self.game.players)
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

                # if len(self.game.players) < 5:
                # self.game.add_mock_players(5 - len(self.game.players))

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
                self.segments.advance_segment()

            except Exception as e:
                self.socketio.emit("error", {"message": str(e)}, to=request.sid)

        @self.socketio.on("lover_alert_closed")
        def handle_lover_alert_closed():
            self.lover_alerts_closed += 1
            if self.lover_alerts_closed == 2:
                print("Lover alerts closed")
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
                print("This player will be added to the pending kill list: ", target)

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

        @self.socketio.on("vote_kill")
        def handle_vote_kill(data):
            if self.alive_players_count == 0:
                self.set_alive_players_count()
            self.kill_votes_count += 1
            player_sid = data.get("sid")
            self.game.set_player_vote(player_sid)
            print("Kill votes count is now: ", self.kill_votes_count)
            print("Alive players count is: ", self.alive_players_count)

            if self.kill_votes_count == self.alive_players_count:
                self.segments.count_votes()
            self.segments.reset_current_segment()
            if not self.game.game_over():
                self.segments.reset_current_segment()

    def set_alive_players_count(self):
        self.alive_players_count = len(
            [player for player in self.game.players.values() if player.is_alive]
        )

    def alert_player_for_roles(self):
        for player in self.game.players.values():
            print(player)
            try:
                self.socketio.emit(
                    "role_assigned", {"role": player.role.value}, room=player.sid
                )
            except Exception as e:
                print("Error in socket emit:", str(e))
