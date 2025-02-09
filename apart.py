import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image

def crop_images(file_paths):
    output_folder = "cropped_images"
    os.makedirs(output_folder, exist_ok=True)

    for file_path in file_paths:
        try:
            img = Image.open(file_path)
            width, height = img.size

            # ファイル名から数字を抽出
            file_name = os.path.basename(file_path)
            file_number = int(''.join(filter(str.isdigit, file_name)))

            # 偶数なら上半分、奇数なら下半分を切り取る
            if file_number % 2 == 0:
                cropped_img = img.crop((0, 0, width, height // 2))
            else:
                cropped_img = img.crop((0, height // 2, width, height))

            # 保存
            save_path = os.path.join(output_folder, f"cropped_{file_name}")
            cropped_img.save(save_path, "JPEG")

        except Exception as e:
            messagebox.showerror(
                "Error", f"Failed to process {file_name}: {str(e)}")

def rotate_images(file_paths, direction):
    output_folder = "rotated_images"
    os.makedirs(output_folder, exist_ok=True)

    for file_path in file_paths:
        try:
            img = Image.open(file_path)

            # 回転方向の選択
            if direction == "cw":
                rotated_img = img.rotate(-90, expand=True)  # 時計回り
            else:
                rotated_img = img.rotate(90, expand=True)  # 反時計回り

            # 保存
            file_name = os.path.basename(file_path)
            save_path = os.path.join(output_folder, f"rotated_{file_name}")
            rotated_img.save(save_path, "JPEG")

        except Exception as e:
            messagebox.showerror(
                "Error", f"Failed to rotate {file_name}: {str(e)}")

def select_files(action):
    file_paths = filedialog.askopenfilenames(
        filetypes=[("JPEG files", "*.jpg"), ("All files", "*.*")]
    )
    if file_paths:
        if action == "crop":
            crop_images(file_paths)
            messagebox.showinfo(
                "Completed", "Images have been cropped and saved!")
        elif action == "cw":
            rotate_images(file_paths, "cw")
            messagebox.showinfo(
                "Completed", "Images have been rotated (Clockwise) and saved!")
        elif action == "ccw":
            rotate_images(file_paths, "ccw")
            messagebox.showinfo(
                "Completed", "Images have been rotated (Counterclockwise) and saved!")

def main():
    root = tk.Tk()
    root.title("Image Crop & Rotate App")

    crop_button = tk.Button(
        root, text="Select Images for Cropping", command=lambda: select_files("crop"))
    crop_button.pack(pady=10)

    rotate_cw_button = tk.Button(
        root, text="Rotate Images 90° Clockwise", command=lambda: select_files("cw"))
    rotate_cw_button.pack(pady=10)

    rotate_ccw_button = tk.Button(
        root, text="Rotate Images 90° Counterclockwise", command=lambda: select_files("ccw"))
    rotate_ccw_button.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()
