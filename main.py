import sys
from wmctrl import Window
import time
import subprocess
import logging as log

# Set up logging
log.basicConfig(filename='window-memory.log', level=log.INFO)

PREFIX = "CUSTOM_MEMORY_WINDOW_"
MAX_WAITING_TIME_MILLIS = 3000
WAITING_INTERVAL_MILLIS = 100.0


def get_open_window_ids():
    output = []
    for current_window in Window.list():
        output.append(current_window.id)
    log.debug("returning ids from currently open window: " + str(output))
    return output


def get_new_window_id(fst, snd):
    diff = list(set(fst) - set(snd))
    if len(diff) == 0:
        log.debug("no new window id")
        return None
    else:
        log.debug("found new window id: " + diff[0])
        return diff[0]


def set_window_memory(memory_window_title):
    ids_before_allocation = get_open_window_ids()
    log.debug("ids from windows open before user set a new window: " + str(ids_before_allocation))

    current_waiting_time = 0
    new_window_id = None

    while new_window_id is None and current_waiting_time < MAX_WAITING_TIME_MILLIS:
        current_open_window_ids = get_open_window_ids()
        new_window_id = get_new_window_id(current_open_window_ids, ids_before_allocation)
        current_waiting_time += WAITING_INTERVAL_MILLIS
        time.sleep(WAITING_INTERVAL_MILLIS / 1000)

    if new_window_id is not None:
        log.info("new window with id: " + new_window_id)
        log.info("setting new name for window: " + memory_window_title)
        subprocess.run(["wmctrl", "-i", "-r", str(new_window_id), "-T", memory_window_title])
    else:
        log.debug("nothing happened - user was too slow with setting a new window into the memory slot")


def window_already_present(memory_window_title):
    window_present = False
    for current_window in Window.list():
        window_present = window_present or current_window.wm_name == memory_window_title
    log.debug("window with the given name already present: " + memory_window_title)
    return window_present


def select_window_by_name(memory_window_name):
    for current_window in Window.list():
        if current_window.wm_name == memory_window_name:
            log.info("selecting window by name: " + memory_window_name)
            subprocess.run(["wmctrl", "-ia", str(current_window.id)])


# todo toggle visibility when memory slot already allocated
# todo check arg count
memory_window_title = PREFIX + str(sys.argv[1])
if window_already_present(memory_window_title):
    select_window_by_name(memory_window_title)
else:
    set_window_memory(memory_window_title)
