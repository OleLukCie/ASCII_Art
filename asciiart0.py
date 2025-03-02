from PIL import Image, ImageDraw, ImageFont
import os
import numpy as np
import argparse

sample_rate = 0.6
input_folder = "D:/data/FunTools/ASCII Art/output"
output_folder = "D:/data/FunTools/ASCII Art/out"


def ascii_art(file_path):
    im = Image.open(file_path)
    image_size = im.size

    font = ImageFont.truetype("SourceCodePro-Bold.ttf", size=12)

    letter_bbox = font.getbbox('A')
    letter_size = (letter_bbox[2] - letter_bbox[0], letter_bbox[3] - letter_bbox[1])

    aspect_ratio = letter_size[0] / letter_size[1]
    new_im_size = tuple(np.array([image_size[0] * sample_rate, image_size[1] * sample_rate / aspect_ratio]).astype(int))

    im = im.resize(new_im_size)
    im_color = np.array(im)
    im = im.convert("L")
    im = np.array(im)

    symbols = np.array(list(" .-vM"))

    max_val = im.max() - im.min()
    if max_val == 0:
        max_val = 1
    im_normalized = np.clip((im - im.min()) / max_val, 0, 1)

    im_clipped = np.round(im_normalized * (symbols.size - 1))
    im_clipped[im_clipped < 0] = 0
    im_clipped[im_clipped >= symbols.size] = symbols.size - 1

    # 确保 im_clipped 中的所有值都在 0 到 symbols.size - 1 之间
    im_clipped = np.clip(im_clipped, 0, symbols.size - 1)
    assert np.all((0 <= im_clipped) & (im_clipped < symbols.size)), "存在超出预期范围的值"
    ascii = symbols[im_clipped.astype(int)]

    im_out_size = (new_im_size[0] * letter_size[0], new_im_size[1] * letter_size[1])
    bg_color = "black"
    im_out = Image.new("RGB", im_out_size, bg_color)
    draw = ImageDraw.Draw(im_out)

    for i, line in enumerate(ascii):
        for j, ch in enumerate(line):
            color = tuple(im_color[i, j])
            draw.text((j * letter_size[0], i * letter_size[1]), ch, fill=color, font=font)

    output_file_path = os.path.join(output_folder, os.path.basename(file_path) + ".ascii.png")
    im_out.save(output_file_path)


def batch_process_images():
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if filename.endswith(".png") or filename.endswith(".jpg"):
            file_path = os.path.join(input_folder, filename)
            ascii_art(file_path)
            print(f"Processed {filename}.")


if __name__ == "__main__":
    batch_process_images()
