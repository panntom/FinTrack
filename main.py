# main.py
# Entry point for FinTrack application
# Run this file to start the app: python main.py

import sys
import os


def check_dependencies():
    """
    Check that required modules are available.
    Gives a friendly error message if something is missing.
    """
    try:
        import tkinter
    except ImportError:
        print("[ERROR] Tkinter is not installed.")
        print("On Linux: sudo apt-get install python3-tk")
        sys.exit(1)


def main():
    check_dependencies()

    # Add project root to path so imports work correctly
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

    from ui.app import FinTrackApp

    print("[FinTrack] Starting application...")
    app = FinTrackApp()
    app.mainloop()
    print("[FinTrack] Application closed.")


if __name__ == "__main__":
    main()