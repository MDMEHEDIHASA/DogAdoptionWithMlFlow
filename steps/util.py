import os
import tensorflow as tf
from tensorflow.keras import layers
import logging
import yaml
from PIL import Image
from random import choice
from typing import Dict, Tuple, List



logging.basicConfig(level=logging.INFO)

#first load the config file
def load_config(config_path: str) -> Dict:
    """
    Loads configuration from YAML file.
    
    Args:
        config_path (str): Path to the YAML config file
        
    Returns:
        dict: Configuration dictionary
    """
    
    logging.info(f'Loading configuration from {config_path}')

    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)

    logging.info(f'Configurataiton loaded successfully')
    return config


def format_class_names(raw_class_names: list) -> list:
    """
    Formats class names by removing numeric prefixes and replacing underscores.
    
    Example: "001-Chihuahua" -> "Chihuahua"
             "002-Japanese_spaniel" -> "Japanese spaniel"
    
    Args:
        raw_class_names (list): List of raw folder names
        
    Returns:
        list: List of formatted class names
    """

    formatted_names = []

    for name in raw_class_names:
        # Split by '-' and take everything after the first part
        # Then replace underscores with spaces
        formatted = name.split('-', 1)[-1].replace('_', ' ')
        formatted_names.append(formatted)
    return formatted_names


def load_data(config: Dict, format_labels: bool = True) -> Tuple:
    """
    Loads training and validation datasets from directory using config.
    
    Args:
        config (dict): Configuration dictionary
        format_labels (bool): Whether to format class names (remove prefixes, etc.)
        
    Returns:
        tuple: (train_ds, val_ds, class_names, num_classes)
    """
    # Extract parameters from config
    image_dir = os.path.abspath(config.get('image_dir')) 
    img_size = tuple(config.get('image_size', (224,224)))
    batch_size = config.get('batch_size')
    validation_split = config.get('validation_split')
    seed = config.get('seed')
    
    logging.info(f'Loading training data from {image_dir}')
    logging.info(f'Image size: {img_size}, Batch size: {batch_size}')

    if not os.path.exists(image_dir):
        raise ValueError(f"Image directory not found: {image_dir}")
    
    # Load training dataset
    train_ds = tf.keras.utils.image_dataset_from_directory(
        image_dir,
        validation_split=validation_split,
        subset="training",
        seed=seed,
        image_size=img_size,
        batch_size=batch_size
    )
    
    logging.info(f'Loading validation data from {image_dir}')
    
    # Load validation dataset
    val_ds = tf.keras.utils.image_dataset_from_directory(
        image_dir,
        validation_split=validation_split,
        subset="validation",
        seed=seed,
        image_size=img_size,
        batch_size=batch_size
    )
    
    # Get class names
    raw_class_names = train_ds.class_names
    
    # Format class names if requested
    if format_labels:
        class_names = format_class_names(raw_class_names)
        logging.info(f'Formatted class names from folders')
    else:
        class_names = raw_class_names
    
    num_classes = len(class_names)
    
    logging.info(f'Found {num_classes} classes')
    logging.info(f'Sample classes: {class_names[:5]}')
    
    return train_ds, val_ds, class_names, num_classes


#If you want to use limited image for faster training use this funciton
def load_data_small(config: Dict, format_labels: bool = True) -> Tuple:
    """Loads training and validation datasets from directory using config."""
    
    image_dir = os.path.abspath(config.get('image_dir')) 
    img_size = tuple(config.get('image_size', (224, 224)))
    batch_size = config.get('batch_size', 32)
    validation_split = config.get('validation_split', 0.2)
    seed = config.get('seed', 42)
    
    # 🚀 NEW: Limit images if specified
    n_images = config.get('n_images_per_dir', None)
    if n_images:
        logging.info(f'⚡ FAST MODE: Limiting to {n_images} images per breed')
        image_dir = _create_subset(image_dir, n_images, seed)
    
    logging.info(f'Loading training data from {image_dir}')
    
    if not os.path.exists(image_dir):
        raise ValueError(f"Image directory not found: {image_dir}")
    
    # Load datasets (same as before)
    train_ds = tf.keras.utils.image_dataset_from_directory(
        image_dir, validation_split=validation_split, subset="training",
        seed=seed, image_size=img_size, batch_size=batch_size
    )
    
    val_ds = tf.keras.utils.image_dataset_from_directory(
        image_dir, validation_split=validation_split, subset="validation",
        seed=seed, image_size=img_size, batch_size=batch_size
    )
    
    raw_class_names = train_ds.class_names
    
    if format_labels:
        class_names = format_class_names(raw_class_names)
    else:
        class_names = raw_class_names
    
    num_classes = len(class_names)
    logging.info(f'Found {num_classes} classes')
    
    return train_ds, val_ds, class_names, num_classes


# 🚀 ADD this helper function
def _create_subset(image_dir: str, n_images: int, seed: int) -> str:
    """Create temporary folder with limited images per breed."""
    import tempfile
    import shutil
    import random
    
    temp_dir = tempfile.mkdtemp(prefix='subset_')
    random.seed(seed)
    
    for breed in os.listdir(image_dir):
        breed_path = os.path.join(image_dir, breed)
        if not os.path.isdir(breed_path):
            continue
        
        # Get all images
        images = [f for f in os.listdir(breed_path)
                 if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        
        if not images:
            continue
        
        # Select random subset
        selected = random.sample(images, min(n_images, len(images)))
        
        # Copy to temp folder
        temp_breed = os.path.join(temp_dir, breed)
        os.makedirs(temp_breed, exist_ok=True)
        
        for img in selected:
            shutil.copy2(
                os.path.join(breed_path, img),
                os.path.join(temp_breed, img)
            )
    
    return temp_dir

# IF Pre-split data existstrain/ and test/Use load_train_test_data()

def load_train_test_data(config: Dict,
                          format_labels: bool = True) -> Tuple:
    """
    Loads separate train and test datasets from different directories.
    
    Args:
        config (dict): Configuration dictionary
        format_labels (bool): Whether to format class names
        
    Returns:
        tuple: (train_ds, test_ds, class_names, num_classes)
    """
    train_dir = config.get('image_dir_train')
    test_dir = config.get('image_dir_test')
    img_size = tuple(config.get('image_size'))
    batch_size = config.get('batch_size')
    
    if not train_dir or not test_dir:
        raise ValueError("Both 'image_dir_train' and 'image_dir_test' must be specified in config")
    
    logging.info(f'Loading training data from {train_dir}')
    
    # Load training dataset (no validation split)
    train_ds = tf.keras.utils.image_dataset_from_directory(
        train_dir,
        image_size=img_size,
        batch_size=batch_size,
        shuffle=True,
        seed=config.get('seed')
    )
    
    logging.info(f'Loading test data from {test_dir}')
    
    # Load test dataset
    test_ds = tf.keras.utils.image_dataset_from_directory(
        test_dir,
        image_size=img_size,
        batch_size=batch_size,
        shuffle=False
    )
    
    # Get class names
    raw_class_names = train_ds.class_names
    
    if format_labels:
        class_names = format_class_names(raw_class_names)
    else:
        class_names = raw_class_names
    
    num_classes = len(class_names)
    
    logging.info(f'Found {num_classes} classes')
    
    return train_ds, test_ds, class_names, num_classes




