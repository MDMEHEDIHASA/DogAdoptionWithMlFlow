from zenml.integrations.constants import MLFLOW
from zenml.config import DockerSettings
from zenml.pipelines import pipeline

docker_settings = DockerSettings(required_integrations=[MLFLOW])


@pipeline(enable_cache=False, settings={"docker": docker_settings})
def train_pipeline(import_data, train_model, evaluate_model):
    """
    Simplified training pipeline with just data import and training.
    Evaluation can be added later.
    
    Args:
        import_data: Step to load and prepare datasets
        train_model: Step to train the model
        
    Returns:
        tf.keras.Model: Trained model
    """
    # Step 1: Import and prepare data
    train_ds, val_ds, class_names, num_classes = import_data()
    
    # Step 2: Train model
    model = train_model(
        train_ds=train_ds,
        val_ds=val_ds,
        num_classes=num_classes,
        class_names=class_names
    )

    precision, recall, f1 = evaluate_model(model, val_ds, class_names)