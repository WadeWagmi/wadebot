#!/usr/bin/env python3
"""
wadebot chat bridge — reads Twitch/YouTube chat and posts to the overlay.

Connects to Twitch IRC (anonymous, no auth needed for reading) and forwards
chat messages to the wadebot overlay server via POST /say. Agents can then
respond to chat through the normal /say endpoint.

Usage:
    python3 chat-bridge.py --channel <twitch_channel> [--server http://localhost:8888]

    # YouTube (uses yt-dlp to scrape live chat):
    python3 chat-bridge.py --youtube <video_url> [--server http://localhost:8888]

Environment:
    TWITCH_CHANNEL  — Twitch channel to join (alternative to --channel)
    WADEBOT_SERVER  — Overlay server URL (default: http://localhost:8888)
    TWITCH_TOKEN    — OAuth token for authenticated features (optional)
    TWITCH_NICK     — Bot nickname for sending messages (optional)
"""

import argparse
import json
import os
import re
import socket
import sys
import threading
import time
import urllib.request
import subprocess
from collections import deque

# ── Config ──
TWITCH_IRC_HOST = "irc.chat.twitch.tv"
TWITCH_IRC_PORT = 6667
DEFAULT_SERVER = "http://localhost:8888"
RECONNECT_DELAY = 5
MAX_RECENT = 50  # Track recent messages to avoid duplicates

# ── State ──
recent_messages = deque(maxlen=MAX_RECENT)
running = True


def post_to_overlay(server_url, agent, text, msg_type="speech"):
    """Post a message to the wadebot overlay server."""
    url = f"{server_url}/say"
    data = json.dumps({
        "agent": agent,
        "text": text,
        "type": msg_type,
    }).encode()
    
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status == 200
    except Exception as e:
        print(f"  ⚠️  Failed to post to overlay: {e}")
        return False


def post_chat_message(server_url, username, text):
    """Post a chat message to the overlay as a chat-type message."""
    url = f"{server_url}/say"
    data = json.dumps({
        "agent": f"chat:{username}",
        "text": text,
        "type": "chat",
    }).encode()
    
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status == 200
    except Exception as e:
        print(f"  ⚠️  Failed to post chat: {e}")
        return False


# ── Twitch IRC ──

class TwitchChat:
    """Anonymous Twitch IRC reader (no auth needed for reading)."""
    
    def __init__(self, channel, server_url, nick=None, token=None):
        self.channel = channel.lower().lstrip("#")
        self.server_url = server_url
        self.nick = nick or f"justinfan{int(time.time()) % 99999}"  # Anonymous
        self.token = token
        self.sock = None
    
    def connect(self):
        """Connect to Twitch IRC."""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(300)  # 5 min timeout for PING/PONG
        self.sock.connect((TWITCH_IRC_HOST, TWITCH_IRC_PORT))
        
        if self.token:
            self.sock.send(f"PASS oauth:{self.token}\r\n".encode())
        self.sock.send(f"NICK {self.nick}\r\n".encode())
        self.sock.send(f"JOIN #{self.channel}\r\n".encode())
        
        # Request tags for badges, emotes, etc.
        self.sock.send(b"CAP REQ :twitch.tv/tags\r\n")
        self.sock.send(b"CAP REQ :twitch.tv/commands\r\n")
        
        print(f"  📺 Connected to #{self.channel} as {self.nick}")
    
    def run(self):
        """Main loop — read IRC messages and forward to overlay."""
        global running
        
        while running:
            try:
                self.connect()
                buffer = ""
                
                while running:
                    try:
                        data = self.sock.recv(4096).decode("utf-8", errors="replace")
                    except socket.timeout:
                        # Send PING to keep alive
                        self.sock.send(b"PING :tmi.twitch.tv\r\n")
                        continue
                    
                    if not data:
                        print("  ⚠️  Disconnected from Twitch IRC")
                        break
                    
                    buffer += data
                    lines = buffer.split("\r\n")
                    buffer = lines.pop()  # Incomplete line stays in buffer
                    
                    for line in lines:
                        self._handle_line(line)
                        
            except Exception as e:
                print(f"  ❌ Twitch IRC error: {e}")
            
            if running:
                print(f"  🔄 Reconnecting in {RECONNECT_DELAY}s...")
                time.sleep(RECONNECT_DELAY)
    
    def _handle_line(self, line):
        """Parse an IRC line and forward chat messages."""
        # Handle PING
        if line.startswith("PING"):
            self.sock.send(b"PONG :tmi.twitch.tv\r\n")
            return
        
        # Parse PRIVMSG (chat messages)
        # Format: @tags :user!user@user.tmi.twitch.tv PRIVMSG #channel :message
        privmsg_match = re.search(
            r":(\w+)!\w+@\w+\.tmi\.twitch\.tv PRIVMSG #\w+ :(.+)",
            line
        )
        if privmsg_match:
            username = privmsg_match.group(1)
            message = privmsg_match.group(2).strip()
            
            # Skip bot's own messages
            if username.lower() == self.nick.lower():
                return
            
            # Dedup
            msg_key = f"{username}:{message}"
            if msg_key in recent_messages:
                return
            recent_messages.append(msg_key)
            
            print(f"  💬 {username}: {message}")
            post_chat_message(self.server_url, username, message)


# ── YouTube Live Chat (via yt-dlp) ──

class YouTubeChat:
    """YouTube live chat reader using yt-dlp."""
    
    def __init__(self, video_url, server_url):
        self.video_url = video_url
        self.server_url = server_url
    
    def run(self):
        """Read YouTube live chat via yt-dlp."""
        global running
        
        print(f"  📺 Connecting to YouTube live chat: {self.video_url}")
        
        while running:
            try:
                proc = subprocess.Popen(
                    [
                        "yt-dlp",
                        "--skip-download",
                        "--write-sub",
                        "--sub-lang", "live_chat",
                        "--sub-format", "json",
                        "-o", "-",
                        self.video_url,
                    ],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
                
                for line in proc.stdout:
                    if not running:
                        break
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                        # Extract chat message from yt-dlp JSON
                        actions = data.get("replayChatItemAction", {}).get("actions", [])
                        for action in actions:
                            item = action.get("addChatItemAction", {}).get("item", {})
                            renderer = item.get("liveChatTextMessageRenderer", {})
                            if renderer:
                                author = renderer.get("authorName", {}).get("simpleText", "Unknown")
                                runs = renderer.get("message", {}).get("runs", [])
                                message = "".join(r.get("text", "") for r in runs)
                                if message:
                                    msg_key = f"{author}:{message}"
                                    if msg_key not in recent_messages:
                                        recent_messages.append(msg_key)
                                        print(f"  💬 {author}: {message}")
                                        post_chat_message(self.server_url, author, message)
                    except json.JSONDecodeError:
                        pass
                
                proc.wait()
                
            except FileNotFoundError:
                print("  ❌ yt-dlp not found. Install: pip install yt-dlp")
                return
            except Exception as e:
                print(f"  ❌ YouTube chat error: {e}")
            
            if running:
                print(f"  🔄 Reconnecting in {RECONNECT_DELAY}s...")
                time.sleep(RECONNECT_DELAY)


def main():
    global running
    
    parser = argparse.ArgumentParser(description="wadebot chat bridge")
    parser.add_argument("--channel", "-c", help="Twitch channel name")
    parser.add_argument("--youtube", "-y", help="YouTube live video URL")
    parser.add_argument("--server", "-s", default=DEFAULT_SERVER, help="Overlay server URL")
    args = parser.parse_args()
    
    server_url = args.server or os.environ.get("WADEBOT_SERVER", DEFAULT_SERVER)
    
    # Check overlay server is reachable
    try:
        req = urllib.request.Request(f"{server_url}/health")
        with urllib.request.urlopen(req, timeout=5) as resp:
            health = json.loads(resp.read())
            print(f"  ✅ Overlay server: {health.get('agents', [])} agent(s), {health.get('messages', 0)} messages")
    except Exception as e:
        print(f"  ⚠️  Overlay server not reachable at {server_url}: {e}")
        print(f"      Chat will still be captured and posted when server comes up.")
    
    # Determine source
    channel = args.channel or os.environ.get("TWITCH_CHANNEL")
    youtube = args.youtube
    
    if not channel and not youtube:
        print("Usage: chat-bridge.py --channel <twitch_channel>")
        print("       chat-bridge.py --youtube <video_url>")
        print("   or: TWITCH_CHANNEL=<channel> chat-bridge.py")
        sys.exit(1)
    
    print(f"""
╔══════════════════════════════════════════╗
║         wadebot chat bridge              ║
╠══════════════════════════════════════════╣
║  Source: {"Twitch #" + channel if channel else "YouTube"}
║  Server: {server_url}
╚══════════════════════════════════════════╝
""")
    
    try:
        if channel:
            nick = os.environ.get("TWITCH_NICK")
            token = os.environ.get("TWITCH_TOKEN")
            client = TwitchChat(channel, server_url, nick, token)
            client.run()
        elif youtube:
            client = YouTubeChat(youtube, server_url)
            client.run()
    except KeyboardInterrupt:
        print("\n  Shutting down chat bridge...")
        running = False


if __name__ == "__main__":
    main()
