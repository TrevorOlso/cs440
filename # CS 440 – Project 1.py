# CS 440 – Project 1
# PCB Simulator
# Trevor Olson 6686
# Tobias DiRito 8451

import sys
from enum import Enum
from collections import deque

class State(Enum):
    NEW = 0
    READY = 1
    RUNNING = 2
    WAITING = 3
    TERMINATED = 4

class PCB:
    def __init__(self, pid, name, priority):
        self.pid = pid
        self.name = name
        self.priority = priority
        self.state = State.NEW
        self.pc = 0
        self.cpuTime = 0


process_table = {}
ready_queue = deque()
waiting_queue = deque()
running_reference = None


n = 9

def main():
# TODO: parse args
    if len(sys.argv) < 2:
        print("Usage: python3 project1.py <trace file>")
        sys.exit(1)

    filename = sys.argv[1]
# TODO: read trace file
    try:
        with open(filename, 'r') as f:
            trace_lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        sys.exit(1)

    step_count = 0

    print('BearID last digit: 6')
    print('Auto status every 9 steps')
    
    for line in lines:
        line = line.strip()

        if not line or line.startswith('#'):
            continue

        step_count += 1
        parts = line.split()
        command = parts[0]


    # TODO: dispatch commands
    if command == "CREATE":
        pass # TODO: Implement CREATE
    elif command == "DISPATCH":
        pass # TODO: Implement DISPATCH
    elif command == "TICK":
        pass # TODO: Implement TICK
    elif command == "BLOCK":
        pass # TODO: Implement BLOCK
    elif command == "WAKE":
        pass # TODO: Implement WAKE
    elif command == "EXIT":
        pass # TODO: Implement EXIT
    elif command == "STATUS":
        pass # TODO: Implement STATUS
    elif command == "KILL":
        pass # TODO: Extra Credit
    else:
        print(f"[step={step_count}] CMD={command} | ERROR | Unknown command")
    

    if step_count % 9 == 0:
        pass # TODO: Print status

if __name__ == "__main__":
    main()