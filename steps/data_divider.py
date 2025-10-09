import os
import zipfile
import tarfile
import shutil
import random
import logging

from zenml import step


@step

def data_divider(
    data_path:str = "data/raw/Images.zip",
    output_dir:str = "data/processed"
):
    """
    Extracts images from a zip/tar file, cleans folder names,
    and splits dataset into train and validation sets.
    """
    train_split = 0.8
    extract_dir = os.path.join(output_dir, "extracted")
    os.makedirs(extract_dir, exist_ok=True)

    #1. Extract dataset (zip or tar)
    if not os.listdir(extract_dir):
        if data_path.endswith(".zip"):
            with zipfile.ZipFile(data_path,'r') as zip_ref:
                zip_ref.extractall(extract_dir)
                print(f"Extracted zip to {extract_dir}")
        elif data_path.endswith((".tar", ".tar.gz", ".tgz")):
            with tarfile.open(data_path, 'r:*') as tar_ref:
                tar_ref.extractall(extract_dir)
        else:
            raise ValueError("Unsupported file format. Use .zip, .tar, or .tar.gz")
        print(f" Extracted dataset to {extract_dir}")
        
    
    #--- 2. Prepare output folders ---
    train_dir = os.path.join(output_dir, "train")
    val_dir = os.path.join(output_dir, "val")
    os.makedirs(train_dir, exist_ok=True)
    os.makedirs(val_dir, exist_ok=True)

    # 3. Find the Images folder (might be nested)
    images_root = extract_dir
    if os.path.exists(os.path.join(extract_dir, "Images")):
        images_root = os.path.join(extract_dir, "Images")

    #4. Get all breed folders (e.g., n02085620-Chihuahua)
    breed_folders = [f for f in os.listdir(images_root) 
                     if os.path.isdir(os.path.join(images_root, f))]
    print(f"📂 Found {len(breed_folders)} breed folders")

    # 5. Split each breed into train/val
    for breed_folder in breed_folders:
        breed_path = os.path.join(images_root, breed_folder)
        
        # Get all image files
        image_files = [f for f in os.listdir(breed_path) 
                      if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        
        # Shuffle for random split
        random.shuffle(image_files)
        
        # Calculate split point
        split_idx = int(len(image_files) * train_split)
        train_files = image_files[:split_idx]
        val_files = image_files[split_idx:]
        
        # Create breed folders in train/val
        train_breed_dir = os.path.join(train_dir, breed_folder)
        val_breed_dir = os.path.join(val_dir, breed_folder)
        os.makedirs(train_breed_dir, exist_ok=True)
        os.makedirs(val_breed_dir, exist_ok=True)
        
        # Copy files to train folder
        for img_file in train_files:
            src = os.path.join(breed_path, img_file)
            dst = os.path.join(train_breed_dir, img_file)
            shutil.copy2(src, dst)
        
        # Copy files to val folder
        for img_file in val_files:
            src = os.path.join(breed_path, img_file)
            dst = os.path.join(val_breed_dir, img_file)
            shutil.copy2(src, dst)
        
        print(f"  ✓ {breed_folder}: {len(train_files)} train, {len(val_files)} val")
    
    print(f"✅ Split complete! Train: {train_dir}, Val: {val_dir}")
    return train_dir, val_dir

    