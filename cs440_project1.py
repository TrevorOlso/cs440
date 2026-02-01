# CS 440 – Project 1
# PCB Simulator
# Trevor Olson 6686
# Tobias DiRito 8451

import sys
from enum import Enum
from collections import deque
import math

trevor_bear_id = 6
tobias_bear_id = 1

N = max(trevor_bear_id, tobias_bear_id)
auto_status_interval = N + 3

#INITIALIZE PROCESS STATES
class State(Enum):
    NEW = 0
    READY = 1
    RUNNING = 2
    WAITING = 3
    TERMINATED = 4

#INITIALIZE PCB CLASS
class PCB:
    def __init__(self, pid, name, priority):
        self.pid = pid
        self.name = name
        self.priority = priority
        self.state = State.NEW
        self.pc = 0
        self.cpuTime = 0

#initialize global variables
pid_counter = 1
process_table = {}
ready_queue = deque()
waiting_queue = deque()
running_process = None

#function for printing the log line after each step IF successfull
def log_success(step, command_str, details):
    """Prints a standard success log line."""
    print(f"[step={step}] CMD={command_str} | OK | {details}")

#function for printing the log line after each step IF NOT successfull
def log_error(step, command_str, error_msg):
    """Prints a standard error log line."""
    print(f"[step={step}] CMD={command_str} | ERROR | {error_msg}")

#function for status printing correctly formatted based on project requirements. called upon interval, or is status command received.
def print_status():
    """Prints the system state snapshot."""
    global running_process, ready_queue, waiting_queue, process_table
    
    # 1. RUNNING
    run_str = running_process.name if running_process else "NONE"
    print(f"RUNNING: {run_str}")
    
    # 2. READY (Format: [P1, P3])
    ready_names = [p.name for p in ready_queue]
    print(f"READY: [{', '.join(ready_names)}]")
    
    # 3. WAITING (Format: [P2])
    waiting_names = [p.name for p in waiting_queue]
    print(f"WAITING: [{', '.join(waiting_names)}]")
    
    # 4. TABLE
    print("TABLE:")
    # Header 
    print(f"{'PID':<5} {'NAME':<10} {'STATE':<12} {'PRIO':<6} {'PC':<5} {'CPUTIME':<8}")
    
    # Sort by PID so the table looks good adn in order
    sorted_pcbs = sorted(process_table.values(), key=lambda x: x.pid)
    for p in sorted_pcbs:
        print(f"{p.pid:<5} {p.name:<10} {p.state.name:<12} {p.priority:<6} {p.pc:<5} {p.cpuTime:<8}")


def main():
    global running_process, ready_queue, waiting_queue, process_table, pid_counter
# parse args
    if len(sys.argv) < 2:
        print("Usage: python3 project1.py <trace file>")
        sys.exit(1)

    filename = sys.argv[1]
# read trace file
    try:
        with open(filename, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        sys.exit(1)

    # BEGIN SIMULATION
    step_count = 0

    print(f"BearID last digit: {N}")
    print(f"Auto status every {auto_status_interval} steps")
    print("---- BEGIN LOG ----")

    for line in lines:
        line = line.strip()

        if not line or line.startswith('#'):
            continue

        step_count += 1
        parts = line.split()
        command = parts[0]


        if command == "CREATE":
            # create <name> <priority>
            name = parts[1]
            priority = int(parts[2])
            #create a pcb for this new process
            new_pcb = PCB(pid_counter, name, priority)
            pid_counter += 1
            #place process into ready
            new_pcb.state = State.READY
            process_table[name] = new_pcb
            ready_queue.append(new_pcb)
            log_success(step_count, line, f"{name}: NEW -> READY (pid={new_pcb.pid})")
        elif command == "DISPATCH":
            #check if cpu is busy
            if running_process is not None:
                log_error(step_count, line, f"CPU already running {running_process.name}")
            #check if there's nothing in the ready queue
            elif len(ready_queue) == 0:
                log_error(step_count, line, "no READY processes")
            #if cpu is idle:
            else:
                proc = ready_queue.popleft() #this is fifo as discussed in class
                proc.state = State.RUNNING
                running_process = proc

                log_success(step_count, line, f"{proc.name}: READY -> RUNNING")
        elif command == "TICK":
            pass # TODO: Implement TICK
        elif command == "BLOCK":
            pass # TODO: Implement BLOCK
        elif command == "WAKE":
            pass # TODO: Implement WAKE
        elif command == "EXIT":
            pass # TODO: Implement EXIT
        elif command == "STATUS":
            log_success(step_count, line, "")
            print_status()
        elif command == "KILL":
            pass # TODO: Extra Credit
        else:
            print(f"[step={step_count}] CMD={command} | ERROR | Unknown command")
        

        if step_count % auto_status_interval == 0:
            print_status()
    print("--- END LOG ---")
if __name__ == "__main__":
    main()