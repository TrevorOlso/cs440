# CS 440
# Trevor Olson, Tobias DiRito
# 6686, 8451
# Due on 2/15/2026
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
    print(f"[step={step}] CMD={command_str} | OK | {details}")

#function for printing the log line after each step IF NOT successfull
def log_error(step, command_str, error_msg):
    print(f"[step={step}] CMD={command_str} | ERROR | {error_msg}")

#function for status printing correctly formatted
def print_status():

    global running_process, ready_queue, waiting_queue, process_table
    
    # 1. running
    run_str = running_process.name if running_process else "NONE"
    print(f"RUNNING: {run_str}")
    
    # 2. ready
    ready_names = [p.name for p in ready_queue]
    print(f"READY: [{', '.join(ready_names)}]")
    
    # 3. waiting
    waiting_names = [p.name for p in waiting_queue]
    print(f"WAITING: [{', '.join(waiting_names)}]\n")
    
    # 4. table
    print("TABLE:")
    # Header 
    print(f"{'PID':<5} {'NAME':<10} {'STATE':<12} {'PRIO':<6} {'PC':<5} {'CPUTIME':<8}")
    
    # Sort by PID so the table looks good adn in order
    sorted_pcbs = sorted(process_table.values(), key=lambda x: x.pid)
    for p in sorted_pcbs:
        print(f"{p.pid:<5} {p.name:<10} {p.state.name:<12} {p.priority:<6} {p.pc:<5} {p.cpuTime:<8}")
    print()

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
    print("\n---- BEGIN LOG ----")

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
                #check if cpu is idle
                if running_process is None:
                    log_error(step_count, line, "no process is currently RUNNING")
                #if running_process is not None, add n ticks to pc and cpuTime
                else:
                    n_ticks = int(parts[1])
                    running_process.pc += n_ticks
                    running_process.cpuTime += n_ticks
                    log_success(step_count, line, f"{running_process.name}: pc+={n_ticks} cpuTime+={n_ticks}")
            

        elif command == "BLOCK":
            #check if cpu is idle
            if running_process is None:
                log_error(step_count, line, "no process is currently RUNNING")
            #if cpu is busy: running --> waiting
            else:
                proc = running_process
                proc.state = State.WAITING
                waiting_queue.append(running_process)
                running_process = None
                log_success(step_count, line, f"{proc.name}: RUNNING -> WAITING")
                


        elif command == "WAKE":
            #check if there's nothing in the waiting queue
            if len(waiting_queue) == 0:
                log_error(step_count, line, "no WAITING processes")
            #if there's something in the waiting queue: waiting --> ready
            else:
               proc = waiting_queue.popleft()
               proc.state = State.READY
               ready_queue.append(proc)
               log_success(step_count, line, f"{proc.name}: WAITING -> READY")
               
            

        elif command == "EXIT":
            if running_process is None:
                log_error(step_count, line, "no process is currently RUNNING")
            else:
                running_process.state = State.TERMINATED
                log_success(step_count, line, f"{running_process.name}: RUNNING -> TERMINATED")
                running_process = None
            
        elif command == "STATUS":
            log_success(step_count, line, "")
            print_status()
        elif command == "KILL":
            name = parts[1]
            #check if process exists or if process is already terminated, else kill it and remove from whatever queue it's in
            if name not in process_table:
                log_error(step_count, line, f"Process {name} does not exist")
            elif process_table[name].state == State.TERMINATED:
                log_error(step_count, line, f"Process {name} is already TERMINATED")
            else:
                proc = process_table[name]
                old_state = proc.state
                msg_extra = ""

                if old_state == State.READY:
                    ready_queue.remove(proc)
                    msg_extra = "(removed from READY)"
                elif old_state == State.WAITING:
                    waiting_queue.remove(proc)
                    msg_extra = "(removed from WAITING)"
                elif old_state == State.RUNNING:
                    running_process = None
                    msg_extra = "(CPU now NONE)"

                proc.state = State.TERMINATED
                log_success(step_count, line, f"{proc.name}: {old_state.name} -> TERMINATED {msg_extra}")
        

        if step_count % auto_status_interval == 0:
            print_status()
    print("--- END LOG ---")
if __name__ == "__main__":
    main()