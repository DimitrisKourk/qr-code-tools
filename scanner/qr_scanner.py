import sys
import cv2
import numpy as np
from pyzbar import pyzbar
from bs4 import BeautifulSoup as bs
import requests

frequency = 2000  # beep frequency in Hertz
duration = 350  # beep duration in ms


def beep():
    """Play a confirmation beep: winsound on Windows, the terminal bell elsewhere."""
    try:
        import winsound
        winsound.Beep(frequency, duration)
    except ImportError:
        print("\a", end="", flush=True)


def scan_qr_code():
    """Show the webcam feed until a QR code is read. Returns its text, or None."""
    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        print("Error: could not open the webcam.")
        return None

    data = None
    try:
        while data is None:
            success, image = cam.read()
            if not success:
                print("Error: could not read a frame from the webcam.")
                break

            for code in pyzbar.decode(image):
                decoded = code.data.decode("utf-8")
                if decoded:
                    pts = np.array([code.polygon], np.int32)
                    cv2.polylines(image, [pts], True, (0, 255, 0), 3)
                    data = decoded

            cv2.imshow("QR Code Scanner (press q to quit)", image)
            if cv2.waitKey(5) & 0xFF == ord("q"):
                break
    finally:
        cam.release()
        cv2.destroyAllWindows()

    if data is not None:
        beep()
    return data


def get_receipt_price(url):
    """Download the receipt page and return the price, or None if it can't be found."""
    try:
        result = requests.get(url, timeout=10)
        result.raise_for_status()
    except requests.RequestException as e:
        print(f"Error: could not load the receipt page ({e}).")
        return None

    # scraping the website for the price
    soup = bs(result.text, "lxml")
    box = soup.find("div", class_="grid-container")
    receipt = box.find("p", class_="receipt") if box else None
    if receipt is None:
        print("Error: the page doesn't have the expected receipt layout.")
        return None

    tokens = receipt.get_text().split()
    try:
        return float(tokens[9])  # the price is the 10th word of the receipt text
    except (IndexError, ValueError):
        print("Error: could not find the price in the receipt text.")
        return None


data = scan_qr_code()
if data is None:
    sys.exit(1)

print(f"QR code: {data}")
if not data.startswith(("http://", "https://")):
    print("Error: the QR code doesn't contain a web link.")
    sys.exit(1)

price = get_receipt_price(data)
if price is None:
    sys.exit(1)
print(price)
