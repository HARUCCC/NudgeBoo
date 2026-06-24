"""Generate a cute, playful ghost icon for Loggy app."""
from PIL import Image, ImageDraw
import math


def make_icon(size=256):
    """Create a cute ghost icon at the given size."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    s = size / 256  # scale factor

    # ── Ghost body (rounded top + wavy bottom) ──
    body_color = (235, 235, 250, 230)
    shadow_color = (210, 210, 235, 180)

    # Main body - rounded rectangle-ish shape
    cx, cy = 128 * s, 120 * s
    rx, ry = 72 * s, 80 * s

    # Draw the body as a series of filled ellipses for smooth shape
    # Top dome
    for y_off in range(int(-ry), int(ry * 0.3)):
        progress = (y_off + ry) / (ry * 1.3)
        width = rx * math.sqrt(max(0, 1 - (y_off / ry) ** 2))
        y_pos = cy + y_off
        draw.ellipse(
            [cx - width, y_pos - 2 * s, cx + width, y_pos + 2 * s],
            fill=body_color
        )

    # Bottom wavy part
    for y_off in range(int(ry * 0.3), int(ry * 0.9)):
        progress = (y_off - ry * 0.3) / (ry * 0.6)
        # Narrower as we go down
        width = rx * (1 - progress * 0.5)
        y_pos = cy + y_off
        # Add wave
        wave = math.sin(progress * math.pi * 3) * 8 * s
        draw.ellipse(
            [cx - width + wave, y_pos - 2 * s, cx + width + wave, y_pos + 2 * s],
            fill=body_color
        )

    # Wavy bottom edge with 3 bumps
    bottom_y = cy + ry * 0.8
    for i in range(3):
        bx = cx + (i - 1) * 40 * s
        bump_r = 22 * s
        draw.ellipse(
            [bx - bump_r, bottom_y - bump_r * 0.6, bx + bump_r, bottom_y + bump_r * 0.6],
            fill=body_color
        )

    # ── Left highlight ──
    highlight_color = (255, 255, 255, 100)
    for y_off in range(int(-ry * 0.7), int(ry * 0.2)):
        progress = (y_off + ry * 0.7) / (ry * 0.9)
        width = 8 * s * (1 - abs(progress - 0.5) * 1.5)
        if width > 0:
            hx = cx - rx * 0.55
            hy = cy + y_off
            draw.ellipse(
                [hx - width, hy - 1.5 * s, hx + width, hy + 1.5 * s],
                fill=highlight_color
            )

    # ── Eyes ──
    eye_color = (50, 50, 75)
    iris_color = (80, 80, 130)
    pupil_color = (30, 30, 50)
    shine_color = (255, 255, 255, 220)

    for ex in [cx - 26 * s, cx + 26 * s]:
        ey = cy - 10 * s
        er = 14 * s
        # White of eye (not really white, slightly tinted)
        draw.ellipse([ex - er, ey - er * 1.1, ex + er, ey + er * 1.1], fill=(250, 250, 255))
        # Iris
        draw.ellipse([ex - er * 0.7, ey - er * 0.8, ex + er * 0.7, ey + er * 0.8], fill=iris_color)
        # Pupil
        pr = er * 0.45
        draw.ellipse([ex - pr, ey - pr * 1.1, ex + pr, ey + pr * 1.1], fill=pupil_color)
        # Shine
        sr = er * 0.25
        draw.ellipse([ex + sr * 0.3, ey - sr * 1.5, ex + sr * 0.3 + sr, ey - sr * 1.5 + sr], fill=shine_color)
        # Small secondary shine
        sr2 = er * 0.15
        draw.ellipse([ex - sr * 0.8, ey + sr * 0.3, ex - sr * 0.8 + sr2, ey + sr * 0.3 + sr2], fill=(255, 255, 255, 140))

    # ── Blush ──
    blush_color = (255, 160, 160, 70)
    for bx in [cx - 42 * s, cx + 42 * s]:
        by = cy + 10 * s
        draw.ellipse([bx - 10 * s, by - 5 * s, bx + 10 * s, by + 5 * s], fill=blush_color)

    # ── Mouth (small cute 'w' shape) ──
    mouth_color = (70, 70, 100)
    my = cy + 22 * s
    # Left bump of 'w'
    draw.arc(
        [cx - 12 * s, my - 6 * s, cx, my + 6 * s],
        start=0, end=180, fill=mouth_color, width=int(2.5 * s)
    )
    # Right bump of 'w'
    draw.arc(
        [cx, my - 6 * s, cx + 12 * s, my + 6 * s],
        start=0, end=180, fill=mouth_color, width=int(2.5 * s)
    )

    # ── Tiny pen in bottom-right (hint at logging) ──
    pen_x, pen_y = cx + 55 * s, cy + 50 * s
    pen_color = (240, 190, 60, 200)
    pen_tip = (100, 100, 100, 200)
    # Pen body (small rectangle, rotated)
    for i in range(int(25 * s)):
        px = pen_x + i * 0.3
        py = pen_y - i * 0.9
        draw.rectangle([px - 2 * s, py - 2 * s, px + 2 * s, py + 2 * s], fill=pen_color)
    # Pen tip
    tip_x = pen_x + 25 * s * 0.3
    tip_y = pen_y - 25 * s * 0.9
    draw.polygon([
        (tip_x, tip_y - 3 * s),
        (tip_x + 4 * s, tip_y + 5 * s),
        (tip_x - 4 * s, tip_y + 5 * s),
    ], fill=pen_tip)

    return img


def save_ico(path):
    """Generate and save as .ico with multiple sizes."""
    sizes = [16, 24, 32, 48, 64, 128, 256]
    images = []
    for sz in sizes:
        img = make_icon(sz)
        images.append(img)

    # Save as ICO
    images[0].save(
        path,
        format="ICO",
        sizes=[(sz, sz) for sz in sizes],
        append_images=images[1:]
    )
    print(f"Icon saved to {path}")


if __name__ == "__main__":
    import os
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app.ico")
    save_ico(out)
    # Also save a PNG preview
    preview = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app_preview.png")
    make_icon(256).save(preview)
    print(f"Preview saved to {preview}")
