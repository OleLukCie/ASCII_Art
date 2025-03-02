from PIL import Image
import numpy as np


def ascii_art(file):
    im = Image.open(file)
    im = im.convert("L")

    sample_rate = 0.15
    new_im_size = [int(x * sample_rate) for x in im.size]
    im = im.resize(new_im_size)

    im = np.array(im)

    symbols = np.array(list(".-vM"))

    im = (im - im.min()) / (im.max() - im.min()) * (symbols.size - 1)

    # Generate the ascii art
    ascii = symbols[im.astype(int)]
    lines = '\n'.join(("".join(r) for r in ascii))
    print(lines)


if __name__ == "__main__":
    ascii_art("one-piece.png")
