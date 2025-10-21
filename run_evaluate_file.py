"""
from steps.evaluate_model import evaluate_model
from steps.util import load_data_small, load_config

config = load_config("steps/config.yaml")
_, val_ds, class_names, _ = load_data_small(config)

# Pass the model path instead of loading the model
model_path = "saved_model/model-2025-10-19-00-47-24.keras"

# Now call evaluate_model with the path
evaluate_model(
    model_path=model_path,
    test_ds=val_ds,
    class_names=class_names
)


"""


from tensorflow import keras
from steps.util import load_data, load_config
from model.evaluator import DogBreedEvaluator
import logging

logging.basicConfig(level=logging.INFO)

# Load config and data
config = load_config("steps/config.yaml")
_, val_ds, class_names, _ = load_data(config)

# Load model
model_path = "saved_model/model-2025-10-20-14-42-38.keras"
logging.info(f"Loading model from: {model_path}")
model = keras.models.load_model(model_path)

# Create evaluator and evaluate
logging.info("Starting evaluation...")
evaluator = DogBreedEvaluator(model=model, class_names=class_names)

# Evaluate on validation dataset
metrics = evaluator.evaluate_dataset(val_ds)

# Print results
evaluator.print_results()
evaluator.print_classification_report()

# Additional metrics
top5_acc = evaluator.get_top_k_accuracy(k=5)
logging.info(f"Top-5 Accuracy: {top5_acc:.4f}")

# Show worst predictions
evaluator.print_worst_predictions(n=10)

# Plot confusion matrix
try:
    evaluator.plot_confusion_matrix(save_path='confusion_matrix.png')
    logging.info("Confusion matrix saved")
except Exception as e:
    logging.warning(f"Could not plot confusion matrix: {e}")

# Save results
evaluator.save_results('evaluation_results.json')
logging.info("Evaluation completed successfully!")