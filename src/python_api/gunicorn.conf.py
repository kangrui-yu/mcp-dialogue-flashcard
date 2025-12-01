import multiprocessing

bind = "0.0.0.0:8081"
workers = multiprocessing.cpu_count() // 2 or 1
threads = 4
timeout = 30
