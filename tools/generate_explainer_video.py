#!/usr/bin/env python3
"""Render a silent, captioned explainer video for the AIORI-3 submission."""

from pathlib import Path
import subprocess
import tempfile

from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg


WIDTH, HEIGHT = 1280, 720
BACKGROUND = "#08111f"
PANEL = "#111f32"
PANEL_ALT = "#14263c"
TEXT = "#eff6ff"
MUTED = "#9cb0c8"
CYAN = "#53d8e8"
GREEN = "#65e6b1"
AMBER = "#ffc66d"
OUTPUT = Path(__file__).resolve().parents[1] / "assets" / "aiori-3-demo-explainer.mp4"


def font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    fonts = (
        Path("C:\\Windows\\Fonts\\segoeui.ttf"),
        Path("C:\\Windows\\Fonts\\arial.ttf"),
    )
    for font_path in fonts:
        if font_path.exists():
            return ImageFont.truetype(str(font_path), size)
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def make_canvas(index: int, title: str, subtitle: str) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    image = Image.new("RGB", (WIDTH, HEIGHT), BACKGROUND)
    draw = ImageDraw.Draw(image)
    for x in range(0, WIDTH, 48):
        draw.line((x, 0, x, HEIGHT), fill="#0c1929", width=1)
    for y in range(0, HEIGHT, 48):
        draw.line((0, y, WIDTH, y), fill="#0c1929", width=1)

    draw.text((72, 44), "AIORI-3  /  LAST MINUTE CODERS", font=font(22), fill=CYAN)
    draw.text((1100, 44), f"{index:02d} / 05", font=font(20), fill=MUTED)
    draw.text((72, 108), title, font=font(48), fill=TEXT)
    draw.text((74, 174), subtitle, font=font(25), fill=MUTED)
    draw.line((72, 654, 1208, 654), fill="#26384d", width=2)
    draw.text((72, 674), "PRIVACY-AWARE IPv6 IoT SECURITY MONITORING", font=font(16), fill=MUTED)
    draw.rounded_rectangle((1040, 674, 1208, 694), radius=10, fill="#1a2a3f")
    draw.rounded_rectangle((1040, 674, 1040 + index * 33, 694), radius=10, fill=CYAN)
    return image, draw


def card(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], label: str, detail: str, color: str = CYAN) -> None:
    draw.rounded_rectangle(box, radius=20, fill=PANEL, outline="#26384d", width=2)
    x1, y1, _, _ = box
    draw.rounded_rectangle((x1 + 20, y1 + 20, x1 + 31, y1 + 66), radius=5, fill=color)
    draw.text((x1 + 50, y1 + 22), label, font=font(25), fill=TEXT)
    draw.text((x1 + 50, y1 + 67), detail, font=font(20), fill=MUTED)


def arrow(draw: ImageDraw.ImageDraw, start: tuple[int, int], end: tuple[int, int]) -> None:
    draw.line((start, end), fill=CYAN, width=5)
    x, y = end
    draw.polygon(((x, y), (x - 16, y - 10), (x - 16, y + 10)), fill=CYAN)


def slides() -> list[Image.Image]:
    result = []

    image, draw = make_canvas(
        1,
        "Address rotation hides device behavior",
        "IoT devices can appear under changing IPv6 addresses.",
    )
    card(draw, (92, 280, 366, 404), "One device", "demo-sensor-01", CYAN)
    addresses = ("2001:db8:1::1", "2001:db8:1::2", "2001:db8:1::3")
    for position, address in enumerate(addresses):
        x = 470 + position * 235
        card(draw, (x, 280, x + 205, 404), f"Address {position + 1}", address, AMBER)
    arrow(draw, (370, 340), (456, 340))
    draw.text((92, 472), "Same source. New addresses. Harder to correlate without privacy-aware monitoring.", font=font(23), fill=TEXT)
    result.append(image)

    image, draw = make_canvas(
        2,
        "Correlate events without exposing identifiers",
        "HMAC-based pseudonyms support comparison while API responses stay limited.",
    )
    card(draw, (92, 290, 360, 414), "Device ID", "private input", CYAN)
    card(draw, (492, 290, 760, 414), "HMAC-SHA256", "secret-keyed", GREEN)
    card(draw, (892, 290, 1160, 414), "Pseudonym", "stable correlation key", AMBER)
    arrow(draw, (370, 352), (476, 352))
    arrow(draw, (770, 352), (876, 352))
    draw.text((92, 470), "IPv6 addresses are fingerprinted for rotation checks.", font=font(23), fill=TEXT)
    draw.text((92, 510), "The demo stores raw IPv6 internally; summary and alert responses omit the full address.", font=font(21), fill=MUTED)
    result.append(image)

    image, draw = make_canvas(
        3,
        "Detect repeated changes in a short window",
        "The prototype checks consecutive address-fingerprint changes over 15 minutes.",
    )
    draw.line((150, 375, 1128, 375), fill="#46627c", width=5)
    for x, number, address in ((230, "1", "::1"), (635, "2", "::2"), (1040, "3", "::3")):
        draw.ellipse((x - 27, 348, x + 27, 402), fill=PANEL_ALT, outline=CYAN, width=4)
        draw.text((x - 8, 359), number, font=font(25), fill=TEXT)
        draw.text((x - 65, 425), f"IPv6 {address}", font=font(22), fill=MUTED)
    draw.rounded_rectangle((340, 515, 940, 588), radius=18, fill="#173a3a", outline=GREEN, width=2)
    draw.text((384, 535), "2 rotations detected  ->  review alert", font=font(26), fill=GREEN)
    result.append(image)

    image, draw = make_canvas(
        4,
        "Show an explainable, limited alert",
        "Operators see the signal and pseudonym, not the submitted raw identity.",
    )
    draw.rounded_rectangle((150, 255, 1130, 560), radius=20, fill="#0c1827", outline="#2a4058", width=2)
    lines = (
        ('"device_key":', '"<partial HMAC pseudonym>"', CYAN),
        ('"severity":', '"medium"', AMBER),
        ('"title":', '"Rapid IPv6 Rotation Detected"', GREEN),
        ('"score":', "7.5", TEXT),
    )
    for row, (key, value, color) in enumerate(lines):
        y = 292 + row * 58
        draw.text((205, y), key, font=font(27), fill=MUTED)
        draw.text((465, y), value, font=font(27), fill=color)
    draw.text((150, 596), "Illustrative response fields; show the actual API output in your recording.", font=font(19), fill=MUTED)
    result.append(image)

    image, draw = make_canvas(
        5,
        "A lightweight prototype for security review",
        "FastAPI ingestion  ->  rotation heuristic  ->  SQLite  ->  summary and alerts",
    )
    card(draw, (92, 300, 420, 424), "Ingest", "POST /api/v1/events", CYAN)
    card(draw, (474, 300, 802, 424), "Analyze", "15-minute rotation window", GREEN)
    card(draw, (856, 300, 1184, 424), "Review", "GET /api/v1/summary", AMBER)
    arrow(draw, (426, 362), (458, 362))
    arrow(draw, (808, 362), (840, 362))
    draw.text((92, 492), "Hackathon prototype — protect secrets and validate controls before production use.", font=font(22), fill=TEXT)
    result.append(image)

    return result


def main() -> None:
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="aiori-video-") as temporary_directory:
        temporary_path = Path(temporary_directory)
        for index, image in enumerate(slides()):
            image.save(temporary_path / f"slide-{index:02d}.png")

        command = [
            ffmpeg,
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-framerate",
            "1/4",
            "-i",
            "slide-%02d.png",
            "-vf",
            "fps=24",
            "-frames:v",
            "480",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "25",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            str(OUTPUT),
        ]
        subprocess.run(command, cwd=temporary_path, check=True)

    print(f"Created silent explainer video: {OUTPUT}")


if __name__ == "__main__":
    main()
