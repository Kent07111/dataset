import os
import random
import shutil
from pathlib import Path

# =========================
# SETTING
# =========================
source_dir = "."
output_dir = "dataset_yolo"

classes = {
    "car": 0,
    "pickup": 1,
    "truck": 2,
    "motorcycle": 3
}

train_ratio = 0.8
valid_ratio = 0.1

image_exts = [".jpg", ".jpeg", ".png", ".bmp", ".webp"]

# =========================
# HAPUS OUTPUT LAMA JIKA ADA
# =========================
if os.path.exists(output_dir):
    shutil.rmtree(output_dir)

# =========================
# BUAT FOLDER OUTPUT
# =========================
for split in ["train", "valid", "test"]:
    os.makedirs(os.path.join(output_dir, split, "images"), exist_ok=True)
    os.makedirs(os.path.join(output_dir, split, "labels"), exist_ok=True)

# =========================
# AMBIL DATA GAMBAR + LABEL
# =========================
all_data = []

label_root = os.path.join(source_dir, "labels")

for class_name in classes.keys():
    image_folder = os.path.join(source_dir, class_name)
    label_folder = os.path.join(label_root, class_name)

    print(f"\nCek kelas: {class_name}")
    print("Image folder:", image_folder)
    print("Label folder:", label_folder)

    if not os.path.exists(image_folder):
        print(f"Folder gambar tidak ditemukan: {image_folder}")
        continue

    if not os.path.exists(label_folder):
        print(f"Folder label tidak ditemukan: {label_folder}")
        continue

    for file in os.listdir(image_folder):
        ext = Path(file).suffix.lower()

        if ext in image_exts:
            image_path = os.path.join(image_folder, file)
            label_path = os.path.join(label_folder, Path(file).stem + ".txt")

            if os.path.exists(label_path):
                all_data.append((image_path, label_path, file))
            else:
                print(f"Label tidak ditemukan: {class_name}/{file}")

# =========================
# SPLIT DATA
# =========================
random.shuffle(all_data)

total = len(all_data)

if total == 0:
    print("\nTotal data 0.")
    print("Cek nama folder dan label.")
    exit()

train_count = int(total * train_ratio)
valid_count = int(total * valid_ratio)

train_data = all_data[:train_count]
valid_data = all_data[train_count:train_count + valid_count]
test_data = all_data[train_count + valid_count:]

split_data = {
    "train": train_data,
    "valid": valid_data,
    "test": test_data
}

# =========================
# COPY FILE KE FOLDER YOLO
# =========================
for split, data in split_data.items():
    for image_path, label_path, image_file in data:
        image_name = Path(image_file).stem
        image_ext = Path(image_file).suffix

        dst_image = os.path.join(output_dir, split, "images", image_name + image_ext)
        dst_label = os.path.join(output_dir, split, "labels", image_name + ".txt")

        shutil.copy2(image_path, dst_image)
        shutil.copy2(label_path, dst_label)

# =========================
# BUAT data.yaml
# =========================
yaml_path = os.path.join(output_dir, "data.yaml")

with open(yaml_path, "w") as f:
    f.write("train: train/images\n")
    f.write("val: valid/images\n")
    f.write("test: test/images\n\n")
    f.write("nc: 4\n")
    f.write("names:\n")
    f.write("  0: car\n")
    f.write("  1: pickup\n")
    f.write("  2: truck\n")
    f.write("  3: motorcycle\n")

print("\nSplit YOLO selesai.")
print("==============================")
print(f"Total data : {total}")
print(f"Train      : {len(train_data)}")
print(f"Valid      : {len(valid_data)}")
print(f"Test       : {len(test_data)}")
print(f"Output     : {output_dir}")
print(f"YAML       : {yaml_path}")