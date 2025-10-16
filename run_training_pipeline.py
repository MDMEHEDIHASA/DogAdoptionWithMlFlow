import logging

from steps.util import load_data
from steps.train_model import train_model
from steps.evaluate_model import evaluate_model
from pipelines.training_pipeline import train_pipeline

logging.basicConfig(level=logging.DEBUG)


def run_training():
    training = train_pipeline(
        load_data(),
        train_model(),
        evaluate_model(),
    )

    training.run()


if __name__ == "__main__":
    run_training()