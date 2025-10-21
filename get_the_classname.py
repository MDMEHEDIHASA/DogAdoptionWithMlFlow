import os

dataset_dir = "data/processed/extracted/Images"
folders = sorted(os.listdir(dataset_dir))  # sorted to match training order
class_names = []

for f in folders:
    if os.path.isdir(os.path.join(dataset_dir, f)):  # ensure it's a folder
        name = f.split('-', 1)[-1].replace('_', ' ')
        class_names.append(name)

print("Total classes:", len(class_names))
print("Sample:", class_names[:10])

with open("dog_classes.txt", "w") as f:
    for name in class_names:
        f.write(name + "\n")