"""
ZenML Steps for Dog Breed Classification Pipeline - Model Evaluation
"""

import yaml
import logging
import mlflow
import numpy as np
import tensorflow as tf

from zenml import step
from typing import Annotated, Tuple
from steps.util import load_config, load_data, load_data_small
from model.evaluator import DogBreedEvaluator

logging.basicConfig(level=logging.INFO)


@step
def evaluate_model(
    model_path: str,
    test_ds_path: str,  # ← Path to data instead of dataset object
    class_names: list,
    config_path: str = 'steps/config.yaml'
) -> Tuple[
    Annotated[float, "accuracy"],
    Annotated[float, "precision"],
    Annotated[float, "recall"],
    Annotated[float, "f1"]
]:
    """
    Evaluate trained model on validation/test dataset.
    
    Args:
        model_path: Path to the saved Keras model
        test_ds_path: Path to test data directory
        class_names: List of class names
        config_path (str): Path to configuration file
        
    Returns:
        tuple: (accuracy, precision, recall, f1)
    """
    logging.info("Beginning model evaluation...")

    try:
        # Load the model from the provided path
        logging.info(f"Loading model from: {model_path}")
        model = tf.keras.models.load_model(model_path)
        logging.info("Model loaded successfully")
        
        # Load config and recreate dataset
        config = load_config(config_path)
        logging.info(f"Loading test data from: {test_ds_path}")
        
        # Recreate the dataset from the path
        _, test_ds, _, _ = load_data(config) #for faster result you can use the load_data_small
        
        # Initialize evaluator with model and class names
        evaluator = DogBreedEvaluator(model=model, class_names=class_names)
        
        # Evaluate on validation dataset
        logging.info("Evaluating model on validation set...")
        metrics = evaluator.evaluate_dataset(test_ds)
        
        # Print results
        evaluator.print_results()
        evaluator.print_classification_report()
        
        # Log additional metrics
        top5_acc = evaluator.get_top_k_accuracy(k=5)
        logging.info(f"Top-5 Accuracy: {top5_acc:.4f}")
        
        # Show worst predictions
        evaluator.print_worst_predictions(n=10)
        
        # Plot confusion matrix (optional)
        try:
            evaluator.plot_confusion_matrix(save_path='confusion_matrix.png')
            mlflow.log_artifact('confusion_matrix.png')
        except Exception as e:
            logging.warning(f"Could not plot confusion matrix: {e}")
        
        # Log metrics to MLflow
        mlflow.log_metric("test_accuracy", metrics['accuracy'])
        mlflow.log_metric("test_precision", metrics['precision'])
        mlflow.log_metric("test_recall", metrics['recall'])
        mlflow.log_metric("test_f1", metrics['f1'])
        mlflow.log_metric("test_top5_accuracy", top5_acc)
        
        # Save results
        evaluator.save_results('evaluation_results.json')
        try:
            mlflow.log_artifact('evaluation_results.json')
        except Exception as e:
            logging.warning(f"Could not log artifact to MLflow: {e}")
        
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


# Alternative version that loads everything inside the step
@step
def evaluate_model_standalone(
    model_path: str,
    config_path: str = 'steps/config.yaml'
) -> Tuple[
    Annotated[float, "accuracy"],
    Annotated[float, "precision"],
    Annotated[float, "recall"],
    Annotated[float, "f1"]
]:
    """
    Evaluate trained model - loads everything internally.
    
    Args:
        model_path: Path to the saved Keras model
        config_path: Path to configuration file
        
    Returns:
        tuple: (accuracy, precision, recall, f1)
    """
    logging.info("Beginning model evaluation...")

    try:
        # Load config
        config = load_config(config_path)
        
        # Load the model
        logging.info(f"Loading model from: {model_path}")
        model = tf.keras.models.load_model(model_path)
        logging.info("Model loaded successfully")
        
        # Load test data
        logging.info("Loading test data...")
        _, test_ds, class_names, _ = load_data(config) #for faster result you can use the load_data_small
        
        # Initialize evaluator
        evaluator = DogBreedEvaluator(model=model, class_names=class_names)
        
        # Evaluate
        logging.info("Evaluating model on validation set...")
        metrics = evaluator.evaluate_dataset(test_ds)
        
        # Print results
        evaluator.print_results()
        evaluator.print_classification_report()
        
        # Log additional metrics
        top5_acc = evaluator.get_top_k_accuracy(k=5)
        logging.info(f"Top-5 Accuracy: {top5_acc:.4f}")
        
        # Show worst predictions
        evaluator.print_worst_predictions(n=10)
        
        # Plot confusion matrix
        try:
            evaluator.plot_confusion_matrix(save_path='confusion_matrix.png')
            mlflow.log_artifact('confusion_matrix.png')
        except Exception as e:
            logging.warning(f"Could not plot confusion matrix: {e}")
        
        # Log metrics to MLflow
        mlflow.log_metric("test_accuracy", metrics['accuracy'])
        mlflow.log_metric("test_precision", metrics['precision'])
        mlflow.log_metric("test_recall", metrics['recall'])
        mlflow.log_metric("test_f1", metrics['f1'])
        mlflow.log_metric("test_top5_accuracy", top5_acc)
        
        # Save results
        evaluator.save_results('evaluation_results.json')
        try:
            mlflow.log_artifact('evaluation_results.json')
        except Exception as e:
            logging.warning(f"Could not log artifact to MLflow: {e}")
        
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


@step
def evaluate_model_with_arrays(
    config_path: str = 'config.yaml',
    model_path: str = None
) -> Tuple[
    Annotated[float, "accuracy"],
    Annotated[float, "precision"],
    Annotated[float, "recall"],
    Annotated[float, "f1"]
]:
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
        logging.info("Loading test arrays...")
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
    
    Args:
        config: Configuration dictionary
        
    Returns:
        tuple: (X_test, y_test, class_names)
    """
    from steps.util import load_data
    
    # Load as dataset first
    _, val_ds, class_names, num_classes = load_data(config, format_labels=True)
    
    # Convert to arrays
    X_test = []
    y_test = []
    
    for images, labels in val_ds:
        X_test.append(images.numpy())
        y_test.append(labels.numpy())
    
    X_test = np.concatenate(X_test, axis=0)
    y_test = np.concatenate(y_test, axis=0)
    
    return X_test, y_test, class_names