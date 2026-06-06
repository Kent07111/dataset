import cv2
import os
import glob

# =========================
# KONFIGURASI
# =========================
INPUT_DIR = "."
LABEL_DIR = "labels_manual"
PREVIEW_DIR = "preview_manual"

# PILIH FOLDER YANG MAU DIKERJAKAN
# Contoh:
# ["car"]
# ["motorcycle"]
# ["pickup"]
# ["truck"]
# ["car", "pickup"]
TARGET_FOLDERS = ["pickup"]

SKIP_ALREADY_LABELED = True

CLASS_NAMES = {
    0: "car",
    1: "motorcycle",
    2: "pickup",
    3: "truck"
}

CLASS_COLORS = {
    0: (255, 0, 0),      # biru
    1: (0, 255, 0),      # hijau
    2: (0, 0, 255),      # merah
    3: (0, 255, 255)     # kuning
}

CLASS_ID_BY_FOLDER = {
    "car": 0,
    "motorcycle": 1,
    "pickup": 2,
    "truck": 3
}

IMAGE_EXTS = ["*.jpg", "*.jpeg", "*.png", "*.bmp", "*.webp"]

# =========================
# VARIABEL GLOBAL
# =========================
drawing = False
start_x, start_y = -1, -1
boxes = []
current_class = 0
img_display = None
img_original = None


# =========================
# KONVERSI KE YOLO FORMAT
# =========================
def to_yolo_format(x1, y1, x2, y2, img_w, img_h):
    x_min = min(x1, x2)
    y_min = min(y1, y2)
    x_max = max(x1, x2)
    y_max = max(y1, y2)

    box_w = x_max - x_min
    box_h = y_max - y_min

    x_center = (x_min + box_w / 2) / img_w
    y_center = (y_min + box_h / 2) / img_h
    width = box_w / img_w
    height = box_h / img_h

    return x_center, y_center, width, height


# =========================
# GAMBAR BOX + LABEL CLASS
# =========================
def draw_boxes():
    global img_display

    img_display = img_original.copy()

    for box in boxes:
        cls_id, x1, y1, x2, y2 = box
        color = CLASS_COLORS[cls_id]
        label = CLASS_NAMES[cls_id]

        cv2.rectangle(
            img_display,
            (x1, y1),
            (x2, y2),
            color,
            2
        )

        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.7
        thickness = 2

        (text_w, text_h), baseline = cv2.getTextSize(
            label,
            font,
            font_scale,
            thickness
        )

        label_y = y1 - 10 if y1 - 10 > text_h else y1 + text_h + 10

        cv2.rectangle(
            img_display,
            (x1, label_y - text_h - baseline),
            (x1 + text_w + 8, label_y + baseline),
            color,
            -1
        )

        cv2.putText(
            img_display,
            label,
            (x1 + 4, label_y),
            font,
            font_scale,
            (255, 255, 255),
            thickness
        )


# =========================
# EVENT MOUSE UNTUK DRAW BOX
# =========================
def mouse_callback(event, x, y, flags, param):
    global drawing, start_x, start_y, boxes

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        start_x, start_y = x, y

    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            temp_img = img_display.copy()
            color = CLASS_COLORS[current_class]

            cv2.rectangle(
                temp_img,
                (start_x, start_y),
                (x, y),
                color,
                2
            )

            cv2.imshow("Annotate YOLO Manual", temp_img)

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False

        x1 = min(start_x, x)
        y1 = min(start_y, y)
        x2 = max(start_x, x)
        y2 = max(start_y, y)

        if abs(x2 - x1) > 10 and abs(y2 - y1) > 10:
            boxes.append((current_class, x1, y1, x2, y2))
            draw_boxes()
            cv2.imshow("Annotate YOLO Manual", img_display)


# =========================
# AMBIL GAMBAR BERDASARKAN FOLDER TARGET
# =========================
def collect_images():
    image_paths = []

    for folder in TARGET_FOLDERS:
        folder_path = os.path.join(INPUT_DIR, folder)

        if not os.path.isdir(folder_path):
            print(f"Folder tidak ditemukan: {folder_path}")
            continue

        for ext in IMAGE_EXTS:
            image_paths.extend(glob.glob(os.path.join(folder_path, ext)))

    return sorted(image_paths)


# =========================
# CEK LABEL SUDAH ADA
# =========================
def label_exists(img_path):
    rel_path = os.path.relpath(img_path, INPUT_DIR)
    class_folder = rel_path.split(os.sep)[0]

    file_name = os.path.basename(img_path)
    base_name = os.path.splitext(file_name)[0]

    label_path = os.path.join(LABEL_DIR, class_folder, base_name + ".txt")

    return os.path.exists(label_path)


# =========================
# SIMPAN LABEL YOLO
# =========================
def save_annotation(img_path, boxes):
    img_h, img_w = img_original.shape[:2]

    rel_path = os.path.relpath(img_path, INPUT_DIR)
    class_folder = rel_path.split(os.sep)[0]

    file_name = os.path.basename(img_path)
    base_name = os.path.splitext(file_name)[0]

    label_folder = os.path.join(LABEL_DIR, class_folder)
    preview_folder = os.path.join(PREVIEW_DIR, class_folder)

    os.makedirs(label_folder, exist_ok=True)
    os.makedirs(preview_folder, exist_ok=True)

    label_path = os.path.join(label_folder, base_name + ".txt")
    preview_path = os.path.join(preview_folder, file_name)

    with open(label_path, "w") as f:
        for box in boxes:
            cls_id, x1, y1, x2, y2 = box

            x_center, y_center, w, h = to_yolo_format(
                x1, y1, x2, y2, img_w, img_h
            )

            f.write(
                f"{cls_id} {x_center:.6f} {y_center:.6f} {w:.6f} {h:.6f}\n"
            )

    cv2.imwrite(preview_path, img_display)

    print(f"Label disimpan : {label_path}")
    print(f"Preview        : {preview_path}")


# =========================
# MAIN PROGRAM
# =========================
def main():
    global img_original, img_display, boxes, current_class

    image_paths = collect_images()

    if not image_paths:
        print("Tidak ada gambar ditemukan.")
        print("Pastikan TARGET_FOLDERS sesuai nama folder.")
        return

    if SKIP_ALREADY_LABELED:
        before = len(image_paths)
        image_paths = [p for p in image_paths if not label_exists(p)]
        skipped = before - len(image_paths)
        print(f"File yang sudah dilabel dilewati: {skipped}")

    if not image_paths:
        print("Semua gambar pada folder target sudah punya label.")
        return

    first_folder = os.path.relpath(image_paths[0], INPUT_DIR).split(os.sep)[0]
    current_class = CLASS_ID_BY_FOLDER.get(first_folder, 0)

    print(f"Folder yang dikerjakan: {TARGET_FOLDERS}")
    print(f"Total gambar yang perlu dilabel: {len(image_paths)}")
    print("==============================")
    print("KONTROL:")
    print("0 = car")
    print("1 = motorcycle")
    print("2 = pickup")
    print("3 = truck")
    print("Klik tahan mouse lalu drag untuk buat bounding box")
    print("s = simpan dan otomatis lanjut")
    print("u = undo box terakhir")
    print("n = skip gambar tanpa simpan")
    print("q = keluar")
    print("==============================")

    cv2.namedWindow("Annotate YOLO Manual")
    cv2.setMouseCallback("Annotate YOLO Manual", mouse_callback)

    idx = 0

    while idx < len(image_paths):
        img_path = image_paths[idx]

        rel_path = os.path.relpath(img_path, INPUT_DIR)
        class_folder = rel_path.split(os.sep)[0]

        if class_folder in CLASS_ID_BY_FOLDER:
            current_class = CLASS_ID_BY_FOLDER[class_folder]

        img_original = cv2.imread(img_path)

        if img_original is None:
            print(f"Gagal membaca gambar: {img_path}")
            idx += 1
            continue

        boxes = []

        print("\n==============================")
        print(f"Gambar {idx + 1}/{len(image_paths)}")
        print(f"File: {img_path}")
        print(f"Folder: {class_folder}")
        print(f"Class otomatis: {current_class} - {CLASS_NAMES[current_class]}")

        draw_boxes()
        cv2.imshow("Annotate YOLO Manual", img_display)

        while True:
            key = cv2.waitKey(1) & 0xFF

            if key == ord("0"):
                current_class = 0
                print("Class aktif: 0 - car")

            elif key == ord("1"):
                current_class = 1
                print("Class aktif: 1 - motorcycle")

            elif key == ord("2"):
                current_class = 2
                print("Class aktif: 2 - pickup")

            elif key == ord("3"):
                current_class = 3
                print("Class aktif: 3 - truck")

            elif key == ord("u"):
                if boxes:
                    boxes.pop()
                    draw_boxes()
                    cv2.imshow("Annotate YOLO Manual", img_display)
                    print("Undo box terakhir.")
                else:
                    print("Belum ada box untuk di-undo.")

            elif key == ord("s"):
                if boxes:
                    save_annotation(img_path, boxes)
                    idx += 1
                    break
                else:
                    print("Belum ada bounding box. Tidak disimpan.")

            elif key == ord("n"):
                idx += 1
                print("Gambar diskip.")
                break

            elif key == ord("q"):
                print("Program dihentikan.")
                cv2.destroyAllWindows()
                return

    cv2.destroyAllWindows()
    print("Semua gambar pada folder target selesai.")


if __name__ == "__main__":
    main()