from colorama import Fore, Style, init
from flask import jsonify, request
from flask_socketio import SocketIO

from core.game import Game
from core.roles import PlayerRole
from segments.segment_manager import SegmentManager

init()


class GameEvents:
    def __init__(self, game: Game, segment_manager: SegmentManager, app, socketio):
        self.game = game
        self.segments = segment_manager
        self.app = app
        self.lover_alerts_closed = 0
        self.kill_votes_count = 0
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
                self.mock_controllers[controller_sid] = [p["sid"] for p in mock_players]
                for player_data in mock_players:
                    player = self.game.add_player(
                        name=player_data["name"], sid=player_data["sid"]
                    )
                    self.socketio.emit(
                        "player_data",
                        {"playerId": player.sid, "data": player.to_dict()},
                        to=controller_sid,
                    )
                self.socketio.emit(
                    "update_players_list",
                    [p.to_dict() for p in self.game.players.values()],
                )
                if len(self.game.players) >= 6:
                    self.game.assign_roles()
                    self.alert_player_for_roles()
                    self.segments.start_night()
            except Exception as e:
                self.socketio.emit("error", {"message": str(e)}, broadcast=True)

        @self.socketio.on("mock_player_action")
        def handle_mock_player_action(data):
            try:
                player_id = data.get("playerId")
                action = data.get("action")
                choice = data.get("choice")
                controller_sid = data.get("controllerSid")

                if not controller_sid in self.mock_controllers:
                    raise ValueError("Invalid controller")
                if not player_id in self.mock_controllers[controller_sid]:
                    raise ValueError("Invalid mock player")

                if action == "vote":
                    self.game.set_player_vote(choice)
                elif action == "werewolf_kill":
                    target = self.game.get_player(choice)
                    if target and target.lover_sid:
                        lover = self.game.get_player(target.lover_sid)
                        if lover:
                            self.game.add_pending_death(lover)
                    if target is not None:
                        self.game.add_pending_death(target)
                elif action == "witch_heal":
                    last_victim = self.game.get_player(self.game.pending_deaths[-1])
                    if last_victim and last_victim.lover_sid:
                        last_victim_lover = self.game.get_player(last_victim.lover_sid)
                        if last_victim_lover:
                            self.game.remove_pending_death(last_victim_lover)
                    if last_victim:
                        self.game.remove_pending_death(last_victim)
                        self.game.witch_heal_available = False
                elif action == "witch_kill":
                    target = self.game.get_player(choice)
                    if target:
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

        @self.socketio.on("add_player")
        def handle_add_player(data):
            try:
                if "name" not in data:
                    raise ValueError("Player name required")

                player = self.game.add_player(data["name"], request.sid)

                # if len(self.game.players) < 5:
                #     self.game.add_mock_players(5 - len(self.game.players))

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

                if len(self.game.players) >= 6:
                    self.game.assign_roles()
                    self.alert_player_for_roles()
                    self.segments.start_night()

            except Exception as e:
                self.socketio.emit("error", {"message": str(e)}, to=request.sid)

        @self.socketio.on("cupidon_selection_complete")
        def handle_cupidon_selection(data):
            try:
                # sids = [player["sid"] for player in data]
                # player1 = self.game.get_player(sids[0])
                # player2 = self.game.get_player(sids[1])
                #
                # if not player1 or not player2:
                #     raise ValueError("Invalid player selection")
                #
                # self.game.set_lovers(player1, player2)
                self.game.temporary_function()
                self.segments.advance_segment()

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

                self.segments.advance_segment()

            except Exception as e:
                self.socketio.emit("error", {"message": str(e)}, to=request.sid)

        @self.socketio.on("seer_check")
        def handle_seerd_check(data):
            target_player = self.game.get_player(data["sid"])
            if not target_player:
                raise ValueError("Invalid target player")
            self.socketio.emit(
                "role_reveal", {"role": target_player.role.value}, to=request.sid
            )

        @self.socketio.on("hunter_selection")
        def handle_hunter_selection(data):
            target_sid = data["sid"]
            print(
                Fore.RED + "Hunter decided to kill : ",
                target_sid,
                "!!!",
                Style.RESET_ALL,
            )
            self.game.kill_player(target_sid)
            self.segments.count_votes()

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

        @self.socketio.on("vote_kill")
        def handle_vote_kill(data):
            if self.alive_players_count == 0:
                self.set_alive_players_count()
            self.kill_votes_count += 1
            player_sid = data.get("sid")
            self.game.set_player_vote(player_sid)

            print("Kill votes count: ", self.kill_votes_count)
            print("Alive players count: ", self.alive_players_count)

            if self.kill_votes_count == self.alive_players_count:
                self.reset_counters()
                self.segments.count_votes()
                self.segments.check_game_over()

    def reset_counters(self):
        self.kill_votes_count = 0
        self.alive_players_count = 0

    def set_alive_players_count(self):
        self.alive_players_count = (
            self.game.werewolves_alive + self.game.villagers_alive
        )

    def alert_player_for_roles(self):
        for player in self.game.players.values():
            try:
                self.socketio.emit(
                    "role_assigned", {"role": player.role.value}, room=player.sid
                )
            except Exception as e:
                print("Error in socket emit:", str(e))
