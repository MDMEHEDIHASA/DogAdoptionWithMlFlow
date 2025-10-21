import logging
import datetime
import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.layers import Input
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.optimizers import Adam


logging.basicConfig(level=logging.DEBUG)

class DogBreedClassifier:
    """
    Dog breed classifier using transfer learning with ResNet50.
    Supports both numpy arrays (legacy) and tf.data.Dataset (modern).
    """
    def __init__(self, config:dict):
        """
        Initialize the classifier with configuration.
        
        Args:
            config (dict): Configuration dictionary with model parameters
        """
        self.config = config
        self.model = None
        self.history = None

    def create_data_augmentation(self):
        """
        Creates data augmentation pipeline.
        
        Returns:
            tf.keras.Sequential: Data augmentation model
        """
        logging.info("Creating data augmentation pipeline...")

        data_augmentation = tf.keras.Sequential([
            layers.RandomFlip("horizontal"),
            layers.RandomRotation(self.config.get('rotation_range', 0.1)),
            layers.RandomZoom(self.config.get('zoom_range', 0.1)),
        ], name='data_augmentation')

        return data_augmentation
    
    def build_model(self, num_classes: int, use_augmentation:bool = True):
        """
        Builds the transfer learning model with ResNet50.
        
        Args:
            num_classes (int): Number of output classes
            use_augmentation (bool): Whether to include data augmentation
            
        Returns:
            tf.keras.Model: Compiled model
        """
        logging.info("Building transfer learning model with ResNet50...")

        img_size = tuple(self.config.get('image_size'))

        #load pretrained ResNet50
        base_model = ResNet50(
            input_shape = img_size + (3,),
            include_top = False,
            weights = "imagenet"
        )

        # Freeze base model for inital training
        base_model.trainable = False
        logging.info(f"Base model loaded. Trainable: {base_model.trainable}")
        
        #Build model
        inputs = Input(shape=img_size + (3,))

        #optional data augmentation
        if use_augmentation:
            x = self.create_data_augmentation()(inputs)
        else:
            x = inputs
        
        # Preprocess for ResNet50
        x = tf.keras.applications.resnet50.preprocess_input(x)
        
        # Base model
        x = base_model(x, training=False)
        
        # Classification head
        x = layers.GlobalAveragePooling2D()(x)
        x = layers.Dropout(self.config.get('dropout', 0.3))(x)
        
        # Output layer
        outputs = layers.Dense(num_classes, activation="softmax")(x)
        
        # Create model
        model = models.Model(inputs, outputs, name='dog_breed_classifier')
        
        logging.info(f"Model built with {num_classes} classes")
        return model
    
    def train(self, train_ds, val_ds, num_classes: int):
        """
        Train model with two-phase approach:
        1. Train only the classification head (frozen backbone)
        2. Fine-tune the entire model (unfrozen backbone)
        
        Args:
            train_ds: Training dataset (tf.data.Dataset)
            val_ds: Validation dataset (tf.data.Dataset)
            num_classes (int): Number of classes
            
        Returns:
            tf.keras.Model: Trained model
        """
        # Build Model
        self.model = self.build_model(
            num_classes=num_classes,
            use_augmentation=self.config.get('use_augmentation', True)
            )
        
        #phase 1: tRAIN WITH  frozen backbone
        logging.info("=" * 60)
        logging.info("PHASE 1: Training classification head (frozen backbone)")
        logging.info("=" * 60)

        self.model.compile(
            optimizer=Adam(learning_rate=self.config.get('learning_rate')),
            loss="sparse_categorical_crossentropy",
            metrics=["accuracy"]
        )
        
        initial_epochs = self.config.get('initial_epochs')
        history_phase1 = self.model.fit(
            train_ds,
            validation_data=val_ds,
            epochs=initial_epochs,
            verbose=1
        )

        # Phase 2: Fine-tune entire model
        if self.config.get('fine_tune'):
            logging.info("=" * 60)
            logging.info("PHASE 2: Fine-tuning entire model (unfrozen backbone)")
            logging.info("=" * 60)

            # Unfreeze base model
            base_model = self.model.layers[2]  # Get ResNet50 base
            base_model.trainable = True

             # Recompile with lower learning rate
            self.model.compile(
                optimizer=Adam(learning_rate=self.config.get('fine_tune_lr')),
                loss="sparse_categorical_crossentropy",
                metrics=["accuracy"]
            )

            fine_tune_epochs = self.config.get('fine_tune_epochs', 5)
            total_epochs = initial_epochs + fine_tune_epochs

            history_phase2 = self.model.fit(
                train_ds,
                validation_data=val_ds,
                epochs=total_epochs,
                initial_epoch=initial_epochs,
                verbose=1
            )

            # Combine histories
            self.history = {
                'phase1': history_phase1.history,
                'phase2': history_phase2.history
            }
        else:
            self.history = history_phase1.history
        
        logging.info("Model training complete!")
        return self.model
    


    def train_legacy(self, X_train, y_train):
        """
        Legacy training method for backward compatibility with numpy arrays.
        
        Args:
            X_train (np.ndarray): Training images
            y_train (np.ndarray): Training labels
            
        Returns:
            tf.keras.Model: Trained model
        """
        logging.info("Using legacy training method with numpy arrays...")
        
        # Infer number of classes
        num_classes = y_train.shape[1] if len(y_train.shape) > 1 else len(set(y_train))
        
        # Build model (no augmentation in legacy mode)
        self.model = self.build_model(num_classes=num_classes, use_augmentation=False)
        
        # Compile
        self.model.compile(
            optimizer=Adam(learning_rate=self.config.get('learning_rate')),
            loss='categorical_crossentropy' if len(y_train.shape) > 1 else 'sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
        
        # Train
        history = self.model.fit(
            X_train,
            y_train,
            epochs=self.config.get('num_epochs', self.config.get('initial_epochs', 10)),
            batch_size=self.config.get('batch_size'),
            validation_split=self.config.get('val_split'),
            verbose=1
        )
        
        self.history = history.history
        return self.model
    
    def save(self, model=None, save_format='keras'):
        """
        Save the trained model.
        
        Args:
            model (tf.keras.Model, optional): Model to save. Uses self.model if None.
            save_format (str): Format to save ('keras' or 'h5')
        """
        if model is None:
            model = self.model
        
        if model is None:
            raise ValueError("No model to save. Train the model first.")
        
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        output_path = self.config.get('output_path')
        
        if save_format == 'h5':
            filepath = f"{output_path}/model-{timestamp}.h5"
        else:
            filepath = f"{output_path}/model-{timestamp}.keras"
        
        #model.save(filepath, save_format=save_format)
        model.save(filepath)
        logging.info(f"Model saved to {filepath}")
        
        return filepath
    
    def get_model_summary(self):
        """Print model summary."""
        if self.model:
            self.model.summary()
        else:
            logging.warning("No model built yet. Call build_model() or train() first.")


