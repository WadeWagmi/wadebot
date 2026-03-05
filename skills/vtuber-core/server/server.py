#!/usr/bin/env python3
"""
wadebot overlay server — WebSocket-based real-time multi-agent streaming overlay.

Serves the overlay HTML and handles real-time message routing between agents.
Replaces the polling-based approach (thought.json) with instant WebSocket delivery.

Usage:
    python3 server.py [--port 8888] [--host 0.0.0.0]

API:
    POST /say     — Agent sends a message (speech or thought)
    GET  /agents  — List connected agents and their colors
    GET  /health  — Health check
    WS   /ws      — WebSocket for real-time overlay updates

POST /say body:
    {"agent": "Wade", "text": "Hello world", "type": "speech"}
    type: "speech" (TTS + overlay) or "thought" (overlay only)
"""

import asyncio
import json
import time
import os
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import threading
import signal

# Try websockets, fall back to polling mode
try:
    import websockets
    HAS_WEBSOCKETS = True
except ImportError:
    HAS_WEBSOCKETS = False

# ── Configuration ──
PORT = int(os.environ.get('PORT', os.environ.get('WADEBOT_PORT', 8888)))
HOST = os.environ.get('WADEBOT_HOST', '0.0.0.0')
OVERLAY_DIR = Path(__file__).parent.parent / 'overlay'
MAX_MESSAGES = 50

# ── State ──
messages = []
connected_clients = set()
agent_colors = {}
color_palette = ['#22c55e', '#6366f1', '#f59e0b', '#ec4899', '#06b6d4']
chat_color = '#94a3b8'  # Muted color for chat messages
next_color = 0
active_speaker = None  # Current agent with the floor
chat_messages = []  # Recent chat messages for agent context


def assign_color(agent):
    global next_color
    if agent not in agent_colors:
        agent_colors[agent] = color_palette[next_color % len(color_palette)]
        next_color += 1
    return agent_colors[agent]


def add_message(agent, text, msg_type='speech'):
    """Add a message and broadcast to all connected clients."""
    if agent.startswith('chat:'):
        color = chat_color
    else:
        color = assign_color(agent)
    msg = {
        'agent': agent,
        'text': text,
        'type': msg_type,
        'color': color,
        'timestamp': int(time.time() * 1000),
    }
    messages.append(msg)
    if len(messages) > MAX_MESSAGES:
        messages.pop(0)
    
    # Write to messages.json for polling fallback
    try:
        messages_file = OVERLAY_DIR / 'messages.json'
        with open(messages_file, 'w') as f:
            json.dump({'messages': messages[-20:]}, f)
    except Exception:
        pass
    
    # Also write thought.json for legacy compat
    try:
        thought_file = OVERLAY_DIR / 'thought.json'
        with open(thought_file, 'w') as f:
            json.dump(msg, f)
    except Exception:
        pass
    
    return msg


class OverlayHTTPHandler(SimpleHTTPRequestHandler):
    """Serves overlay files + REST API for agent messages."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(OVERLAY_DIR), **kwargs)
    
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        
        if self.path == '/say':
            try:
                data = json.loads(body)
                agent = data.get('agent', 'Agent')
                text = data.get('text', '')
                msg_type = data.get('type', 'speech')
                
                if not text.strip():
                    self._json_response(400, {'error': 'text is required'})
                    return
                
                msg = add_message(agent, text, msg_type)
                
                # Broadcast via WebSocket if available
                if HAS_WEBSOCKETS and connected_clients:
                    asyncio.run_coroutine_threadsafe(
                        broadcast(json.dumps(msg)),
                        ws_loop
                    )
                
                self._json_response(200, msg)
                print(f"  [{agent}] ({msg_type}) {text}")
                
            except json.JSONDecodeError:
                self._json_response(400, {'error': 'invalid JSON'})
        
        elif self.path == '/handoff':
            try:
                global active_speaker
                data = json.loads(body)
                from_agent = data.get('from', '')
                to_agent = data.get('to', '')
                reason = data.get('reason', '')
                
                if not to_agent:
                    self._json_response(400, {'error': 'to is required'})
                    return
                
                prev_speaker = active_speaker
                active_speaker = to_agent
                assign_color(to_agent)
                
                handoff_event = {
                    'type': 'handoff',
                    'from': from_agent,
                    'to': to_agent,
                    'reason': reason,
                    'activeSpeaker': active_speaker,
                    'timestamp': int(time.time() * 1000),
                }
                
                # Add system message to overlay
                handoff_text = f"🎤 {to_agent} has the floor"
                if from_agent:
                    handoff_text = f"🎤 {from_agent} → {to_agent}"
                if reason:
                    handoff_text += f" ({reason})"
                
                msg = add_message('system', handoff_text, 'handoff')
                
                # Broadcast handoff event via WebSocket
                if HAS_WEBSOCKETS and connected_clients:
                    asyncio.run_coroutine_threadsafe(
                        broadcast(json.dumps(handoff_event)),
                        ws_loop
                    )
                
                self._json_response(200, {
                    'ok': True,
                    'activeSpeaker': active_speaker,
                    'previousSpeaker': prev_speaker,
                })
                print(f"  🎤 Handoff: {from_agent or '(none)'} → {to_agent}" + (f" ({reason})" if reason else ""))
                
            except json.JSONDecodeError:
                self._json_response(400, {'error': 'invalid JSON'})
        
        else:
            self._json_response(404, {'error': 'not found'})
    
    def do_GET(self):
        if self.path == '/agents':
            self._json_response(200, {
                'agents': agent_colors,
                'messageCount': len(messages),
            })
        elif self.path.startswith('/chat'):
            # Return recent chat messages for agents to read and respond to
            limit = 20
            try:
                if '?' in self.path:
                    params = dict(p.split('=') for p in self.path.split('?')[1].split('&') if '=' in p)
                    limit = int(params.get('limit', 20))
            except (ValueError, IndexError):
                pass
            chat_msgs = [m for m in messages if m.get('type') == 'chat'][-limit:]
            self._json_response(200, {
                'chat': chat_msgs,
                'count': len(chat_msgs),
            })
        elif self.path == '/health':
            self._json_response(200, {
                'status': 'ok',
                'websockets': HAS_WEBSOCKETS,
                'clients': len(connected_clients),
                'agents': list(agent_colors.keys()),
                'activeSpeaker': active_speaker,
                'messages': len(messages),
            })
        elif self.path == '/messages':
            self._json_response(200, {'messages': messages[-20:]})
        else:
            super().do_GET()
    
    def _json_response(self, status, data):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def log_message(self, format, *args):
        # Suppress default logging for cleaner output
        pass


# ── WebSocket server (if websockets available) ──
ws_loop = None

async def broadcast(message):
    """Send message to all connected WebSocket clients."""
    if connected_clients:
        await asyncio.gather(
            *[client.send(message) for client in connected_clients],
            return_exceptions=True
        )

async def ws_handler(websocket):
    """Handle a WebSocket connection."""
    connected_clients.add(websocket)
    print(f"  🔌 Overlay client connected ({len(connected_clients)} total)")
    try:
        # Send recent messages on connect
        for msg in messages[-10:]:
            await websocket.send(json.dumps(msg))
        
        # Keep connection alive, handle incoming messages
        async for raw in websocket:
            try:
                data = json.loads(raw)
                if 'text' in data:
                    msg = add_message(
                        data.get('agent', 'Agent'),
                        data['text'],
                        data.get('type', 'speech')
                    )
                    await broadcast(json.dumps(msg))
            except json.JSONDecodeError:
                pass
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        connected_clients.discard(websocket)
        print(f"  🔌 Overlay client disconnected ({len(connected_clients)} total)")

async def start_ws_server():
    """Start the WebSocket server."""
    global ws_loop
    ws_loop = asyncio.get_event_loop()
    ws_port = PORT + 1  # WebSocket on port+1
    server = await websockets.serve(ws_handler, HOST, ws_port)
    print(f"  📡 WebSocket server on ws://{HOST}:{ws_port}/ws")
    await server.wait_closed()


def main():
    print(f"""
╔══════════════════════════════════════════╗
║         wadebot overlay server           ║
╠══════════════════════════════════════════╣
║  HTTP:  http://{HOST}:{PORT}         ║
║  Overlay: /multi-overlay.html            ║
║  API:   POST /say  GET /agents /health   ║""")
    
    if HAS_WEBSOCKETS:
        print(f"║  WS:   ws://{HOST}:{PORT + 1}              ║")
    else:
        print(f"║  WS:   unavailable (pip install websockets)║")
    
    print(f"""╚══════════════════════════════════════════╝
""")
    
    # Start HTTP server
    httpd = HTTPServer((HOST, PORT), OverlayHTTPHandler)
    http_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    http_thread.start()
    print(f"  🌐 HTTP server on http://{HOST}:{PORT}")
    
    # Start WebSocket server if available
    if HAS_WEBSOCKETS:
        ws_thread = threading.Thread(
            target=lambda: asyncio.run(start_ws_server()),
            daemon=True
        )
        ws_thread.start()
    
    # Handle shutdown
    def shutdown(sig, frame):
        print("\n  Shutting down...")
        httpd.shutdown()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)
    
    print(f"  ✅ Ready. Agents can POST to http://{HOST}:{PORT}/say")
    print()
    
    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        shutdown(None, None)


if __name__ == '__main__':
    main()
