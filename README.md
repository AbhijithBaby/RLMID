# RLMID — Ripes LED Matrix Image Display

Display images on the [Ripes](https://github.com/mortbopet/Ripes) simulator's LED Matrix peripheral using a C program with inlined pixel data.

---

## Overview

RLMID lets you take any PNG image, convert it into a flat `uint32_t` pixel array, and embed it directly into a C source file. The resulting file compiles and runs inside Ripes, writing every pixel to the LED Matrix memory-mapped peripheral — showing your image on the virtual LED display.

The project includes:

- **`png_inline.py`** — Python script that reads an image, resizes it, and inlines the pixel array into a C file by replacing a `#include "pixels.h"` directive (or prepending it if the directive is absent).
- **`main.c`** — Minimal C driver that writes each pixel value to the LED Matrix base address via a memory-mapped pointer.
- **`main_inlined.c` / `main_inlined1.c`** — Pre-generated examples of `main.c` with the pixel array already inlined (100×100 pixels).
- **`images.png`** — Sample input image used to generate the inlined files.
- **`Lenna_(test_image)_IMGP.png`** — Classic Lenna test image included for experimentation.

---

## Screenshots

### Running in Ripes — LED Matrix output

![Screenshot 1](https://raw.githubusercontent.com/AbhijithBaby/RLMID/Master/Screenshot_2026-03-07_22-23-08.png)

![Screenshot 2](https://raw.githubusercontent.com/AbhijithBaby/RLMID/Master/Screenshot_2026-03-08_03-39-22.png)

---

## Test Images

Two 100×100 sample images are included to get started immediately.

| Image | Preview | Description |
|---|---|---|
| `images.png` | ![images.png](https://raw.githubusercontent.com/AbhijithBaby/RLMID/Master/images.png) | Default sample image used by `png_inline.py` |
| `Lenna_(test_image)_IMGP.png` | ![Lenna](https://raw.githubusercontent.com/AbhijithBaby/RLMID/Master/Lenna_%28test_image%29_IMGP.png) | Classic [Lenna](https://en.wikipedia.org/wiki/Lenna) test image, resized to 100×100 |

To use either image, pass it with `-i`:

```bash
python3 png_inline.py -i "Lenna_(test_image)_IMGP.png" -o lenna_inlined.c
```

---

## Requirements

- Python 3.x
- [Pillow](https://python-pillow.org/) (`pip install Pillow`)
- [Ripes simulator](https://github.com/mortbopet/Ripes) with an LED Matrix peripheral configured

---

## Usage

### Step 1 — Generate the inlined C file

```bash
python3 png_inline.py
```

This uses the defaults: reads `images.png`, patches `main.c`, and writes `main_inlined.c`.

**Custom options:**

```bash
python3 png_inline.py -i my_image.png -c main.c -o output.c --width 100 --height 100
```

| Flag | Default | Description |
|---|---|---|
| `-i`, `--image` | `images.png` | Input PNG image |
| `-c`, `--cfile` | `main.c` | C source file to patch |
| `-o`, `--out` | `main_inlined.c` | Output C file |
| `--width` | `100` | Target display width in pixels |
| `--height` | `100` | Target display height in pixels |
| `--force-overwrite` | off | Overwrite the output file if it already exists |

If the image dimensions differ from the target, it is automatically resized using a high-quality Lanczos filter.

### Step 2 — Run in Ripes

1. Open Ripes and navigate to the **I/O** tab.
2. Double-click **LED Matrix** to instantiate it. Ripes automatically assigns it a base address in the memory map.
3. Select the LED Matrix device and set its **Width** and **Height** parameters to match what you used with `png_inline.py` (default: 100×100).
4. In the right-hand panel, Ripes will show the exported symbol (e.g. `LED_MATRIX_BASE`) with the actual base address assigned to your device. This value is available in C by including the generated header:
   ```c
   #include "ripes_system.h"
   ```
   Once included, you can reference `LED_MATRIX_BASE` directly — no hardcoding needed.
5. Load `main_inlined.c` into the Ripes editor, build, and run.

The program writes each pixel (as `0x00RRGGBB`) to the LED Matrix memory region and the image appears on the display.

> **Note:** The `LED_MATRIX_BASE` macro in `main.c` has a fallback value of `0xF0000000` for reference only. Always use `ripes_system.h` in practice so your code picks up the address Ripes actually assigned.

---

## How It Works

`png_inline.py` converts each pixel to a 24-bit hex value of the form `0xRRGGBB` and emits a static C array:

```c
static const uint32_t pixels[10000] = {
    0xF6F6F6, 0xF6F6F6, /* ... */
};
```

`main.c` casts the LED Matrix base address to a `volatile uint32_t *` pointer and copies the array to it in a loop:

```c
volatile uint32_t *led_mem = (volatile uint32_t *)LED_MATRIX_BASE;
for (size_t i = 0; i < to_copy; ++i) {
    led_mem[i] = pixels[i];
}
```

---

## Configuration

The following compile-time macros can be overridden:

| Macro | Default | Description |
|---|---|---|
| `LED_MATRIX_BASE` | `0xF0000000` (fallback only) | Base address of the LED Matrix peripheral. Ripes assigns this automatically — use `#include "ripes_system.h"` to get the correct value. |
| `WIDTH` | `100` | Display width in pixels |
| `HEIGHT` | `100` | Display height in pixels |

Ripes exports all device base addresses and sizes as named symbols (e.g. `LED_MATRIX_BASE`, `LED_MATRIX_SIZE`) which are accessible in C programs via `#include "ripes_system.h"`. See the [Ripes MMIO documentation](https://github.com/mortbopet/Ripes/blob/master/docs/mmio.md) for details.

---

## License

This project is licensed under the terms found in the [LICENSE](LICENSE) file.
