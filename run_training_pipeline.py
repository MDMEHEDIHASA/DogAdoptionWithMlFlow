import logging
import yaml
from steps.util import load_data
from steps.train_model import train_model
from steps.evaluate_model import evaluate_model
from pipelines.training_pipeline import train_pipeline

logging.basicConfig(level=logging.DEBUG)


def run_training():

    # Load configuration from YAML
    with open("steps/config.yaml", "r") as f:
        config = yaml.safe_load(f)

    training = train_pipeline(
        load_data(config),
        train_model(),
        evaluate_model(),
    )

    training.run()


if __name__ == "__main__":
    run_training()