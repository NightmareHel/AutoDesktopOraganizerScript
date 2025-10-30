import os
import shutil
import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from win10toast import ToastNotifier   # <=== NEW LIBRARY for Windows popups

# === CONFIGURATION ===
DESKTOP_PATH = r"C:\Users\likea\Desktop"   # <-- Update this path if needed
ORGANIZED_DIR = os.path.join(DESKTOP_PATH, "Organized")

CATEGORIES = {
    "Documents": [".pdf", ".docx", ".txt", ".xlsx", ".pptx"],
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".heic"],
    "Videos": [".mp4", ".mov", ".avi", ".mkv"],
    "Audio": [".mp3", ".wav", ".m4a"],
    "Archives": [".zip", ".rar", ".7z"],
}

# === LOGGING SETUP ===
logging.basicConfig(
    filename=os.path.join(ORGANIZED_DIR, "organizer.log"),
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
)

# === NOTIFICATION SETUP ===
toaster = ToastNotifier()

# === FILE EVENT HANDLER CLASS ===
class DesktopHandler(FileSystemEventHandler):
    def on_created(self, event):
        # Skip directories
        if event.is_directory:
            return

        # Wait briefly so file finishes downloading
        time.sleep(1)

        # Get filename and extension
        filename = os.path.basename(event.src_path)
        _, ext = os.path.splitext(filename)
        ext = ext.lower()

        moved = False

        # Sort into proper category
        for category, extensions in CATEGORIES.items():
            if ext in extensions:
                dest_folder = os.path.join(ORGANIZED_DIR, category)
                os.makedirs(dest_folder, exist_ok=True)
                shutil.move(event.src_path, os.path.join(dest_folder, filename))
                msg = f"Moved {filename} → {category}"
                print("📂", msg)
                logging.info(msg)
                toaster.show_toast("Desktop Organizer", msg, duration=3, threaded=True)
                moved = True
                break

        # If extension doesn’t match any category
        if not moved:
            other_folder = os.path.join(ORGANIZED_DIR, "Others")
            os.makedirs(other_folder, exist_ok=True)
            shutil.move(event.src_path, os.path.join(other_folder, filename))
            msg = f"Moved {filename} → Others"
            print("📂", msg)
            logging.info(msg)
            toaster.show_toast("Desktop Organizer", msg, duration=3, threaded=True)

# === MAIN PROGRAM ===
if __name__ == "__main__":
    # Make sure Organized folder exists
    os.makedirs(ORGANIZED_DIR, exist_ok=True)

    # Show startup notification
    toaster.show_toast("Desktop Organizer", "🧠 Organizer is now running!", duration=5, threaded=True)
    time.sleep(1)

    # Start the folder watcher
    event_handler = DesktopHandler()
    observer = Observer()
    observer.schedule(event_handler, DESKTOP_PATH, recursive=False)
    observer.start()
    print("🧠 Desktop Organizer is running... (Press Ctrl+C to stop)")

    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        observer.stop()
        print("\n🛑 Organizer stopped.")
    observer.join()
