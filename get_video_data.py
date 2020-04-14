import errno
import os.path
import videoprops


def main():
    filename = 'S:\TV Shows\Law and Order SVU\Law and Order SVU s05e11_20090418013055.mpg'
    props = get_video_data(filename)
    print(f"""
    Codec: {props['codec_name']}
    Resolution: {props['width']}×{props['height']}
    """)


def get_video_data(filename):
    if os.path.exists(filename):
        props = videoprops.get_video_properties(filename)
    else:
        raise FileNotFoundError(
            errno.ENOENT, os.strerror(errno.ENOENT), filename)

    fields = ['codec_name', 'width', 'height']
    result = {prop: props[prop] for prop in fields}
    return result


if __name__ == "__main__":
    main()
