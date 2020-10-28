FULL_RESOLUTION = "full resolution"

def format_label_to_codec_width_height(format_label):
    video_codec, resolution = format_label[:-1].rsplit(" (", 1)
    if resolution == FULL_RESOLUTION:
        width = height = None
    else:
        width, height = resolution.split("x")
    return video_codec, width, height


def codec_width_height_to_format_label(video_codec, width, height):
    resolution = f"{width}x{height}" if width or height else FULL_RESOLUTION
    return f"{video_codec} ({resolution})"
