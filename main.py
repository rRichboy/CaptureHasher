import signal
import menu_utils

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    while True:
        menu_utils.main_menu()
