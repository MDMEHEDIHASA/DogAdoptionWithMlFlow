import yaml
import logging
import tensorflow as tf
from zenml.steps import step, Output
from zenml.integrations.tensorflow.materializers import KerasMaterializer
import mlflow

from model.dog_breed_classifier import DogBreedClassifier
from util import load_config, load_data

logging.basicConfig(level=logging.DEBUG)

@step(output_materializers=KerasMaterializer,
      experiment_tracker="mlflow_tracker")
def train_model(config_path: str = 'config.yaml') -> Output(model=tf.keras.Model): # type: ignore
    """
    Modern training pipeline using tf.data.Dataset and transfer learning.
    
    Args:
        config_path (str): Path to configuration YAML file
        
    Returns:
        tf.keras.Model: Trained model
    """
    # Load configuration
    logging.info(f"Loading configuration from {config_path}")
    config = load_config(config_path)
    
    # Enable MLflow autologging
    mlflow.tensorflow.autolog()
    
    # Load datasets
    logging.info("Loading and preparing datasets...")
    train_ds, val_ds, class_names, num_classes = load_data(
        config=config,
        format_labels=True
    )
    
    
    
    # Initialize classifier
    logging.info("Initializing DogBreedClassifier...")
    classifier = DogBreedClassifier(config)
    
    # Train model
    logging.info(f"Starting training for {num_classes} dog breeds...")
    logging.info(f"Classes: {class_names[:5]}... (showing first 5)")
    
    model = classifier.train(
        train_ds=train_ds,
        val_ds=val_ds,
        num_classes=num_classes
    )
    
    # Save model
    logging.info("Saving model...")
    save_path = classifier.save(model)
    logging.info(f"Model saved to: {save_path}")
    
    # Log additional info to MLflow
    mlflow.log_param("num_classes", num_classes)
    mlflow.log_param("class_names_sample", class_names[:10])
    
    logging.info("Training complete!")
    return model


# Legacy version for backward compatibility
@step(output_materializers=KerasMaterializer,
      experiment_tracker="mlflow_tracker")
def train_model_legacy(X_train, y_train, config_path: str = 'config.yaml') -> Output(model=tf.keras.Model): #type: ignore
    """
    Legacy training pipeline using numpy arrays.
    
    Args:
        X_train: Training images (numpy array)
        y_train: Training labels (numpy array)
        config_path (str): Path to configuration file
        
    Returns:
        tf.keras.Model: Trained model
    """
    # Load configuration
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    
    # Enable MLflow autologging
    mlflow.tensorflow.autolog()
    
    # Initialize classifier
    classifier = DogBreedClassifier(config)
    
    # Train model
    logging.info("Starting legacy training...")
    model = classifier.train_legacy(X_train, y_train)
    
    # Save model
    logging.info("Saving model...")
    classifier.save(model)
    
    logging.info("Training complete!")
    return model


# Standalone training script (without ZenML)
def train_standalone(config_path: str = 'config.yaml'):
    """
    Standalone training function without ZenML dependencies.
    Use this for simple training without pipeline orchestration.
    
    Args:
        config_path (str): Path to configuration YAML file
        
    Returns:
        tf.keras.Model: Trained model
    """
    # Load configuration
    logging.info(f"Loading configuration from {config_path}")
    config = load_config(config_path)
    
    # Load datasets
    logging.info("Loading and preparing datasets...")
    train_ds, val_ds, class_names, num_classes = load_data(
        config=config,
        format_labels=True
    )
    
    logging.info(f"Found {num_classes} dog breeds")
    logging.info(f"Sample breeds: {class_names[:10]}")
    
    
    # Initialize and train classifier
    classifier = DogBreedClassifier(config)
    
    logging.info("Starting training...")
    model = classifier.train(
        train_ds=train_ds,
        val_ds=val_ds,
        num_classes=num_classes
    )
    
    # Save model
    save_path = classifier.save(model)
    logging.info(f"Model saved to: {save_path}")
    
    # Print model summary
    classifier.get_model_summary()
    
    return model, class_names
