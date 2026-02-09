1. BearID Auto-STATUS Rule
    Trevor last digit - 6
    Tobias last digit - 1
    Auto-STATUS interval - 9
2. Error Handling
    [step=4] CMD=WAKE P1 | ERROR | no WAITING processes
    The command WAKE was illegal at this point because there was no process in the 
    waiting queue. If BLOCK was performed on a running process before this command, it would
    have been legal (a proccess would have been in waiting) but due to no commands that would
    send a process to the waiting queue, it could not be performed.
3. Process Lifecycle
    Process P1:
    P1 was created with the first command and moved from NEW to READY.
    At step 5, P1 was moved to RUNNING due to a DISPATCH command that took it from the front of the ready queue.
    At step 7, P1 was moved from RUNNING to WAITING due to a BLOCK command.
    At step 13, P1 was moved from WAITING to READY due to a WAKE command.
    At step 16, P1 was moved from READY to RUNNING due to a DISPATCH command and it was removed from the front of the queue. It was at the front of the queue because all other proccesses had been dispatched and blocked/exited.
    At step 18, P1 was moved from RUNNING to TERMINATED due to an EXIT command that was valid because P1 was running.
4. Kill command
    Our KILL command first checks if the process exists or if the process is already terminated (and logs an error) before moving onto killing the process.
    It then identifies the process and the process state in local variables called proc and old_state.
    If the process state is READY, it removes the process from the ready queue.
    If the process state is WAITING, it removes it from the waiting queue.
    If the process state is RUNNING, it sets the running_process variable to None thus removing it from the running state.
    It then changes the process state to TERMINATED and logs a success.
    