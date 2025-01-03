from flask import Flask
from flask_socketio import SocketIO

from core.game import Game
from segments.segment_manager import SegmentManager

from .events import GameEvents


def create_app():
    app = Flask(__name__)
    socketio = SocketIO(app, cors_allowed_origins="*")

    game = Game()
    segment_manager = SegmentManager(game, socketio)
    events = GameEvents(game, segment_manager, app, socketio)
    events.register_handlers()

    return app, socketio
