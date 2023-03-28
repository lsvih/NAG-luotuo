import signal
import time

from modules import options
from modules.model import load_model
from modules.options import cmd_opts
from modules.api import create_api


def init():
    load_model()


def wait_on_server(api=None):
    while 1:
        time.sleep(1)
        if options.need_restart:
            options.need_restart = False
            time.sleep(0.5)
            api.close()
            time.sleep(0.5)
            break


instance = None


def handler(signum, frame):
    global instance
    res = input("Ctrl-c was pressed. Do you really want to exit? y/n ")
    if res == 'y':
        instance.close()
        exit(1)


signal.signal(signal.SIGINT, handler)


def main():
    global instance
    while True:
        instance = create_api()
        instance.queue(concurrency_count=5, max_size=64).launch(
            server_name="0.0.0.0" if cmd_opts.listen else None,
            server_port=cmd_opts.port,
            share=False,
            prevent_thread_lock=True,
            show_api=True
        )
        wait_on_server(instance)


if __name__ == "__main__":
    init()
    main()
