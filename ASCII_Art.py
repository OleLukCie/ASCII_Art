from PIL import Image, ImageFont
import numpy as np


def ascii_art(file):
    im = Image.open(file)

    # Convert to grayscale image
    im = im.convert("L")

    sample_rate = 0.15

    # Compute letter aspect ratio
    font = ImageFont.truetype("SourceCodePro-Regular.ttf")
    # Using getbbox method to get the size, ensure it's not a tuple of arrays
    bbox = font.getbbox("x")
    aspect_ratio = (bbox[2] - bbox[0]) / (bbox[3] - bbox[1])

    # Ensure calculations are done with integers or properly casted floats
    new_im_size = [
        int(im.size[0] * sample_rate),
        int(im.size[1] * sample_rate * aspect_ratio)
    ]

    # Downsample the image
    im = im.resize(new_im_size)

    # Convert to numpy array for image manipulation
    im = np.array(im)

    # Defines all the symbols in ascending order that will form the final ascii
    symbols = np.array(list(".-vM"))

    # Normalize minimum and maximum to [0,max_symbol_index)
    im = (im - im.min()) / (im.max() - im.min()) * (symbols.size - 1)

    # Generate the ascii art
    ascii = symbols[im.astype(int)]
    lines = '\n'.join(("".join(r) for r in ascii))
    print(lines)


if __name__ == "__main__":
    ascii_art("one-piece.png")
