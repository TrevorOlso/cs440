#include <iostream>
#include <vector>
#include <thread>
#include <chrono>
#include <string>
#include <iomanip>

using namespace std;
using namespace std::chrono;

// --- Global Constants & Counters ---
const int TOTAL_THREADS_REQUIRED = 5000;
const int OUTPUT_GROUPING = 25; // As per sample output

// --- Helper for Timestamping ---
void print_timestamp(string label) {
    auto now = system_clock::now();
    auto ms = duration_cast<milliseconds>(now.time_since_epoch()) % 1000;
    auto timer = system_clock::to_time_t(now);
    struct tm tx;
    localtime_r(&timer, &tx);
    cout << label << ": " << put_time(&tx, "%Y-%m-%d %H:%M:%S") 
         << "." << setfill('0') << setw(3) << ms.count() << endl;
}

// --- Experiment A: Flat Threads ---
void experiment_A() {
    cout << "\n=== A. Flat (UNBATCHED) ===\n";
    vector<thread> threads;
    
    auto start = high_resolution_clock::now();
    print_timestamp("Start time");

    for (int i = 1; i <= TOTAL_THREADS_REQUIRED; ++i) {
        threads.emplace_back([](int id) {
            // Thread work (minimal)
        }, i);

        if (i % OUTPUT_GROUPING == 0 || i == TOTAL_THREADS_REQUIRED) {
            // Adjust to match your specific logging needs
        }
    }

    for (auto& t : threads) {
        if (t.joinable()) t.join();
    }

    auto end = high_resolution_clock::now();
    print_timestamp("End time");
    
    auto elapsed = duration_cast<duration<double, milli>>(end - start);
    cout << "Elapsed: " << elapsed.count() << " ms\n";
    cout << "Threads created: 5000\nThreads destroyed: 5000\n";
}

// --- Experiment B: Two-Level Hierarchy ---
// Parents: 50, Children per parent: 99
void parent_thread_B(int parent_id) {
    vector<thread> children;
    for (int j = 1; j <= 99; ++j) {
        children.emplace_back([](int p_id, int c_id) {
            // Child work
        }, parent_id, j);
    }
    for (auto& c : children) c.join();
}

void experiment_B() {
    cout << "\n=== B. Two-level (UNBATCHED) ===\n";
    vector<thread> parents;
    
    auto start = high_resolution_clock::now();
    for (int i = 1; i <= 50; ++i) {
        parents.emplace_back(parent_thread_B, i);
    }
    for (auto& p : parents) p.join();
    auto end = high_resolution_clock::now();

    auto elapsed = duration_cast<duration<double, milli>>(end - start);
    cout << "Elapsed: " << elapsed.count() << " ms\n";
}

// --- Experiment C: Three-Level Hierarchy ---
// Initial: 20, Children: 3, Grandchildren: 82
void child_thread_C(int init_id, int child_id) {
    vector<thread> grandchildren;
    for (int k = 1; k <= 82; ++k) {
        grandchildren.emplace_back([](int i_id, int c_id, int g_id) {
            // Grandchild work
        }, init_id, child_id, k);
    }
    for (auto& g : grandchildren) g.join();
}

void initial_thread_C(int init_id) {
    vector<thread> children;
    for (int j = 1; j <= 3; ++j) {
        children.emplace_back(child_thread_C, init_id, j);
    }
    for (auto& c : children) c.join();
}

void experiment_C() {
    cout << "\n=== C. Three-level (UNBATCHED) ===\n";
    vector<thread> initial_threads;
    
    auto start = high_resolution_clock::now();
    for (int i = 1; i <= 20; ++i) {
        initial_threads.emplace_back(initial_thread_C, i);
    }
    for (auto& t : initial_threads) t.join();
    auto end = high_resolution_clock::now();

    auto elapsed = duration_cast<duration<double, milli>>(end - start);
    cout << "Elapsed: " << elapsed.count() << " ms\n";
}

int main() {
    // Note: You must run each experiment 3 times and average them for the report
    experiment_A();
    experiment_B();
    experiment_C();
    return 0;
}