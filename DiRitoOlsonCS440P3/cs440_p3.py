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
def FCFS(random_seed, num_processes, last_arrival_t, maximum_burst_t, context_switch_latency):
    pass

# SJF
def SJF(random_seed, num_processes, last_arrival_t, maximum_burst_t, context_switch_latency):
    pass

# SRTF
def SRTF(random_seed, num_processes, last_arrival_t, maximum_burst_t, context_switch_latency):
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
    
    

if __name__ == "__main__":
    main()
