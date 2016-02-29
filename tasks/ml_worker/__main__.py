import logging
import time

if __name__ == "__main__":

    logging.info("Starting the ML worker")

    from app import app, db
    import ml_worker

    while True:
        ml_worker.work()
        time.sleep(1)