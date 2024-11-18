from main import app
from flask_socketio import SocketIO
from asgiref.wsgi import WsgiToAsgi

# Wrap Flask app in ASGI compatibility layer
asgi_app = WsgiToAsgi(app)
socketio = SocketIO(app)
