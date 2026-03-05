#!/usr/bin/env python3
"""
Generate VTuber avatar PNGs for wadebot using image generation.

Creates idle + talking states based on the agent's personality.
Falls back to pre-made templates if no image generation is available.

Usage:
    python3 generate-avatar.py --name "Wade" --vibe "chaotic" --style "cyberpunk"
    python3 generate-avatar.py --template robot

Environment:
    REPLICATE_API_TOKEN — for Replicate-based generation
    OPENAI_API_KEY — for DALL-E generation (fallback)
"""

import argparse
import json
import os
import sys
import shutil
import urllib.request
from pathlib import Path

AVATAR_DIR = Path(os.environ.get("WADEBOT_AVATARS", Path.home() / ".wadebot" / "avatars"))
TEMPLATE_DIR = Path(__file__).parent.parent / "avatars" / "templates"

# Pre-made template descriptions (for when no image gen is available)
TEMPLATES = {
    "robot": "🤖 Clean techy robot",
    "cat": "🐱 Cute expressive cat",
    "gamer": "🎮 Hoodie & headphones gamer",
    "pixel": "👾 Retro 8-bit pixel art",
    "abstract": "🎭 Geometric abstract shapes",
}


def generate_with_replicate(name, vibe, style, output_dir):
    """Generate avatar using Replicate API."""
    try:
        import replicate
    except ImportError:
        print("  ⚠️  replicate package not installed. pip install replicate")
        return False

    token = os.environ.get("REPLICATE_API_TOKEN")
    if not token:
        print("  ⚠️  REPLICATE_API_TOKEN not set")
        return False

    base_prompt = f"VTuber avatar character named {name}, {vibe} personality, {style} style, clean lines, expressive face, transparent background, digital art, high quality"

    states = {
        "idle": f"{base_prompt}, neutral relaxed expression, calm pose",
        "talking": f"{base_prompt}, mouth open speaking, animated energetic pose",
    }

    output_dir.mkdir(parents=True, exist_ok=True)

    for state_name, prompt in states.items():
        print(f"  🎨 Generating {state_name} avatar...")
        try:
            output = replicate.run(
                "black-forest-labs/flux-schnell",
                input={
                    "prompt": prompt,
                    "num_outputs": 1,
                    "aspect_ratio": "1:1",
                    "output_format": "png",
                }
            )
            # Download the image
            url = output[0] if isinstance(output, list) else str(output)
            out_path = output_dir / f"{state_name}.png"
            urllib.request.urlretrieve(url, str(out_path))
            print(f"  ✅ {state_name}.png saved")
        except Exception as e:
            print(f"  ❌ Failed to generate {state_name}: {e}")
            return False

    return True


def generate_with_openai(name, vibe, style, output_dir):
    """Generate avatar using OpenAI DALL-E API."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return False

    base_prompt = f"VTuber avatar character named {name}, {vibe} personality, {style} style, clean lines, expressive face, solid green background (#00ff00), digital art"

    states = {
        "idle": f"{base_prompt}, neutral relaxed expression, calm pose",
        "talking": f"{base_prompt}, mouth open speaking, animated energetic pose",
    }

    output_dir.mkdir(parents=True, exist_ok=True)

    for state_name, prompt in states.items():
        print(f"  🎨 Generating {state_name} avatar (DALL-E)...")
        try:
            data = json.dumps({
                "model": "dall-e-3",
                "prompt": prompt,
                "n": 1,
                "size": "1024x1024",
                "response_format": "url"
            }).encode()

            req = urllib.request.Request(
                "https://api.openai.com/v1/images/generations",
                data=data,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}"
                }
            )
            with urllib.request.urlopen(req, timeout=60) as resp:
                result = json.loads(resp.read())
                url = result["data"][0]["url"]

            out_path = output_dir / f"{state_name}.png"
            urllib.request.urlretrieve(url, str(out_path))
            print(f"  ✅ {state_name}.png saved")
        except Exception as e:
            print(f"  ❌ Failed to generate {state_name}: {e}")
            return False

    return True


def use_template(template_name, output_dir):
    """Copy pre-made template avatars."""
    template_path = TEMPLATE_DIR / template_name
    if not template_path.exists():
        print(f"  ❌ Template '{template_name}' not found at {template_path}")
        print(f"  Available: {', '.join(TEMPLATES.keys())}")
        return False

    output_dir.mkdir(parents=True, exist_ok=True)
    for f in template_path.glob("*.png"):
        shutil.copy2(f, output_dir / f.name)
        print(f"  ✅ Copied {f.name}")

    return True


def create_placeholder(name, output_dir):
    """Create simple placeholder SVG-based avatars when no generation is available."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate simple colored circle avatars as placeholders
    initial = name[0].upper() if name else "?"
    
    colors = {"idle": "#6366f1", "talking": "#22c55e"}

    for state, color in colors.items():
        mouth = "" if state == "idle" else '<ellipse cx="100" cy="130" rx="15" ry="10" fill="#1a1a2e"/>'
        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200" viewBox="0 0 200 200">
  <circle cx="100" cy="100" r="90" fill="{color}"/>
  <text x="100" y="85" text-anchor="middle" font-size="48" font-family="Arial" fill="white">{initial}</text>
  <circle cx="75" cy="90" r="8" fill="white"/>
  <circle cx="125" cy="90" r="8" fill="white"/>
  <circle cx="75" cy="90" r="4" fill="#1a1a2e"/>
  <circle cx="125" cy="90" r="4" fill="#1a1a2e"/>
  {mouth}
</svg>'''
        # Save as SVG (Veadotube supports PNG, so note this is a fallback)
        out_path = output_dir / f"{state}.svg"
        with open(out_path, 'w') as f:
            f.write(svg)
        print(f"  ✅ {state}.svg placeholder created")

    print(f"\n  ℹ️  These are placeholder avatars. For better results:")
    print(f"     - Set REPLICATE_API_TOKEN for AI-generated avatars")
    print(f"     - Set OPENAI_API_KEY for DALL-E avatars")
    print(f"     - Or create your own PNGs in {output_dir}")
    return True


def main():
    parser = argparse.ArgumentParser(description="Generate VTuber avatars for wadebot")
    parser.add_argument("--name", "-n", default="Agent", help="Character name")
    parser.add_argument("--vibe", "-v", default="friendly", help="Personality vibe")
    parser.add_argument("--style", "-s", default="anime", help="Art style")
    parser.add_argument("--template", "-t", help="Use pre-made template instead of generating")
    parser.add_argument("--output", "-o", help="Output directory (default: ~/.wadebot/avatars)")
    args = parser.parse_args()

    output_dir = Path(args.output) if args.output else AVATAR_DIR
    
    print(f"\n  🎭 Avatar Generator")
    print(f"  Output: {output_dir}\n")

    # Template mode
    if args.template:
        if use_template(args.template, output_dir):
            print(f"\n  ✅ Template '{args.template}' ready!")
        else:
            sys.exit(1)
        return

    # Try generation methods in order
    print(f"  Character: {args.name} | Vibe: {args.vibe} | Style: {args.style}\n")

    if generate_with_replicate(args.name, args.vibe, args.style, output_dir):
        print(f"\n  ✅ Custom avatar generated with Replicate!")
        return

    if generate_with_openai(args.name, args.vibe, args.style, output_dir):
        print(f"\n  ✅ Custom avatar generated with DALL-E!")
        return

    print("  ℹ️  No image generation API available. Creating placeholder...")
    create_placeholder(args.name, output_dir)


if __name__ == "__main__":
    main()
