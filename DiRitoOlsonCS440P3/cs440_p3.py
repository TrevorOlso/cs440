"""
CS 440 - Operating Systems
Project 3 - CPU Scheduling Simulation
Names: Tobias DiRito, Trevor Olson
Date: 2026-03-14

"""
import random
import math

random_seed = 0
num_processes = 0
last_arrival_t = 0
maximum_burst_t = 0
RR_quantum = 0
context_switch_latency = 0
processes = []

# process object
class Process():
    def __init__(self, name, arrival, burst):
        self.name = name
        self.arrival = arrival
        self.burst = burst

# FCFS
def FCFS():
    print("\nFCFS:")

    fcfs_queue = sorted(processes, key=lambda p: p.arrival)
    current_time = 0
    context_switches = 0
    sum_response = 0
    sum_wait = 0

    for i, p in enumerate(fcfs_queue):
        if current_time < p.arrival:
            current_time = p.arrival
        if i > 0:
            context_switches += 1
            if context_switch_latency > 0:
                print(f"@t={current_time}, context switch {context_switches} occurs")
                current_time += context_switch_latency
        first_start = current_time
        print(f"@t={current_time}, {p.name} selected for {p.burst} units")
        current_time += p.burst
        completion = current_time
        response_time = first_start - p.arrival
        waiting_time = completion - p.arrival - p.burst

        sum_response += response_time
        sum_wait += waiting_time
        if i == num_processes - 1:
            print(f"@t={current_time}, all processes complete.")
    print(f"Completed in {current_time} cycles.")
    avg_response = sum_response / num_processes
    avg_wait = sum_wait / num_processes

    print(f"Average response time = {avg_response:.2f}")
    print(f"Average waiting time = {avg_wait:.2f}")
    
    return current_time, avg_wait, avg_response
# SJF
def SJF():
    print("\nSJF:")
    incomplete_processes = processes.copy()
    current_time = 0
    context_switches = 0
    sum_response = 0
    sum_wait = 0

    while len(incomplete_processes) > 0:
        # take all processes that have arrived by current cpu time
        sjf_queue = [p for p in incomplete_processes if p.arrival <= current_time] 

        # check if no processes have arrived, update current time, and restart loop
        if len(sjf_queue) == 0:
            incomplete_processes.sort(key=lambda p: p.arrival)
            current_time = incomplete_processes[0].arrival
            continue

        #sort by burst time, then arrival time for tiebreaker if burst is equal
        sjf_queue.sort(key=lambda p: (p.burst, p.arrival))
        active_process = sjf_queue[0]

        # perform context switch if necessary
        if len(incomplete_processes) < num_processes:
            context_switches += 1
            if context_switch_latency > 0:
                print(f"@t={current_time}, context switch {context_switches} occurs")
                current_time += context_switch_latency

        # set timestamps for calculations
        first_start = current_time
        print(f"@t={current_time}, {active_process.name} selected for {active_process.burst} units")
        current_time += active_process.burst
        completion = current_time
        response_time = first_start - active_process.arrival
        wait_time = completion - active_process.arrival - active_process.burst

        sum_response += response_time
        sum_wait += wait_time

        # remove process from incomplete queue and repeat
        incomplete_processes.remove(active_process)
        
    print(f"@t={current_time}, all processes complete.")        
    print(f"Completed in {current_time} cycles.")
    avg_response = sum_response / num_processes
    avg_wait = sum_wait / num_processes
    print(f"Average response time = {avg_response:.2f}")
    print(f"Average waiting time = {avg_wait:.2f}")


# SRTF
def SRTF():
    pass

# RR
def RR(random_seed, num_processes, last_arrival_t, maximum_burst_t, context_switch_latency, RR_quantum):
    pass

# Random Selection
def RS(random_seed, num_processes, last_arrival_t, maximum_burst_t, context_switch_latency):
    pass

#user input error detection
def try_input(var, s):
    while True:
        try:
            var = int(input(s))
            return var
        except ValueError:
            print("Invalid input! Please enter an integer")


def main():
    global random_seed, num_processes, last_arrival_t, maximum_burst_t, RR_quantum, context_switch_latency, processes
    
    
    random_seed = try_input(random_seed, "Enter random seed: ")
    num_processes = try_input(num_processes, "Enter number of processes (2-10): ")
    last_arrival_t = try_input(last_arrival_t, "Enter last arrival time (0-99): ")
    maximum_burst_t = try_input(maximum_burst_t, "Enter maximum burst time (1-100): ")
    RR_quantum = try_input(RR_quantum, "Enter RR quantum (1-100): ")
    context_switch_latency = try_input(context_switch_latency, "Enter context-switch latency (0-10): ")

    random.seed(random_seed)

    for i in range(1, num_processes + 1):
        arrival = random.randint(0, last_arrival_t)

        burst = random.randint(1, maximum_burst_t)

        name = f"P{i}"

        processes.append(Process(name, arrival, burst))
    




    for p in processes:
        print(f"{p.name}: arrival={p.arrival}, burst={p.burst}")

    print(f"Context-switch latency L={context_switch_latency}")
    print(f"RR quantum q={RR_quantum}")

    FCFS()
    SJF()

    
    

if __name__ == "__main__":
    main()







"""
    # for testing harris' example 1 (comment out all code above in main function to test and insert code below):
    processes.append(Process("P1", 0, 5))
    processes.append(Process("P2", 1, 3))
    processes.append(Process("P3", 2, 6))
    context_switch_latency = 1
    RR_quantum = 2
    num_processes = 3
"""