from config.settings import print_trans_info, print_daemons_info


def pr_trans(text, end="\n", sep=" "):
    if print_trans_info:
        print(f"\nTRANS LOGS >>>>>>>>>> {text}\n", end=end, sep=sep)


def pr_daemon(text, end="\n", sep=" "):
    """Prints "logs" / info if flag is True. Only for thread-related logs"""
    if print_daemons_info:
        print(f"\nDAEMONS LOGS >>>>>>>>>> {text}\n", end=end, sep=sep)