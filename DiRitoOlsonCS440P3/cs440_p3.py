"""
CS 440 - Operating Systems
Project 3 - CPU Scheduling Simulation
Names: Tobias DiRito, Trevor Olson
Date: 2026-03-14
"""
import random

# --- GLOBALS ---
random_seed = 0
num_processes = 0
last_arrival_t = 0
maximum_burst_t = 0
RR_quantum = 0
context_switch_latency = 0
processes = []

class Process:
    def __init__(self, name, arrival, burst):
        self.name = name
        self.arrival = arrival
        self.burst = burst

# --- HELPER FUNCTIONS ---
def try_input(prompt_string, min_val, max_val):
    while True:
        try:
            val = int(input(prompt_string))
            if min_val <= val <= max_val:
                return val
            else:
                print(f"Error: Value must be between {min_val} and {max_val}.")
        except ValueError:
            print("Invalid input! Please enter an integer.")

def print_metrics(total_cycles, first_start, completion_t):
    sum_response = 0
    sum_wait = 0
    
    for p in processes:
        response_time = first_start[p.name] - p.arrival
        waiting_time = completion_t[p.name] - p.arrival - p.burst
        sum_response += response_time
        sum_wait += waiting_time

    avg_response = sum_response / num_processes
    avg_wait = sum_wait / num_processes
    
    print(f"Avg wait = {avg_wait:.2f}")
    print(f"Avg response = {avg_response:.2f}")
    
    return total_cycles, avg_wait, avg_response

# --- ALGORITHMS ---

def FCFS():
    print("\nFCFS Trace:")
    fcfs_queue = sorted(processes, key=lambda p: p.arrival)
    current_time = 0
    context_switches = 0
    first_start = {}
    completion_t = {}

    for i, p in enumerate(fcfs_queue):
        if current_time < p.arrival:
            current_time = p.arrival # Jump idle time
            
        if i > 0 and current_time >= fcfs_queue[i-1].arrival:
            context_switches += 1
            if context_switch_latency > 0:
                print(f"@t={current_time} context switch {context_switches} occurs")
                current_time += context_switch_latency

        first_start[p.name] = current_time
        print(f"@t={current_time} {p.name} runs {p.burst}")
        current_time += p.burst
        completion_t[p.name] = current_time

    print(f"Completed in {current_time} cycles.")
    return print_metrics(current_time, first_start, completion_t)

def SJF():
    print("\nSJF Trace:")
    incomplete = processes.copy()
    current_time = 0
    context_switches = 0
    first_start = {}
    completion_t = {}
    last_process = None

    while incomplete:
        ready = [p for p in incomplete if p.arrival <= current_time]
        if not ready:
            incomplete.sort(key=lambda p: p.arrival)
            current_time = incomplete[0].arrival
            last_process = None
            continue

        ready.sort(key=lambda p: (p.burst, p.arrival))
        active_process = ready[0]

        if last_process is not None and active_process.name != last_process:
            context_switches += 1
            if context_switch_latency > 0:
                print(f"@t={current_time} context switch {context_switches} occurs")
                current_time += context_switch_latency

        first_start[active_process.name] = current_time
        print(f"@t={current_time} {active_process.name} runs {active_process.burst}")
        current_time += active_process.burst
        completion_t[active_process.name] = current_time
        
        last_process = active_process.name
        incomplete.remove(active_process)

    print(f"Completed in {current_time} cycles.")
    return print_metrics(current_time, first_start, completion_t)

def SRTF():
    print("\nSRTF Trace:")
    remaining_t = {p.name: p.burst for p in processes}
    first_start = {p.name: -1 for p in processes}
    completion_t = {p.name: 0 for p in processes}
    
    current_time = 0
    context_switches = 0
    completed = 0
    last_process = None
    
    run_start_time = 0
    current_running_proc = None
    run_duration = 0
    
    def flush_print():
        nonlocal current_running_proc, run_start_time, run_duration
        if current_running_proc is not None and run_duration > 0:
            print(f"@t={run_start_time} {current_running_proc} runs {run_duration}")
        current_running_proc = None
        run_duration = 0

    while completed < num_processes:
        ready = [p for p in processes if p.arrival <= current_time and remaining_t[p.name] > 0]
        
        if not ready:
            flush_print()
            next_arr = min(p.arrival for p in processes if p.arrival > current_time and remaining_t[p.name] > 0)
            current_time = next_arr
            last_process = None
            continue
            
        min_rem = min(remaining_t[p.name] for p in ready)
        candidates = [p for p in ready if remaining_t[p.name] == min_rem]
        
        if last_process in [c.name for c in candidates]:
            best_proc = next(c for c in candidates if c.name == last_process)
        else:
            candidates.sort(key=lambda p: p.arrival)
            best_proc = candidates[0]
            
        if last_process is not None and best_proc.name != last_process:
            flush_print()
            context_switches += 1
            if context_switch_latency > 0:
                print(f"@t={current_time} context switch {context_switches} occurs")
                current_time += context_switch_latency
                last_process = best_proc.name
                continue
                
        if best_proc.name != current_running_proc:
            flush_print()
            current_running_proc = best_proc.name
            run_start_time = current_time
            
        if first_start[best_proc.name] == -1:
            first_start[best_proc.name] = current_time
            
        current_time += 1
        remaining_t[best_proc.name] -= 1
        run_duration += 1
        
        if remaining_t[best_proc.name] == 0:
            completion_t[best_proc.name] = current_time
            completed += 1
            
        last_process = best_proc.name

    flush_print()
    print(f"Completed in {current_time} cycles.")
    return print_metrics(current_time, first_start, completion_t)

def RR():
    print(f"\nRR Trace (q={RR_quantum}):")
    remaining_t = {p.name: p.burst for p in processes}
    first_start = {p.name: -1 for p in processes}
    completion_t = {p.name: 0 for p in processes}
    
    current_time = 0
    context_switches = 0
    completed = 0
    last_process = None
    queue = []
    
    while completed < num_processes:
        new_arrivals = [p for p in processes if p.arrival <= current_time and remaining_t[p.name] > 0 and p not in queue and p.name != last_process]
        new_arrivals.sort(key=lambda p: p.arrival)
        queue.extend(new_arrivals)
        
        if last_process is not None and remaining_t[last_process] > 0:
            proc_obj = next(p for p in processes if p.name == last_process)
            queue.append(proc_obj)

        if not queue:
            next_arr = min(p.arrival for p in processes if p.arrival > current_time and remaining_t[p.name] > 0)
            current_time = next_arr
            last_process = None
            continue

        active_process = queue.pop(0)

        if last_process is not None and active_process.name != last_process:
            context_switches += 1
            if context_switch_latency > 0:
                print(f"@t={current_time} context switch {context_switches} occurs")
                current_time += context_switch_latency
                new_arrivals = [p for p in processes if p.arrival <= current_time and remaining_t[p.name] > 0 and p not in queue and p.name != active_process.name and p.name != last_process]
                new_arrivals.sort(key=lambda p: p.arrival)
                queue.extend(new_arrivals)

        if first_start[active_process.name] == -1:
            first_start[active_process.name] = current_time

        run_time = min(RR_quantum, remaining_t[active_process.name])
        print(f"@t={current_time} {active_process.name} runs {run_time}")
        
        current_time += run_time
        remaining_t[active_process.name] -= run_time
        
        if remaining_t[active_process.name] == 0:
            completion_t[active_process.name] = current_time
            completed += 1
            last_process = None 
        else:
            last_process = active_process.name

    print(f"Completed in {current_time} cycles.")
    return print_metrics(current_time, first_start, completion_t)

def Random_Sched():
    print("\nRandom Trace (one possible order):")
    incomplete = processes.copy()
    current_time = 0
    context_switches = 0
    first_start = {}
    completion_t = {}
    last_process = None

    while incomplete:
        ready = [p for p in incomplete if p.arrival <= current_time]
        if not ready:
            incomplete.sort(key=lambda p: p.arrival)
            current_time = incomplete[0].arrival
            last_process = None
            continue

        active_process = random.choice(ready)

        if last_process is not None and active_process.name != last_process:
            context_switches += 1
            if context_switch_latency > 0:
                print(f"@t={current_time} context switch {context_switches} occurs")
                current_time += context_switch_latency

        first_start[active_process.name] = current_time
        print(f"@t={current_time} {active_process.name} runs {active_process.burst}")
        current_time += active_process.burst
        completion_t[active_process.name] = current_time
        
        last_process = active_process.name
        incomplete.remove(active_process)

    print(f"Completed in {current_time} cycles.")
    return print_metrics(current_time, first_start, completion_t)


def main():
    global random_seed, num_processes, last_arrival_t, maximum_burst_t, RR_quantum, context_switch_latency, processes
    
    random_seed = try_input("Enter random seed: ", -999999, 999999)
    num_processes = try_input("Enter number of processes (2-10): ", 2, 10)
    last_arrival_t = try_input("Enter last arrival time (0-99): ", 0, 99)
    maximum_burst_t = try_input("Enter maximum burst time (1-100): ", 1, 100)
    RR_quantum = try_input("Enter RR quantum (1-100): ", 1, 100)
    context_switch_latency = try_input("Enter context-switch latency (0-10): ", 0, 10)

    random.seed(random_seed)

    for i in range(1, num_processes + 1):
        arrival = random.randint(0, last_arrival_t)
        burst = random.randint(1, maximum_burst_t)
        processes.append(Process(f"P{i}", arrival, burst))
    
    print("\nExample process set:")
    for p in processes:
        print(f"{p.name}: arrival={p.arrival}, burst={p.burst}")

    print(f"Context-switch latency L = {context_switch_latency}")
    print(f"RR quantum q = {RR_quantum}")

    # Run Algorithms and collect checksum data
    results = []
    results.append(FCFS())
    results.append(SJF())
    results.append(SRTF())
    results.append(RR())
    results.append(Random_Sched())

    # Calculate Checksum
    totalCompletion = 0
    totalWait100 = 0
    totalResp100 = 0

    for completion_time, avg_wait, avg_response in results:
        totalCompletion += completion_time
        totalWait100 += round(avg_wait * 100)
        totalResp100 += round(avg_response * 100)

    checksum = totalCompletion + totalWait100 + totalResp100
    print(f"\nCHECKSUM: {checksum}")

if __name__ == "__main__":
    main()