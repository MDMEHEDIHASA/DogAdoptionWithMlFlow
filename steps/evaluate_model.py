"""
ZenML Steps for Dog Breed Classification Pipeline - Model Evaluation
"""

import yaml
import logging
import mlflow
import numpy as np
import tensorflow as tf

from zenml.steps import step, Output
from util import load_config, load_data
from model.evaluator import DogBreedEvaluator

logging.basicConfig(level=logging.INFO)


@step(experiment_tracker="mlflow_tracker")
def evaluate_model(
    config_path: str = 'config.yaml',
    model_path: str = None
) -> Output(
    accuracy=float,
    precision=float,
    recall=float,
    f1=float
):  # type: ignore
    """
    Evaluate trained model on validation/test dataset.
    
    Args:
        config_path (str): Path to configuration file
        model_path (str): Path to saved model (if None, loads from MLflow)
        
    Returns:
        tuple: (accuracy, precision, recall, f1)
    """
    logging.info("Beginning model evaluation...")
    config = load_config(config_path)

    try:
        # Load data
        logging.info("Loading validation dataset...")
        train_ds, val_ds, class_names, num_classes = load_data(
            config=config,
            format_labels=True
        )
        
        # Load the trained model
        logging.info("Loading trained model...")
        if model_path:
            # Load from file path
            model = tf.keras.models.load_model(model_path)
            logging.info(f"Model loaded from {model_path}")
        else:
            # Load from MLflow
            model_uri = mlflow.get_artifact_uri("model")
            model = mlflow.keras.load_model(model_uri)
            logging.info(f"Model loaded from MLflow: {model_uri}")
        
        # Initialize evaluator with model and class names
        evaluator = DogBreedEvaluator(model=model, class_names=class_names)
        
        # Evaluate on validation dataset
        logging.info("Evaluating model on validation set...")
        metrics = evaluator.evaluate_dataset(val_ds)
        
        # Print results
        evaluator.print_results()
        evaluator.print_classification_report()
        
        # Log additional metrics
        top5_acc = evaluator.get_top_k_accuracy(k=5)
        logging.info(f"Top-5 Accuracy: {top5_acc:.4f}")
        
        # Show worst predictions
        evaluator.print_worst_predictions(n=10)
        
        # Plot confusion matrix (optional)
        # evaluator.plot_confusion_matrix(save_path='confusion_matrix.png')
        
        # Log metrics to MLflow
        mlflow.log_metric("test_accuracy", metrics['accuracy'])
        mlflow.log_metric("test_precision", metrics['precision'])
        mlflow.log_metric("test_recall", metrics['recall'])
        mlflow.log_metric("test_f1", metrics['f1'])
        mlflow.log_metric("test_top5_accuracy", top5_acc)
        
        # Save results
        evaluator.save_results('evaluation_results.json')
        mlflow.log_artifact('evaluation_results.json')
        
        logging.info("Model evaluation completed successfully.")
        
        return (
            metrics['accuracy'],
            metrics['precision'],
            metrics['recall'],
            metrics['f1']
        )

    except Exception as e:
        logging.error(f"Error during model evaluation: {e}")
        raise e


@step(experiment_tracker="mlflow_tracker")
def evaluate_model_with_arrays(
    config_path: str = 'config.yaml',
    model_path: str = None
) -> Output(
    accuracy=float,
    precision=float,
    recall=float,
    f1=float
):  # type: ignore
    """
    Evaluate trained model using numpy arrays (legacy mode).
    
    Args:
        config_path (str): Path to configuration file
        model_path (str): Path to saved model
        
    Returns:
        tuple: (accuracy, precision, recall, f1)
    """
    logging.info("Beginning model evaluation (array mode)...")
    config = load_config(config_path)

    try:
        # Load model
        logging.info("Loading trained model...")
        if model_path:
            model = tf.keras.models.load_model(model_path)
        else:
            model_uri = mlflow.get_artifact_uri("model")
            model = mlflow.keras.load_model(model_uri)
        
        # Load data as arrays
        # Assuming you have a function to load as arrays
        X_test, y_test, class_names = load_test_arrays(config)
        
        # Initialize evaluator
        evaluator = DogBreedEvaluator(model=model, class_names=class_names)
        
        # Evaluate
        logging.info("Evaluating model on test arrays...")
        metrics = evaluator.evaluate_arrays(X_test, y_test)
        
        # Print results
        evaluator.print_results()
        evaluator.print_classification_report()
        
        # Log to MLflow
        mlflow.log_metrics({
            "test_accuracy": metrics['accuracy'],
            "test_precision": metrics['precision'],
            "test_recall": metrics['recall'],
            "test_f1": metrics['f1']
        })
        
        logging.info("Model evaluation completed successfully.")
        
        return (
            metrics['accuracy'],
            metrics['precision'],
            metrics['recall'],
            metrics['f1']
        )

    except Exception as e:
        logging.error(f"Error during model evaluation: {e}")
        raise e


def load_test_arrays(config):
    """
    Helper function to load test data as numpy arrays.
    Implement this based on your data loading logic.
    """
    # Placeholder - implement based on your needs
    pass