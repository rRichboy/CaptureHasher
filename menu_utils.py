import signal
import sys
import threading
from termcolor import colored
import network_utils


# Основное меню
def main_menu():
    while True:
        print(colored("\n=== Меню захвата хэндшейка ===", "yellow"))
        print(colored("1. Автоматическое определение сетевой карты", "cyan"))
        print(colored("2. Включить режим монитора", "cyan"))
        print(colored("3. Выключить режим монитора", "cyan"))
        print(colored("4. Обновить интерфейсы и их названия", "cyan"))
        print(colored("5. Поиск сетей", "cyan"))
        print(colored("6. Захват хэндшейка", "cyan"))
        print(colored("0. Выход", "cyan"))

        choice = input(colored("Введите ваш выбор: ", "green"))

        if choice == "1":
            interface = network_utils.auto_detect_network_card()
            if interface:
                print(colored(f"Сетевая карта {interface} обнаружена.", "green"))
        elif choice == "2":
            interface = network_utils.choose_network_card()
            if interface:
                network_utils.enable_monitor_mode(interface)
        elif choice == "3":
            interface = network_utils.choose_network_card()
            if interface:
                network_utils.disable_monitor_mode(interface)
        elif choice == "4":
            network_utils.update_interfaces()
        elif choice == "5":
            interface = network_utils.choose_network_card()
            if interface:
                network_utils.search_networks(interface)
        elif choice == "6":
            interface = network_utils.choose_network_card()
            if interface:
                bssid = input(colored("Введите BSSID выбранной сети: ", "green"))
                channel = input(colored("Введите требуемый канал: ", "green"))
                path = input(colored("Введите путь для сохранения хэндшейка: ", "green"))
                filename = input(colored("Введите имя файла для сохранения хэндшейка: ", "green"))
                # Создаем объект события
                capture_event = threading.Event()

                # Создаем поток для захвата хэндшейка
                capture_thread = threading.Thread(target=network_utils.capture_handshake,
                                                  args=(interface, bssid, channel, path, filename, capture_event))

                # Создаем поток для функции deauthenticate_clients
                deauth_thread = threading.Thread(target=network_utils.deauthenticate_clients,
                                                 args=(interface, bssid, capture_event))

                # Запускаем потоки параллельно
                capture_thread.start()
                deauth_thread.start()

                # Ждем завершения захвата хэндшейка
                capture_thread.join()

                # Останавливаем отключение пользователей после завершения захвата хэндшейка
                capture_event.clear()
                deauth_thread.join()
        elif choice == "0":
            sys.exit(colored("Выход из программы.", "yellow"))
        else:
            print(colored("Неверный выбор. Пожалуйста, попробуйте снова.", "red"))


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_IGN)  # Игнорируем сигнал SIGINT (Ctrl+C) в основном цикле программы
    while True:
        main_menu()
