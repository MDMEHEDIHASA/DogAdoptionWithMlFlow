"""
Model Evaluator for Dog Breed Classification
"""

import logging
import numpy as np
import tensorflow as tf
from typing import Dict, List, Tuple, Optional
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)
import matplotlib.pyplot as plt
import seaborn as sns # type: ignore

logging.basicConfig(level=logging.INFO)


class DogBreedEvaluator:
    """
    Evaluator for dog breed classification models.
    Supports both tf.data.Dataset and numpy array inputs.
    """
    
    def __init__(self, model: tf.keras.Model, class_names: List[str]):
        """
        Initialize the evaluator.
        
        Args:
            model (tf.keras.Model): Trained model to evaluate
            class_names (List[str]): List of class names
        """
        self.model = model
        self.class_names = class_names
        self.num_classes = len(class_names)
        self.results = {}
        
    def evaluate_dataset(self, test_ds: tf.data.Dataset) -> Dict[str, float]:
        """
        Evaluate model on a tf.data.Dataset.
        
        Args:
            test_ds (tf.data.Dataset): Test dataset
            
        Returns:
            Dict[str, float]: Dictionary of metrics
        """
        logging.info("Evaluating model on test dataset...")
        
        # Get predictions
        y_true = []
        y_pred = []
        y_pred_proba = []
        
        for images, labels in test_ds:
            predictions = self.model.predict(images, verbose=0)
            y_true.extend(labels.numpy())
            y_pred.extend(np.argmax(predictions, axis=1))
            y_pred_proba.extend(predictions)
        
        y_true = np.array(y_true)
        y_pred = np.array(y_pred)
        y_pred_proba = np.array(y_pred_proba)
        
        # Calculate metrics
        metrics = self._calculate_metrics(y_true, y_pred, y_pred_proba)
        
        self.results = {
            'metrics': metrics,
            'y_true': y_true,
            'y_pred': y_pred,
            'y_pred_proba': y_pred_proba
        }
        
        return metrics
    
    def evaluate_arrays(self, 
                       X_test: np.ndarray, 
                       y_test: np.ndarray) -> Dict[str, float]:
        """
        Evaluate model on numpy arrays (legacy mode).
        
        Args:
            X_test (np.ndarray): Test images
            y_test (np.ndarray): Test labels
            
        Returns:
            Dict[str, float]: Dictionary of metrics
        """
        logging.info("Evaluating model on test arrays...")
        
        # Get predictions
        y_pred_proba = self.model.predict(X_test, verbose=0)
        y_pred = np.argmax(y_pred_proba, axis=1)
        
        # Handle one-hot encoded labels
        if len(y_test.shape) > 1 and y_test.shape[1] > 1:
            y_true = np.argmax(y_test, axis=1)
        else:
            y_true = y_test
        
        # Calculate metrics
        metrics = self._calculate_metrics(y_true, y_pred, y_pred_proba)
        
        self.results = {
            'metrics': metrics,
            'y_true': y_true,
            'y_pred': y_pred,
            'y_pred_proba': y_pred_proba
        }
        
        return metrics
    
    def _calculate_metrics(self, 
                          y_true: np.ndarray, 
                          y_pred: np.ndarray,
                          y_pred_proba: np.ndarray) -> Dict[str, float]:
        """
        Calculate evaluation metrics.
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            y_pred_proba: Prediction probabilities
            
        Returns:
            Dict[str, float]: Dictionary of metrics
        """
        # Get unique classes in the dataset
        unique_classes = np.unique(np.concatenate([y_true, y_pred]))
        
        # Basic metrics
        accuracy = accuracy_score(y_true, y_pred)
        precision = precision_score(y_true, y_pred, average='weighted', zero_division=0)
        recall = recall_score(y_true, y_pred, average='weighted', zero_division=0)
        f1 = f1_score(y_true, y_pred, average='weighted', zero_division=0)
        
        # Per-class metrics (only for classes present in data)
        precision_per_class = precision_score(y_true, y_pred, labels=unique_classes, average=None, zero_division=0)
        recall_per_class = recall_score(y_true, y_pred, labels=unique_classes, average=None, zero_division=0)
        f1_per_class = f1_score(y_true, y_pred, labels=unique_classes, average=None, zero_division=0)
        
        metrics = {
            'accuracy': float(accuracy),
            'precision': float(precision),
            'recall': float(recall),
            'f1': float(f1),
            'precision_per_class': precision_per_class.tolist(),
            'recall_per_class': recall_per_class.tolist(),
            'f1_per_class': f1_per_class.tolist(),
            'num_classes_in_data': len(unique_classes),
            'total_classes': self.num_classes
        }
        
        return metrics
    
    def print_results(self):
        """Print evaluation results in a formatted way."""
        if not self.results:
            logging.warning("No evaluation results available. Run evaluate_dataset() or evaluate_arrays() first.")
            return
        
        metrics = self.results['metrics']
        
        print("\n" + "=" * 70)
        print("EVALUATION RESULTS")
        print("=" * 70)
        print(f"Classes in test data: {metrics.get('num_classes_in_data', 'N/A')} / {metrics.get('total_classes', 'N/A')}")
        print(f"Accuracy:  {metrics['accuracy']:.4f} ({metrics['accuracy']*100:.2f}%)")
        print(f"Precision: {metrics['precision']:.4f} ({metrics['precision']*100:.2f}%)")
        print(f"Recall:    {metrics['recall']:.4f} ({metrics['recall']*100:.2f}%)")
        print(f"F1 Score:  {metrics['f1']:.4f} ({metrics['f1']*100:.2f}%)")
        print("=" * 70)
    
    def print_classification_report(self):
        """Print detailed classification report."""
        if not self.results:
            logging.warning("No evaluation results available.")
            return
        
        y_true = self.results['y_true']
        y_pred = self.results['y_pred']
        
        # Get unique classes present in the data
        unique_classes = np.unique(np.concatenate([y_true, y_pred]))
        
        # Get labels for only the classes present in the data
        labels_present = [self.class_names[i] for i in unique_classes]
        
        print("\n" + "=" * 70)
        print("CLASSIFICATION REPORT")
        print("=" * 70)
        print(f"Note: Report includes only {len(unique_classes)} out of {len(self.class_names)} total classes present in test data\n")
        print(classification_report(
            y_true, 
            y_pred, 
            labels=unique_classes,
            target_names=labels_present,
            zero_division=0
        ))
        print("=" * 70)
    
    def get_confusion_matrix(self) -> np.ndarray:
        """
        Get confusion matrix.
        
        Returns:
            np.ndarray: Confusion matrix
        """
        if not self.results:
            logging.warning("No evaluation results available.")
            return None
        
        y_true = self.results['y_true']
        y_pred = self.results['y_pred']
        
        return confusion_matrix(y_true, y_pred)
    
    def plot_confusion_matrix(self, 
                             save_path: Optional[str] = None,
                             figsize: Tuple[int, int] = (12, 10)):
        """
        Plot confusion matrix.
        
        Args:
            save_path (str, optional): Path to save the plot
            figsize (tuple): Figure size
        """
        if not self.results:
            logging.warning("No evaluation results available.")
            return
        
        y_true = self.results['y_true']
        y_pred = self.results['y_pred']
        
        # Get unique classes in data
        unique_classes = np.unique(np.concatenate([y_true, y_pred]))
        labels_present = [self.class_names[i] for i in unique_classes]
        
        # Create confusion matrix only for classes present
        cm = confusion_matrix(y_true, y_pred, labels=unique_classes)
        
        plt.figure(figsize=figsize)
        
        # For many classes, use a subset or show without labels
        if len(unique_classes) > 20:
            sns.heatmap(cm, cmap='Blues', fmt='d')
            plt.title(f'Confusion Matrix ({len(unique_classes)} classes)')
            plt.ylabel('True Label')
            plt.xlabel('Predicted Label')
        else:
            sns.heatmap(
                cm, 
                annot=True, 
                fmt='d', 
                cmap='Blues',
                xticklabels=labels_present,
                yticklabels=labels_present
            )
            plt.title(f'Confusion Matrix ({len(unique_classes)} classes)')
            plt.ylabel('True Label')
            plt.xlabel('Predicted Label')
            plt.xticks(rotation=45, ha='right')
            plt.yticks(rotation=0)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logging.info(f"Confusion matrix saved to {save_path}")
        
        plt.show()
    
    def get_top_k_accuracy(self, k: int = 5) -> float:
        """
        Calculate top-k accuracy.
        
        Args:
            k (int): Number of top predictions to consider
            
        Returns:
            float: Top-k accuracy
        """
        if not self.results:
            logging.warning("No evaluation results available.")
            return 0.0
        
        y_true = self.results['y_true']
        y_pred_proba = self.results['y_pred_proba']
        
        # Get top k predictions
        top_k_preds = np.argsort(y_pred_proba, axis=1)[:, -k:]
        
        # Check if true label is in top k
        correct = 0
        for i, true_label in enumerate(y_true):
            if true_label in top_k_preds[i]:
                correct += 1
        
        top_k_acc = correct / len(y_true)
        
        logging.info(f"Top-{k} Accuracy: {top_k_acc:.4f} ({top_k_acc*100:.2f}%)")
        
        return top_k_acc
    
    def get_worst_predictions(self, n: int = 10) -> List[Dict]:
        """
        Get the worst predictions (lowest confidence correct predictions 
        or highest confidence incorrect predictions).
        
        Args:
            n (int): Number of worst predictions to return
            
        Returns:
            List[Dict]: List of worst prediction details
        """
        if not self.results:
            logging.warning("No evaluation results available.")
            return []
        
        y_true = self.results['y_true']
        y_pred = self.results['y_pred']
        y_pred_proba = self.results['y_pred_proba']
        
        worst = []
        
        for i in range(len(y_true)):
            true_label = int(y_true[i])
            pred_label = int(y_pred[i])
            confidence = y_pred_proba[i][pred_label]
            
            is_correct = true_label == pred_label
            
            # Safely get class names
            true_class = self.class_names[true_label] if true_label < len(self.class_names) else f"Class_{true_label}"
            pred_class = self.class_names[pred_label] if pred_label < len(self.class_names) else f"Class_{pred_label}"
            
            worst.append({
                'index': i,
                'true_label': true_class,
                'pred_label': pred_class,
                'confidence': float(confidence),
                'is_correct': is_correct,
                'error_score': confidence if not is_correct else (1 - confidence)
            })
        
        # Sort by error score (high confidence mistakes or low confidence correct)
        worst.sort(key=lambda x: x['error_score'], reverse=True)
        
        return worst[:n]
    
    def print_worst_predictions(self, n: int = 10):
        """Print worst predictions."""
        worst = self.get_worst_predictions(n)
        
        print("\n" + "=" * 70)
        print(f"TOP {n} WORST PREDICTIONS")
        print("=" * 70)
        
        for i, pred in enumerate(worst, 1):
            status = "✓" if pred['is_correct'] else "✗"
            print(f"{i}. {status} True: {pred['true_label']:<30} "
                  f"Pred: {pred['pred_label']:<30} "
                  f"Conf: {pred['confidence']:.2%}")
        
        print("=" * 70)
    
    def save_results(self, filepath: str):
        """
        Save evaluation results to a file.
        
        Args:
            filepath (str): Path to save results
        """
        import json
        
        if not self.results:
            logging.warning("No evaluation results available.")
            return
        
        # Prepare results for JSON serialization
        save_data = {
            'metrics': self.results['metrics'],
            'class_names': self.class_names,
            'num_samples': len(self.results['y_true']),
            'classes_in_test_data': self.results['metrics'].get('num_classes_in_data', 0)
        }
        
        with open(filepath, 'w') as f:
            json.dump(save_data, f, indent=2)
        
        logging.info(f"Results saved to {filepath}")