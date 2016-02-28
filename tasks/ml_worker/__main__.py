import logging

if __name__ == "__main__":

  logging.info("Starting the ML worker")

  from app import app, db
  import ml_worker

  ml_worker.work()