import qrcode

QR = qrcode.QRCode(version=1,
                   error_correction=qrcode.constants.ERROR_CORRECT_L,
                   box_size=20,
                   border=2)

data = input("Enter data to embed: ")
QR.add_data(data)

QR.make(fit=True)

image = QR.make_image(fill_color="black", back_color="white")
image.save("QRCODE.png")

