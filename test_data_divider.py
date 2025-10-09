import logging
from steps.data_divider import data_divider

if __name__ == "__main__":
    train_dir, val_dir = data_divider()
    print("✅ Train directory:", train_dir)
    print("✅ Validation directory:", val_dir)
