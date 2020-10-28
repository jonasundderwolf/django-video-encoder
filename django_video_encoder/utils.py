FULL_RESOLUTION = "full resolution"


def codec_width_height_to_format_label(video_codec, width, height):
    if width and height:
        resolution = f"{width}x{height}"
    elif not width and not height:
        resolution = FULL_RESOLUTION
    elif width:
        resolution = f"{width} width"
    else:
        resolution = f"{height} heigth"
    return f"{video_codec} ({resolution})"
