/*
 * CS 440 Project 2 � POSIX (pthreads) TEMPLATE
 * Name(s): Tobias DiRito, Trevor Olson
 * Date: 02/23/2026
 *
 * Goal: Implement 2.a / 2.b / 2.c so that EACH experiment creates/destroys
 * exactly N_TOTAL threads (including all parent/initial/child/grandchild threads).
 *
 * Includes:
 *  - skeleton runners for 2.a, 2.b, 2.c (non-batched)
 *  - skeleton runners for batching fallback
 *
 * Students: Fill in TODO blocks. Keep printing sparse.
 *
 * Build:
 *   cc -O2 -Wall -Wextra -pedantic -pthread project2_posix_template.c -o project2
 */

#define _POSIX_C_SOURCE 200809L

#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdatomic.h>
#include <time.h>
#include <errno.h>
#include <string.h>

// ======= Fixed baseline (A, B, C must match) =======
enum { N_TOTAL = 5000 };

// ======= 2.b parameters (must total exactly 5000) =======
// VERIFIED
enum { B_PARENTS = 50, B_CHILDREN_PER_PARENT = 99 }; 


// ======= 2.c parameters (must total exactly 5000) =======
// VERIFIED
enum { C_INITIALS = 20, C_CHILDREN_PER_INITIAL = 3, C_GRANDCHILDREN_PER_CHILD = 82 }; 

// ======= Batching knobs (reduce concurrency if needed) =======
enum { A_BATCH_SIZE = 25, B_CHILD_BATCH_SIZE = 25, C_GRANDCHILD_BATCH_SIZE = 25 };

// ======= Counters =======
static atomic_int g_created = 0;
static atomic_int g_destroyed = 0;

// ------------------------------------------------------------
// Timing (POSIX monotonic clock)
// ------------------------------------------------------------
static long long now_ns(void) {
    struct timespec ts;
    // TODO: handle error if clock_gettime fails (rare)
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (long long)ts.tv_sec * 1000000000LL + (long long)ts.tv_nsec;
}

static void reset_counts(void) {
    atomic_store(&g_created, 0);
    atomic_store(&g_destroyed, 0);
}

static void print_summary(const char *label, long long start_ns, long long end_ns) {
    double elapsed_ms = (end_ns - start_ns) / 1e6;
    printf("%s elapsed: %.3f ms\n", label, elapsed_ms);
    printf("\nThreads created:   %d\n", atomic_load(&g_created));
    printf("Threads destroyed: %d\n", atomic_load(&g_destroyed));
}

// ------------------------------------------------------------
// Error helper
// ------------------------------------------------------------
static void die_pthread(int rc, const char *where) {
    if (rc == 0) return;
    fprintf(stderr, "ERROR: %s: %s\n", where, strerror(rc));
    exit(EXIT_FAILURE);
}

// ============================================================
// 2.a � Flat workers
// ============================================================
typedef struct {
    int id; // optional
} flat_arg_t;

static void *flat_worker(void *arg) {
    (void)arg;
    // TODO: optional minimal work
    // TODO: optional sparse print using id
    atomic_fetch_add(&g_destroyed, 1);
    return NULL;
}

// ============================================================
// 2.a � Flat (no batching)
// ============================================================
static void run2a_flat_no_batching(void) {
    printf("\n=== A. Flat (UNBATCHED) ===\n");
    printf("N_TOTAL: %d\n", N_TOTAL);
    printf("Output grouping: %d threads\n", A_BATCH_SIZE);
    long long start = now_ns();
    printf("\nStart time: %lld ns\n\n", start);
    // allocate pthread_t array of size N_TOTAL
    
    pthread_t *ths = (pthread_t*) malloc(sizeof(pthread_t) * N_TOTAL);
    // allocate args array or reuse one per thread
    flat_arg_t *args = (flat_arg_t*) malloc(sizeof(flat_arg_t) * N_TOTAL);

    // loop i = 0..N_TOTAL-1

    for (int i = 0; i < N_TOTAL; i++) {
        int t_id = i + 1; // thread IDs 1 to 5000
        
        // Print the grouping header every 25 threads
        if (t_id % 25 == 1) {
            int end_id = t_id + 24;
            if (end_id > N_TOTAL) end_id = N_TOTAL;
            printf("Created threads:    %d-%d\n", t_id, end_id);
        }

        args[i].id = i + 1;
        atomic_fetch_add(&g_created, 1);

        int rc = pthread_create(&ths[i], NULL, flat_worker, &args[i]);
        die_pthread(rc, "pthread_create failed");
    }

    // join all threads 
    printf("\n");
    for (int i = N_TOTAL - 1; i >= 0; i--) {
        int t_id = i + 1;
        
        // Print the grouping header every 25 threads, counting backwardss
        if (t_id % 25 == 0) {
            int start_id = t_id - 24;
            if (start_id < 1) start_id = 1;
            printf("Joined threads:     %d-%d\n", t_id, start_id);
        }

        pthread_join(ths[i], NULL);
    }
    

    // free allocations

    free(ths);
    free(args);

    long long end = now_ns();
    printf("\nEnd time: %lld ns\n", end);
    print_summary("Time", start, end);

    // verify created == destroyed == N_TOTAL

    int final_created = atomic_load(&g_created);
    int final_destroyed = atomic_load(&g_destroyed);
    if (final_created != N_TOTAL || final_destroyed != N_TOTAL) {
        fprintf(stderr, "ERROR: Count mismatch! Created: %d, Destroyed: %d, Expected: %d\n", 
            final_created, final_destroyed, N_TOTAL);
    }
}



// ============================================================
// 2.b � Two-level hierarchy (parent -> children)
// ============================================================
typedef struct {
    int parent_id;
    // TODO: optional fields for sparse printing
} parent_arg_t;

static void *child_worker_2b(void *arg) {
    (void)arg;
    // TODO: minimal work
    atomic_fetch_add(&g_destroyed, 1);
    return NULL;
}

static void *parent_worker_2b_no_batching(void *arg) {
    parent_arg_t *pa = (parent_arg_t *)arg;
    int p_id = pa->parent_id;
    printf("Parent %d started\n", p_id);

    // create B_CHILDREN_PER_PARENT child threads
    //   - allocate pthread_t children[B_CHILDREN_PER_PARENT]
    //   - loop child_id: atomic_fetch_add(&g_created, 1); pthread_create(...)
    
    pthread_t *children = (pthread_t *)malloc(sizeof(pthread_t) * B_CHILDREN_PER_PARENT);
    for (int i = 0; i < B_CHILDREN_PER_PARENT; i++) {
        int c_id = i + 1;

        if (c_id % 25 == 1) {
            int end_id = c_id + 24;
            if (end_id > B_CHILDREN_PER_PARENT) end_id = B_CHILDREN_PER_PARENT;
            printf("Parent %d created children: %d-%d ... %d-%d\n", p_id, p_id, c_id, p_id, end_id);

        }

        atomic_fetch_add(&g_created, 1);

        int rc = pthread_create(&children[i], NULL, child_worker_2b, NULL);
        die_pthread(rc, "Child create failed");
    }

    // join all children

    printf("Parent %d joined children: %d-%d ... %d-1\n", p_id, p_id, B_CHILDREN_PER_PARENT, p_id);
    // join in revesrse order
    for (int i = B_CHILDREN_PER_PARENT - 1; i >= 0; i--) {
        pthread_join(children[i], NULL);
    }

    // free pa if heap-allocated

    free(children);
    printf("Parent %d completed\n", p_id);

    atomic_fetch_add(&g_destroyed, 1); // parent destroyed
    return NULL;
}

static void run2b_two_level_no_batching(void) {
    printf("\n=== B. Two-level (UNBATCHED) ===\n");
    printf("Parents: %d\n", B_PARENTS);
    printf("Children per parent: %d\n", B_CHILDREN_PER_PARENT);
    printf("Output grouping: %d threads\n", B_CHILD_BATCH_SIZE);
    printf("Total threads: %d\n", N_TOTAL);
    long long start = now_ns();
    printf("\nStart time: %lld ns\n\n", start);
    // allocate pthread_t parents[B_PARENTS]
    pthread_t *parents = (pthread_t *)malloc(sizeof(pthread_t) * B_PARENTS);
    parent_arg_t *p_args = (parent_arg_t *)malloc(sizeof(parent_arg_t) * B_PARENTS);

    // for parent_id in 1..B_PARENTS:

    for (int i = 0; i < B_PARENTS; i++) {
        p_args[i].parent_id = i + 1;
        atomic_fetch_add(&g_created, 1);
        int rc = pthread_create(&parents[i], NULL, parent_worker_2b_no_batching, &p_args[i]);
        die_pthread(rc, "Parent create failed");
    }
    // join all parents
    for (int i = 0; i < B_PARENTS; i++) {
        pthread_join(parents[i], NULL);
    }
    // clean up arrays
    free(parents);
    free(p_args);

    long long end = now_ns();
    printf("\nEnd time: %lld ns\n", end);
    print_summary("Time", start, end);

    // verify created == destroyed == N_TOTAL

    if (atomic_load(&g_created) != N_TOTAL || atomic_load(&g_destroyed) != N_TOTAL) {
        fprintf(stderr, "ERROR: Count mismatch in 2.b!\n");
    }
}



// ============================================================
// 2.c � Three-level hierarchy (initial -> child -> grandchild)
// ============================================================
typedef struct {
    int initial_id;
} initial_arg_t;

typedef struct {
    int initial_id;
    int child_id;
    int grand_batch_size; // used for batched version
} child_arg_t;

static void *grandchild_worker_2c(void *arg) {
    (void)arg;
    // TODO: minimal work
    atomic_fetch_add(&g_destroyed, 1);
    return NULL;
}

static void *child_worker_2c_no_batching(void *arg) {
    child_arg_t *ca = (child_arg_t *)arg;
    int i_id = ca->initial_id;
    int c_id = ca->child_id;

    // create C_GRANDCHILDREN_PER_CHILD grandchild threads
    pthread_t *grandchildren = (pthread_t *)malloc(sizeof(pthread_t) * C_GRANDCHILDREN_PER_CHILD);

    for (int i = 0; i < C_GRANDCHILDREN_PER_CHILD; i++) {
        int g_id = i + 1;
        
        
        if (g_id % 25 == 1) {
            int end_id = g_id + 24;
            if (end_id > C_GRANDCHILDREN_PER_CHILD) end_id = C_GRANDCHILDREN_PER_CHILD;
            
            printf("Child %d-%d created grandchildren: %d-%d-%d ... %d-%d-%d\n", 
                   i_id, c_id, i_id, c_id, g_id, i_id, c_id, end_id);
        }

        atomic_fetch_add(&g_created, 1);
        
        
        int rc = pthread_create(&grandchildren[i], NULL, grandchild_worker_2c, NULL);
        die_pthread(rc, "Grandchild create failed");
    }

    printf("Child %d-%d joined grandchildren: %d-%d-%d ... %d-%d-1\n", 
           i_id, c_id, i_id, c_id, C_GRANDCHILDREN_PER_CHILD, i_id, c_id);
    // join all grandchildren
    for (int i = C_GRANDCHILDREN_PER_CHILD - 1; i >= 0; i--) {
        pthread_join(grandchildren[i], NULL);
    }
    // free ca if heap-allocated

    free(grandchildren);
    printf("Child %d-%d completed\n", i_id, c_id);

    atomic_fetch_add(&g_destroyed, 1); // child destroyed
    return NULL;
}

static void *initial_worker_2c_no_batching(void *arg) {
    initial_arg_t *ia = (initial_arg_t *)arg;
    int i_id = ia->initial_id;

    printf("Initial %d started\n", i_id);

    // create C_CHILDREN_PER_INITIAL child threads
    //   - each child runs child_worker_2c_no_batching
    pthread_t *children = (pthread_t *)malloc(sizeof(pthread_t) * C_CHILDREN_PER_INITIAL);
    child_arg_t *c_args = (child_arg_t *)malloc(sizeof(child_arg_t) * C_CHILDREN_PER_INITIAL);

    for (int i = 0; i < C_CHILDREN_PER_INITIAL; i++) {
        int c_id = i + 1;
        c_args[i].initial_id = i_id; 
        c_args[i].child_id = c_id;   
        
        printf("Initial %d created child: %d-%d\n", i_id, i_id, c_id);

        atomic_fetch_add(&g_created, 1);
        int rc = pthread_create(&children[i], NULL, child_worker_2c_no_batching, &c_args[i]);
        die_pthread(rc, "Child create failed in 2c");
    }
    // join all children
    for (int i = 0; i < C_CHILDREN_PER_INITIAL; i++) {
        pthread_join(children[i], NULL);
    }
    // free ia if heap-allocated
    free(children);
    free(c_args);

    printf("Initial %d completed\n", i_id);

    atomic_fetch_add(&g_destroyed, 1); // initial destroyed
    return NULL;
}

static void run2c_three_level_no_batching(void) {
    printf("\n=== C. Three-level (UNBATCHED) ===\n");
    printf("Initial threads: %d\n", C_INITIALS);
    printf("Children per initial: %d\n", C_CHILDREN_PER_INITIAL);
    printf("Grandchildren per child: %d\n", C_GRANDCHILDREN_PER_CHILD);
    printf("Output grouping: %d threads\n", C_GRANDCHILD_BATCH_SIZE);
    printf("Total threads: %d\n", N_TOTAL);
    long long start = now_ns();
    printf("\nStart time: %lld ns\n\n", start);

    // allocate pthread_t initials[C_INITIALS]
    pthread_t *initials = (pthread_t *)malloc(sizeof(pthread_t) * C_INITIALS);
    initial_arg_t *i_args = (initial_arg_t *)malloc(sizeof(initial_arg_t) * C_INITIALS);

    // for initial_id in 1..C_INITIALS:
    //   - atomic_fetch_add(&g_created, 1) // initial
    //   - allocate initial_arg_t
    //   - pthread_create -> initial_worker_2c_no_batching

    for (int i = 0; i < C_INITIALS; i++) {
        i_args[i].initial_id = i + 1;
        atomic_fetch_add(&g_created, 1);
        int rc = pthread_create(&initials[i], NULL, initial_worker_2c_no_batching, &i_args[i]);
        die_pthread(rc, "Initial create failed");
    }

    // join all initials

    for (int i = 0; i < C_INITIALS; i++){
        pthread_join(initials[i], NULL);
    }

    free(initials);
    free(i_args);

    long long end = now_ns();
    printf("\nEnd time: %lld ns\n", end);
    print_summary("Time", start, end);

    // verify created == destroyed == N_TOTAL

    if (atomic_load(&g_created) != N_TOTAL || atomic_load(&g_destroyed) != N_TOTAL) {
        fprintf(stderr, "ERROR: Count mismatch in 2.c!\n");
}
}



// ============================================================
// main
// ============================================================
int main(void) {
    // TODO: run 3 trials each and compute averages in your report.

    reset_counts();
    //run2a_flat_no_batching();
    // reset_counts();
    // run2a_flat_batched(A_BATCH_SIZE);

    reset_counts();
    //run2b_two_level_no_batching();
    // reset_counts();
    // run2b_two_level_batched(B_CHILD_BATCH_SIZE);

    reset_counts();
    run2c_three_level_no_batching();
    // reset_counts();
    // run2c_three_level_batched(C_GRANDCHILD_BATCH_SIZE);

    return 0;
}
