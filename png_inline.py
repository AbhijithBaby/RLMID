#!/usr/bin/env python3
"""
png_inline.py

Usage:
  python3 png_inline.py            # uses defaults: images.png, main.c -> main_inlined.c
  python3 png_inline.py -i img.png -c main.c -o main_inlined.c
  python3 png_inline.py --width 100 --height 100

What it does:
 - Loads the input image (resizes to width x height if needed)
 - Builds a C array `static const uint32_t pixels[W*H] = { 0xRRGGBB, ... };`
 - Replaces a line `#include "pixels.h"` in the input C file with that array
 - Writes the result to the output C file (default: main_inlined.c)
"""
import argparse
import os
import re
from PIL import Image

def make_array_string(pixels, width, height, name="pixels", per_line=12):
    total = len(pixels)
    header = f"// --- begin inlined pixel array ({width}x{height}) ---\n"
    header += "#include <stdint.h>\n\n"
    header += f"static const uint32_t {name}[{total}] = {{\n"
    lines = []
    for i, (r, g, b, a) in enumerate(pixels):
        val = (r << 16) | (g << 8) | b
        s = f"0x{val:06X}"
        # add comma unless last
        if i != total - 1:
            s += ","
        # add spacing/grouping
        if (i % per_line) == 0:
            lines.append("    " + s)
        else:
            lines[-1] += " " + s
    body = "\n".join(lines) + "\n"
    footer = "};\n// --- end inlined pixel array ---\n\n"
    return header + body + footer

def main():
    ap = argparse.ArgumentParser(description="Inline pixels.h into main.c from an image.")
    ap.add_argument("-i", "--image", default="images.png", help="input image (default: images.png)")
    ap.add_argument("-c", "--cfile", default="main.c", help="input C file to modify (default: main.c)")
    ap.add_argument("-o", "--out", default="main_inlined.c", help="output C file (default: main_inlined.c)")
    ap.add_argument("--width", type=int, default=100, help="image width (default: 100)")
    ap.add_argument("--height", type=int, default=100, help="image height (default: 100)")
    ap.add_argument("--force-overwrite", action="store_true", help="overwrite output even if exists")
    args = ap.parse_args()

    if not os.path.isfile(args.image):
        print(f"Error: image file '{args.image}' not found.")
        return
    if not os.path.isfile(args.cfile):
        print(f"Error: C file '{args.cfile}' not found.")
        return
    if os.path.exists(args.out) and not args.force_overwrite:
        print(f"Error: output file '{args.out}' already exists. Use --force-overwrite to overwrite.")
        return

    # Load image and ensure RGBA
    img = Image.open(args.image).convert("RGBA")
    w, h = img.size
    if (w, h) != (args.width, args.height):
        print(f"Resizing image {w}x{h} -> {args.width}x{args.height}")
        img = img.resize((args.width, args.height), Image.LANCZOS)
    pixels = list(img.getdata())  # row-major

    # Build the C array text
    array_text = make_array_string(pixels, args.width, args.height, name="pixels", per_line=12)

    # Read the input C file
    with open(args.cfile, "r", encoding="utf-8") as f:
        ctext = f.read()

    # Try to replace #include "pixels.h" (allow whitespace)
    include_pattern = r'^[ \t]*#\s*include\s*"pixels\.h"\s*$'
    if re.search(include_pattern, ctext, flags=re.MULTILINE):
        new_ctext = re.sub(include_pattern, array_text, ctext, flags=re.MULTILINE)
        print("Replaced '#include \"pixels.h\"' with inlined array.")
    else:
        # If no include found, prepend the array at the top
        #print("Warning: '#include \"pixels.h\"' not found in the C file. Prepending array to the top of the file.")
        new_ctext = array_text + ctext

    # Write output
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(new_ctext)

    print(f"Wrote {args.out} — open this file in Ripes and compile/run.")

if __name__ == "__main__":
    main()
