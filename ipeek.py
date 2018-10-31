#!/usr/bin/env python3
import sys
import psutil
from psutil import virtual_memory
import re

mem = virtual_memory()
total_memory = mem.total

ipeek_pattern = re.compile(r'ipeek')

LINUX = sys.platform.startswith("linux")


def transform(usage):
    if usage / 1024 < 1:
        mem_str = "%.2f/B" % (usage)
        return mem_str

    if usage / 1024 / 1024 < 1:
        mem_str = "%.2f/K" % (usage / 1024)
        return mem_str

    if usage / 1024 / 1024 / 1024 < 1:
        mem_str = "%.2f/M" % (usage / 1024 / 1024)
        return mem_str

    mem_str = "%.2f/G" % (usage / 1024 / 1024 / 1024)
    return mem_str


def peek_pid(pid):
    while True:
        try:
            proc = psutil.Process(pid)
            memory_info = proc.memory_info()
            rss = memory_info[0]
            cpu_percent = proc.cpu_percent(interval=1)
            show_str = "PID:{pid},MEM::{mem},CPU:{cpu}".format(pid=pid,
                                                               mem=transform(rss),
                                                               cpu=cpu_percent,
                                                               )
            print(show_str)
        except psutil.AccessDenied:
            print("no permission")
            break
        except psutil.NoSuchProcess:
            print("no such process")
            break


def find_pid(pattern):
    pids = psutil.pids()
    finds = []
    for pid in pids:
        try:
            proc = psutil.Process(pid)
            cmdline = " ".join(proc.cmdline())
            matched = re.findall(pattern, cmdline)
            if matched:
                if ipeek_pattern.findall(cmdline):
                    continue
                print("Find:{cmd},PID:{pid}".format(cmd=cmdline, pid=pid))
                finds.append(pid)
        except psutil.AccessDenied:
            pass
        except psutil.NoSuchProcess:
            pass
    if len(finds) == 0:
        print("not find process")
        return -1
    if len(finds) > 1:
        print("more than one found")
        return -1
    return finds[0]


def main(pattern_str):
    try:
        pid = int(pattern_str)
    except ValueError:
        pid = find_pid(pattern_str)
    if pid > 0:
        peek_pid(pid)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("less pid")
        exit(1)

    main(sys.argv[1])
