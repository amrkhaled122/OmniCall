import qrcode
import sys

PWA_URL = "https://amrkhaled122.github.io/OmniCall/"

def generate_qr(url):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4
    )
    qr.add_data(url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    img.save("pwa_qr.png")
    print(f"QR code generated and saved as 'pwa_qr.png'. Scan this to install the PWA.\n")
    
    qr.print_ascii(tty=True)

def main():
    print("Generating QR code for OmniCall PWA install link...\n")
    generate_qr(PWA_URL)
    print("\nScan the QR code above with your phone to open OmniCall PWA install page.")

    # Placeholder - later: listen for CLI commands here

if __name__ == "__main__":
    main()
