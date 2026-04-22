# Tobias DiRito, Trevor Olson
# CS440 Project 4 Submission


import random
import string

# Algorithm ordering for consistent output 
ALGO_ORDER = ['FIFO', 'LRU', 'LFU', 'MIN', 'MRU', 'RAND']

# Items displayed per line before wrapping
WRAP = 40

# Input helpers

def get_valid_input(prompt, min_val, max_val):
    # Prompt until the user enters an integer in range [min_val, max_val]
    while True:
        try:
            value = int(input(prompt))
            if min_val <= value <= max_val:
                print(value)
                return value
            print(f"  Please enter a number between {min_val} and {max_val}.")
        except ValueError:
            print("  Invalid input. Please enter an integer.")


# Simulation helpers

def _make_history(n, num_slots):
    # creatse a blank grid to store cache history for correct printing
    history = [[' '] * n for _ in range(num_slots)]
    return history


def _snapshot(cache, history, t):
    # copy state of cachse into history grid
    for s, page in enumerate(cache):
        if page is not None:
            history[s][t] = page


# FIFO 

def simulate_fifo(ref, num_slots):
    cache = [None] * num_slots
    ptr = 0          # next slot to be evicted (circular)
    filled = 0
    hits = 0
    n = len(ref)
    history = _make_history(n, num_slots)
    markers = []

    for t, page in enumerate(ref):
        if page in cache: # check if the page is already in the cache and then marks it as a "hit"
            hits += 1
            markers.append('+')
        else:
            if filled < num_slots:           # inserts page into cache if there is available space
                slot = filled
                filled += 1
            else:                            # if no space available and the page is not already in the cache, runs fifo to evict the first one in
                slot = ptr
                ptr = (ptr + 1) % num_slots
            cache[slot] = page
            markers.append('-')
        _snapshot(cache, history, t)

    return history, markers, hits


# LRU 

def simulate_lru(ref, num_slots):
    cache    = [None] * num_slots
    last_used = [-1]  * num_slots   # time of last access per slot
    filled = 0
    hits = 0
    n = len(ref)
    history = _make_history(n, num_slots)
    markers = []

    for t, page in enumerate(ref):
        # same logic if page is already in cache or if there is empty space
        if page in cache: 
            hits += 1
            markers.append('+')
            slot = cache.index(page)
            last_used[slot] = t # updates last access time of slot to current time step
        else:
            if filled < num_slots:
                slot = filled
                filled += 1
            else:
                # LRU logic, looks at all slot indices to find one with smallest last_used value and then evicts said page
                slot = min(range(num_slots), key=lambda i: last_used[i])
            cache[slot] = page
            last_used[slot] = t
            markers.append('-')
        _snapshot(cache, history, t)

    return history, markers, hits


# LFU 
#   Tie-break 1: LRU among tied pages
#   Tie-break 2: lowest slot number

def simulate_lfu(ref, num_slots):
    cache     = [None] * num_slots
    freq      = [0]    * num_slots   # tracks number of accesses for each slot 
    last_used = [-1]   * num_slots # same as LRU, tracks last access time which is used for a tie breaker. 
    filled = 0
    hits = 0
    n = len(ref)
    history = _make_history(n, num_slots)
    markers = []

    for t, page in enumerate(ref):
        if page in cache:
            hits += 1
            markers.append('+')
            slot = cache.index(page)
            freq[slot]      += 1 # increase frequency count for a page hit 
            last_used[slot]  = t # updates access time same as LRU
        else:
            if filled < num_slots:
                slot = filled
                filled += 1
            else: # LFU logic, finds the page with the lowest frequency in the cache
                min_freq   = min(freq)
                candidates = [i for i in range(num_slots) if freq[i] == min_freq] # creates a list of identical frequencies to determine if a tie breaker is necessary
                if len(candidates) == 1:
                    slot = candidates[0]
                else:
                    # LRU tiebreak
                    min_lu     = min(last_used[i] for i in candidates)
                    lru_cands  = [i for i in candidates if last_used[i] == min_lu]
                    slot = lru_cands[0]   # lowest slot number wins any remaining tie
            cache[slot]     = page
            freq[slot]      = 1    # reset count for new occupant
            last_used[slot] = t
            markers.append('-')
        _snapshot(cache, history, t)

    return history, markers, hits


# MIN (Optimal)

def simulate_min(ref, num_slots):
    cache  = [None] * num_slots
    filled = 0
    hits   = 0
    n      = len(ref)
    history = _make_history(n, num_slots)
    markers = []

    for t, page in enumerate(ref):
        if page in cache:
            hits += 1
            markers.append('+')
        else:
            if filled < num_slots:
                slot = filled
                filled += 1
            else:
                # Compute next-use distance for every cached page
                future = []
                for s in range(num_slots): #loops every current cached page
                    try:
                        next_use = ref.index(cache[s], t + 1) # searches the reference string to find when the page will be used again.
                    except ValueError:
                        next_use = float('inf')   # never used again
                    future.append(next_use)

                max_fut    = max(future)
                candidates = [i for i in range(num_slots) if future[i] == max_fut]
                slot = candidates[0] # swaps out page with most distance before next use (handles tiebreaker by just picking first one in list)
            cache[slot] = page
            markers.append('-')
        _snapshot(cache, history, t)

    return history, markers, hits


# MRU 

def simulate_mru(ref, num_slots):
    cache     = [None] * num_slots
    last_used = [-1]   * num_slots # same as LRU
    filled = 0
    hits   = 0
    n      = len(ref)
    history = _make_history(n, num_slots)
    markers = []

    for t, page in enumerate(ref):
        if page in cache:
            hits += 1
            markers.append('+')
            slot = cache.index(page)
            last_used[slot] = t
        else:
            if filled < num_slots:
                slot = filled
                filled += 1
            else:
                # Evict most recently used slot by taking max of last used, instead of min
                slot = max(range(num_slots), key=lambda i: last_used[i])
            cache[slot]     = page
            last_used[slot] = t
            markers.append('-')
        _snapshot(cache, history, t)

    return history, markers, hits


# RAND
# uses the shared random state so results are reproducible with the seed.

def simulate_rand(ref, num_slots):
    cache  = [None] * num_slots
    filled = 0
    hits   = 0
    n      = len(ref)
    history = _make_history(n, num_slots)
    markers = []

    for t, page in enumerate(ref):
        if page in cache:
            hits += 1
            markers.append('+')
        else:
            if filled < num_slots:
                slot = filled
                filled += 1
            else:
                slot = random.randint(0, num_slots - 1)
            cache[slot] = page
            markers.append('-')
        _snapshot(cache, history, t)

    return history, markers, hits


# for printing out results

def display_results(ref, results, num_slots, wrap=WRAP):
    # print all algorithm states aligned with the reference string.
    # long sequences are wrapped every `wrap` items for readability.
    n = len(ref)

    # Compute a uniform column-prefix width 
    max_algo_w = max(len(a) for a in ALGO_ORDER)          # 4  (FIFO / RAND)
    slot_w     = len(str(num_slots))                       # 1 or 2
    prefix_len = 1 + max_algo_w + 1 + slot_w + 2

    ref_prefix = "Ref Str:".ljust(prefix_len)

    print()
    for start in range(0, n, wrap):
        end   = min(start + wrap, n)
        chunk = ref[start:end]

        # Reference string
        print(ref_prefix + " ".join(chunk))

        # Each algorithm
        for algo in ALGO_ORDER:
            if algo not in results:
                continue
            history, markers, _ = results[algo]

            for s in range(num_slots):
                label = f" {algo:<{max_algo_w}} {s + 1:>{slot_w}}:".ljust(prefix_len)
                row   = " ".join(history[s][start:end])
                print(label + row)

            hit_row = " ".join(markers[start:end])
            print(" " * prefix_len + hit_row)
            print()                           # blank line between algorithms

    # Hit-rate statistics
    print("Cache Hit Rates:")
    hit_rates = {}
    for algo in ALGO_ORDER:
        if algo not in results:
            continue
        _, _, hits = results[algo]
        rate = hits / n
        hit_rates[algo] = rate
        print(f"{algo:<6}: {hits} / {n} = {rate:.2f}")

    max_rate = max(hit_rates.values())
    min_rate = min(hit_rates.values())
    best     = [a for a, r in hit_rates.items() if r == max_rate]
    worst    = [a for a, r in hit_rates.items() if r == min_rate]

    if len(best) == 1:
        print(f"Best Algorithm: {best[0]}")
    else:
        print(f"Best Algorithm(s): {', '.join(best)} (tie)")

    if len(worst) == 1:
        print(f"Worst Algorithm: {worst[0]}")
    else:
        print(f"Worst Algorithm(s): {', '.join(worst)} (tie)")


# Main

def main():
    
    ref_len   = get_valid_input("Enter page reference pattern length: ", 10, 100)
    num_pages = get_valid_input("Enter number of unique pages: ", 2, 15)
    num_slots = get_valid_input("Enter number of slots: ", 2, 10)

    while True:
        try:
            seed = int(input("Enter a seed: "))
            print(seed)
            break
        except ValueError:
            print("  Invalid input. Please enter an integer.")

    # Generate reference string
    random.seed(seed)
    
    page_pool = list(string.ascii_uppercase[:num_pages])
    ref       = random.choices(page_pool, k=ref_len)

    # Run all algorithms
    # RAND uses random.randint and shares the same state
    # are fully reproducible for a given seed.
    
    results = {
        'FIFO': simulate_fifo(ref, num_slots),
        'LRU':  simulate_lru (ref, num_slots),
        'LFU':  simulate_lfu (ref, num_slots),
        'MIN':  simulate_min (ref, num_slots),
        'MRU':  simulate_mru (ref, num_slots),
        'RAND': simulate_rand(ref, num_slots),
    }

    display_results(ref, results, num_slots)


if __name__ == "__main__":
    main()