import os
from pathlib import Path

source_dir = "."

classes = ["car", "pickup", "truck", "motorcycle"]
image_exts = [".jpg", ".jpeg", ".png", ".bmp", ".webp"]

label_root = os.path.join(source_dir, "labels")

print("CEK DATASET")
print("====================")

for class_name in classes:
    image_folder = os.path.join(source_dir, class_name)
    label_folder = os.path.join(label_root, class_name)

    print(f"\nKelas: {class_name}")
    print("Image folder:", image_folder, os.path.exists(image_folder))
    print("Label folder:", label_folder, os.path.exists(label_folder))

    if not os.path.exists(image_folder):
        continue

    images = [
        f for f in os.listdir(image_folder)
        if Path(f).suffix.lower() in image_exts
    ]

    labels = []
    if os.path.exists(label_folder):
        labels = [
            f for f in os.listdir(label_folder)
            if Path(f).suffix.lower() == ".txt"
        ]

    print("Jumlah gambar:", len(images))
    print("Jumlah label :", len(labels))

    cocok = 0
    tidak_cocok = []

    for img in images:
        name = Path(img).stem
        label_path = os.path.join(label_folder, name + ".txt")

        if os.path.exists(label_path):
            cocok += 1
        else:
            tidak_cocok.append(img)

    print("Pasangan cocok:", cocok)

    if len(tidak_cocok) > 0:
        print("Contoh gambar tanpa label:")
        for x in tidak_cocok[:5]:
            print(" -", x)