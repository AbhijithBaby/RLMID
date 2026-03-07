// main.c
#include <stdint.h>
#include <stddef.h>

#ifndef LED_MATRIX_BASE
// Default peripheral base address. Change this to the BASE you set for the LED Matrix in Ripes I/O.
#define LED_MATRIX_BASE 0xf0000000U
#endif

#ifndef WIDTH
#define WIDTH 100
#endif
#ifndef HEIGHT
#define HEIGHT 100
#endif

int main(void) {
    volatile uint32_t *led_mem = (volatile uint32_t *)LED_MATRIX_BASE;
    const size_t total_pixels = (size_t)WIDTH * (size_t)HEIGHT;

    // Simple safety check: avoid overflow if pixels array missing or wrong size.
    // (If you compiled with a real pixels.h containing 10000 elements this check is optional.)
    // We'll copy min(total_pixels, 10000).
    size_t to_copy = total_pixels < 10000 ? total_pixels : 10000;

    for (size_t i = 0; i < to_copy; ++i) {
        // Each pixel value is expected as 0x00RRGGBB (R in bits 23..16, G in 15..8, B in 7..0)
        led_mem[i] = pixels[i];
    }

    // If you want the program to keep running/looped for a simulator to show output, loop here.

    return 0;
}

