import threading
from GUIManager import *

if __name__ == "__main__":
    try:
        GUIThread = threading.Thread(target = startGUI)
        GUIThread.start()
    except(SystemExit, KeyboardInterrupt):
        pass
    finally:
        GUIThread.join()