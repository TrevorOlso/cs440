import random
import string
# globals
page_ref_pattern_len = 0
num_unique_pages = 0
num_cache_slots = 0
rand_seed = 0
page_pool = []
reference_list = []





def get_valid_input(prompt, min_val, max_val):
    while True:
        try:
            value = int(input(prompt))
            if min_val <= value <= max_val:
                print(value)
                return value
            else:
                print(f"Please enter a number between {min_val} and {max_val}.")
        except ValueError:
            print("Invalid input. Please enter an integer.")


def FIFO(reference_string, num_slots):
    cache = [None] * num_slots
    fifo_pointer = 0
    hits = 0
    history_grid = [[' ' for _ in range(len(reference_string))] for _ in range(num_slots)]
    hit_markers = ['-' for _ in range(len(reference_string))]
    print("\nSimulating FIFO:")
    for t, page in enumerate(reference_string):
        if page in cache:
            hits += 1
            hit_markers[t] = '+'
        else:
            cache[fifo_pointer] = page
            fifo_pointer = (fifo_pointer + 1) % num_slots
        for s in range(num_slots):
            if cache[s] is not None:
                history_grid[s][t] = cache[s]
    ref_str_formatted = " ".join(reference_string)
    print(f"Ref Str: {ref_str_formatted}")
    prefix_length = 9
    for s in range(num_slots):
        row_prefix = f"FIFO {s+1}:".ljust(prefix_length)
        row_history = " ".join(history_grid[s])
        print(f"{row_prefix}{row_history}")
    hit_str = " ".join(hit_markers)
    print(" " * prefix_length + hit_str)
    hit_rate = hits / len(reference_string)
    print(f"\nFIFO Total Hits: {hits}")
    print(f"FIFO Hit Rate: {hit_rate:.2f}")
    return hits

def main():
    global page_ref_pattern_len, num_cache_slots, num_unique_pages, rand_seed, page_pool, reference_list
    page_ref_pattern_len = get_valid_input("Enter page reference pattern length: ", 10, 100)
    num_unique_pages = get_valid_input("Enter number of unique pages: ", 2, 15)
    num_cache_slots = get_valid_input("Enter number of slots: ", 2, 10)
    while True:
        try:
            rand_seed = int(input("Enter a seed: "))
            break
        except ValueError:
            print("Invalid input. Please enter an integer.")
    random.seed(rand_seed)
    page_pool = list(string.ascii_uppercase[:num_unique_pages])
    reference_list = random.choices(page_pool, k=page_ref_pattern_len)
    ref_string_formatted = " ".join(reference_list)
    print("\nRef Str:", ref_string_formatted)
    FIFO(reference_list, num_cache_slots)



if __name__ == "__main__":
    main()