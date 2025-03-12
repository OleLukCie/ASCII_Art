from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np
import time
import os


class VideoAsciiConverter:
    def __init__(self, font_size=20, sample_rate=0.1):
        self.sample_rate = sample_rate
        self.font_size = font_size

        # Try to load Chinese fonts, in order of priority
        font_paths = [
            "simhei.ttf",  # Heiti for Windows
            "C:/Windows/Fonts/simhei.ttf",  # Full path for Windows
            "/System/Library/Fonts/PingFang.ttc",  # Font for macOS
            "SourceCodePro-Bold.ttf"  # Default fallback
        ]

        self.font = None
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    self.font = ImageFont.truetype(font_path, size=font_size)
                    print(f"Using font: {font_path}")
                    break
                except:
                    continue

        if self.font is None:
            print("Warning: No suitable Chinese font found, using default font")
            self.font = ImageFont.load_default()

        # Get character size
        letter_bbox = self.font.getbbox('a')
        self.letter_size = (letter_bbox[2] - letter_bbox[0], letter_bbox[3] - letter_bbox[1])
        self.aspect_ratio = self.letter_size[0] / self.letter_size[1]

        # Use the characters "aaa" as the character set, sorted from dark to bright
        self.symbols = np.array(list("aaa"))

    def process_frame(self, frame):
        # Convert BGR to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        im = Image.fromarray(frame_rgb)

        # Calculate new image size
        new_im_size = tuple(np.array([
            im.size[0] * self.sample_rate,
            im.size[1] * self.sample_rate / self.aspect_ratio
        ]).astype(int))

        # Resize the image
        im = im.resize(new_im_size)
        im_color = np.array(im)

        # Convert to grayscale
        im_gray = im.convert("L")
        im_gray = np.array(im_gray)

        # Normalize processing
        max_val = im_gray.max() - im_gray.min()
        if max_val == 0:
            max_val = 1
        im_normalized = (im_gray - im_gray.min()) / max_val

        # Convert to ASCII indices
        im_ascii_indices = np.clip(
            np.round(im_normalized * (len(self.symbols) - 1)),
            0,
            len(self.symbols) - 1
        ).astype(int)

        # Create output image
        im_out_size = (new_im_size[0] * self.letter_size[0], new_im_size[1] * self.letter_size[1])
        im_out = Image.new("RGB", im_out_size, "black")
        draw = ImageDraw.Draw(im_out)

        # Draw ASCII characters
        for i in range(im_ascii_indices.shape[0]):
            for j in range(im_ascii_indices.shape[1]):
                color = tuple(im_color[i, j])
                char = self.symbols[im_ascii_indices[i, j]]
                draw.text(
                    (j * self.letter_size[0], i * self.letter_size[1]),
                    char,
                    fill=color,
                    font=self.font
                )

        # Convert back to OpenCV format
        return cv2.cvtColor(np.array(im_out), cv2.COLOR_RGB2BGR)


def process_video(input_path, output_path=None, preview=True):
    # Open video file
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        print("Error: Unable to open video file")
        return

    # Get video information
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Create ASCII converter
    converter = VideoAsciiConverter()

    # If saving video, create a video writer
    video_writer = None
    if output_path:
        # Process the first frame to get output size
        ret, frame = cap.read()
        if ret:
            ascii_frame = converter.process_frame(frame)
            height, width = ascii_frame.shape[:2]
            video_writer = cv2.VideoWriter(
                output_path,
                cv2.VideoWriter_fourcc(*'mp4v'),
                fps,
                (width, height)
            )
            # Process the first frame
            video_writer.write(ascii_frame)
        # Reset video
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    print("Starting video processing...")
    frame_count = 0
    start_time = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Convert frame to ASCII art
        ascii_frame = converter.process_frame(frame)

        # Show preview
        if preview:
            cv2.imshow('ASCII Video', ascii_frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Save video
        if video_writer is not None:
            video_writer.write(ascii_frame)

        frame_count += 1
        if frame_count % 30 == 0:
            elapsed_time = time.time() - start_time
            fps = frame_count / elapsed_time
            print(f"Processed {frame_count} frames, current FPS: {fps:.2f}")

    # Clean up resources
    cap.release()
    if video_writer is not None:
        video_writer.release()
    cv2.destroyAllWindows()

    print(f"Processing complete! Total processed frames: {frame_count}")


if __name__ == "__main__":
    # Example usage
    input_video = "D:/data/FunTools/ASCII Art/sos.mp4"  # Use forward slashes instead of backslashes
    output_video = "D:/data/FunTools/ASCII Art/00000.mp4"  # Use forward slashes instead of backslashes

    # Process video (preview and save simultaneously)
    process_video(input_video, output_video, preview=True)
