# QR Code Tools

Two small Python utilities for working with QR codes: a **generator** that turns text into a QR code image, and a **webcam scanner** that reads a QR code live from the camera and pulls a price from the receipt page it links to.

```
qr-code-tools/
├── generator/qr_generator.py   # text → QR code PNG
├── scanner/qr_scanner.py       # webcam → decoded URL → scraped price
└── requirements.txt
```

## Install

```bash
pip install -r requirements.txt
```

The scanner's `pyzbar` package also needs the system **ZBar** library:

| OS | Command |
|---|---|
| Arch Linux | `sudo pacman -S zbar` |
| Debian / Ubuntu | `sudo apt install libzbar0` |
| macOS | `brew install zbar` |
| Windows | Included in the `pyzbar` wheel |

---

## Generator

Turns any text or URL into a QR code image, using the [`qrcode`](https://pypi.org/project/qrcode/) library.

1. Asks you for the data to embed.
2. Builds the QR code with these settings:

   | Setting | Value | Meaning |
   |---|---|---|
   | `version` | 1, with `fit=True` | Start with the smallest 21×21 grid and grow automatically if the data doesn't fit |
   | `error_correction` | `ERROR_CORRECT_L` | About 7% of the code can be damaged and still scan |
   | `box_size` | 20 | Each module (square) is 20×20 pixels |
   | `border` | 2 | Quiet-zone width around the code, in modules |

3. Saves it black on white as **`QRCODE.png`** in the current folder. Running it again overwrites the file.

```bash
python generator/qr_generator.py
```

```
Enter data to embed: https://github.com/DimitrisKourk
```

---

## Scanner

Reads a QR code from the webcam and, if it links to a digital receipt, extracts the total price from that page.

1. **Capture.** Opens the default webcam with OpenCV and shows the live feed in a window.
2. **Detect and decode.** Every frame is passed to [ZBar](https://github.com/NaturalHistoryMuseum/pyzbar). When a QR code is found, its outline is drawn in green, a beep sounds, and the camera closes.
3. **Fetch.** The decoded content is treated as a URL and downloaded with `requests`.
4. **Scrape.** The page is parsed with BeautifulSoup. The script finds the receipt text (`<div class="grid-container">` → `<p class="receipt">`) and prints the price, which it takes from a fixed position in that text.

```bash
python scanner/qr_scanner.py
```

Hold a receipt's QR code up to the camera, or press **q** to quit. The price is printed once the code is read.

The script stops with a clear message, instead of crashing, if:
- the webcam can't be opened
- the QR code isn't a web link
- the page can't be loaded
- the page doesn't have the expected layout

The confirmation beep uses `winsound` on Windows and the terminal bell on other systems.

### Limitations

- **Tied to one receipt page layout.** The scraper looks for specific HTML classes and reads the price from a fixed word position, so it only works with receipts from the site it was written for.
