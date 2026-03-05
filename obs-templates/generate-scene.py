#!/usr/bin/env python3
"""
Generate an OBS-compatible scene collection JSON for WadeBot.
Run this to create a scene collection that can be imported into OBS.

Usage:
    python3 generate-scene.py [--overlay-url http://localhost:8888] [--output wadebot-scenes.json]
"""

import json
import uuid
import argparse
import os

def make_uuid():
    return str(uuid.uuid4())

def make_item(name, source_uuid, item_id, x=0, y=0, scale_x=1.0, scale_y=1.0, visible=True):
    return {
        "name": name,
        "source_uuid": source_uuid,
        "visible": visible,
        "locked": False,
        "rot": 0.0,
        "scale_ref": {"x": 1920.0, "y": 1080.0},
        "align": 5,
        "bounds_type": 0,
        "bounds_align": 0,
        "bounds_crop": False,
        "crop_left": 0, "crop_top": 0, "crop_right": 0, "crop_bottom": 0,
        "id": item_id,
        "group_item_backup": False,
        "pos": {"x": x, "y": y},
        "scale": {"x": scale_x, "y": scale_y},
        "bounds": {"x": 0.0, "y": 0.0},
        "scale_filter": "disable",
        "blend_method": "default",
        "blend_type": "normal",
        "show_transition": {"duration": 0},
        "hide_transition": {"duration": 0},
        "private_settings": {}
    }

def generate_scene_collection(overlay_url="http://localhost:8888", name="WadeBot VTuber"):
    # Source UUIDs
    screen_uuid = make_uuid()
    overlay_uuid = make_uuid()
    avatar_uuid = make_uuid()
    audio_uuid = make_uuid()
    stream_scene_uuid = make_uuid()
    chatting_scene_uuid = make_uuid()

    sources = [
        # Stream scene
        {
            "prev_ver": 536870916,
            "name": "Stream",
            "uuid": stream_scene_uuid,
            "id": "scene",
            "versioned_id": "scene",
            "settings": {
                "id_counter": 5,
                "custom_size": False,
                "items": [
                    make_item("Screen Capture", screen_uuid, 1),
                    make_item("VTuber Overlay", overlay_uuid, 2),
                    make_item("Avatar (Veadotube)", avatar_uuid, 3, x=1480, y=580, scale_x=0.5, scale_y=0.5),
                ]
            },
            "mixers": 0,
            "muted": False,
            "private_settings": {}
        },
        # Just Chatting scene
        {
            "prev_ver": 536870916,
            "name": "Just Chatting",
            "uuid": chatting_scene_uuid,
            "id": "scene",
            "versioned_id": "scene",
            "settings": {
                "id_counter": 4,
                "custom_size": False,
                "items": [
                    make_item("Avatar (Veadotube)", avatar_uuid, 1, x=460, y=140, scale_x=1.0, scale_y=1.0),
                    make_item("VTuber Overlay", overlay_uuid, 2),
                ]
            },
            "mixers": 0,
            "muted": False,
            "private_settings": {}
        },
        # Screen capture source
        {
            "prev_ver": 536870916,
            "name": "Screen Capture",
            "uuid": screen_uuid,
            "id": "screen_capture",
            "versioned_id": "screen_capture",
            "settings": {
                "type": 0,
                "show_cursor": True
            },
            "mixers": 0,
            "muted": False,
            "private_settings": {}
        },
        # Browser source for overlay
        {
            "prev_ver": 536870916,
            "name": "VTuber Overlay",
            "uuid": overlay_uuid,
            "id": "browser_source",
            "versioned_id": "browser_source",
            "settings": {
                "url": f"{overlay_url}/multi-overlay.html",
                "width": 1920,
                "height": 1080,
                "fps": 30,
                "shutdown": False,
                "restart_when_active": False,
                "css": "body { background-color: rgba(0, 0, 0, 0); margin: 0px auto; overflow: hidden; }"
            },
            "filters": [
                {
                    "prev_ver": 536870916,
                    "name": "Remove Magenta",
                    "uuid": make_uuid(),
                    "id": "color_key_filter_v2",
                    "versioned_id": "color_key_filter_v2",
                    "settings": {
                        "key_color": 16711935,
                        "key_color_type": "custom",
                        "similarity": 80,
                        "smoothness": 50
                    }
                }
            ],
            "mixers": 0,
            "muted": False,
            "private_settings": {}
        },
        # Window capture for Veadotube
        {
            "prev_ver": 536870916,
            "name": "Avatar (Veadotube)",
            "uuid": avatar_uuid,
            "id": "window_capture",
            "versioned_id": "window_capture",
            "settings": {},
            "filters": [
                {
                    "prev_ver": 536870916,
                    "name": "Remove Green",
                    "uuid": make_uuid(),
                    "id": "color_key_filter_v2",
                    "versioned_id": "color_key_filter_v2",
                    "settings": {
                        "key_color_type": "green",
                        "similarity": 80,
                        "smoothness": 50
                    }
                }
            ],
            "mixers": 0,
            "muted": False,
            "private_settings": {}
        },
        # Audio input for TTS
        {
            "prev_ver": 536870916,
            "name": "TTS Audio (BlackHole)",
            "uuid": audio_uuid,
            "id": "coreaudio_input_capture",
            "versioned_id": "coreaudio_input_capture",
            "settings": {
                "device_id": "BlackHole2ch_UID"
            },
            "mixers": 255,
            "muted": False,
            "private_settings": {}
        }
    ]

    collection = {
        "current_scene": "Stream",
        "current_program_scene": "Stream",
        "scene_order": [
            {"name": "Stream"},
            {"name": "Just Chatting"}
        ],
        "name": name,
        "sources": sources,
        "groups": [],
        "quick_transitions": [],
        "transitions": [],
        "saved_projectors": []
    }

    return collection


def main():
    parser = argparse.ArgumentParser(description="Generate OBS scene collection for WadeBot")
    parser.add_argument("--overlay-url", default="http://localhost:8888", help="Overlay server URL")
    parser.add_argument("--name", default="WadeBot VTuber", help="Scene collection name")
    parser.add_argument("--output", "-o", default=None, help="Output file path")
    args = parser.parse_args()

    collection = generate_scene_collection(args.overlay_url, args.name)

    if args.output:
        output_path = args.output
    else:
        # Default: OBS scene directory
        obs_dir = os.path.expanduser("~/Library/Application Support/obs-studio/basic/scenes")
        if os.path.isdir(obs_dir):
            output_path = os.path.join(obs_dir, f"{args.name}.json")
        else:
            output_path = "wadebot-scenes.json"

    with open(output_path, 'w') as f:
        json.dump(collection, f, indent=4)
    
    print(f"✅ Scene collection written to: {output_path}")
    print(f"   Open OBS → Scene Collection → Import → select '{args.name}'")


if __name__ == "__main__":
    main()
