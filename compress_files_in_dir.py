import os
import re
import subprocess
from collections import OrderedDict

from get_video_data import get_video_data
from pathlib import Path


def description(props):
    return f"codec:{props['codec_name']}, resolution:{props['width']}x{props['height']}"


def recompressed_filename(filename, profile):
    file = Path(filename)
    suffix = '_'
    if profile == 'PAL':
        suffix = '_PAL'
    new_file = file.parent / (file.stem + suffix + ".mkv")
    return str(new_file)


def encodefile(file, profile):
    handbrake = 'C:\Program Files\HandBrake\HandBrakeCLI.exe'
    outputfile = recompressed_filename(file, profile)
    if os.path.exists(outputfile):
        print(f"File {outputfile} already exists, exiting")
        return
    profiles = {'PAL':
                    [handbrake,
                     '--encoder-preset=fast', '--encoder-level=4.0', '--encoder-profile=main', '--crop', '0:0:0:0',
                     '--custom-anamorphic', '--pixel-aspect', '0:0', '--modulus', '2', '-e', 'x265', '-b', '600', '-2',
                     '-T',
                     '--deinterlace',
                     'codec=-t', '1', '--angle', '1', '-f', 'mkv', '--denoise=medium', '-w', '720', '-l', '576',
                     '--rate',
                     '25',
                     'audio=--cfr', '-a', '1', '-E', 'copy', '-6', 'none', '-R', 'Auto', '-B', '0', '-D', '0', '--gain',
                     '0',
                     '--audio-fallback', 'ac3'],
                'HD': [handbrake,
                       '--encoder-preset=fast', '--encoder-level=4.0', '--encoder-profile=main', '--crop', '0:0:0:0',
                       '--custom-anamorphic', '--pixel-aspect', '0:0', '--modulus', '2', '-e', 'x265', '-b', '1200',
                       '-2', '-T',
                       'codec=-t', '1', '--angle', '1', '-f', 'mkv', '--denoise=medium', '--rate', '25',
                       'audio=--cfr', '-a', '1', '-E', 'copy', '-6', 'none', '-R', 'Auto', '-B', '0', '-D', '0',
                       '--gain', '0',
                       '--audio-fallback', 'ac3']
                }

    if profile not in profiles.keys():
        print(f"Unknown profile {profile}")
        return

    compression = profiles[profile] + ['-i', file, '-o', outputfile]
    print(f"\nConverting file {file} to format {profile}")
    cp = subprocess.Popen(compression, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1,
                          universal_newlines=True)
    # print("the commandline is {}".format(cp.args))
    # print("the commandline is ", " ".join(cp.args))
    shortname = Path(outputfile).stem
    # print(cp.communicate())
    # while True:
    #     line = cp.stdout.readline()
    #     if not line:
    #         break
    #     # the real code does filtering here
    #     print("test:", line.rstrip())
    for line in iter(cp.stdout.readline, ''):
        #     # # regex match for % complete and ETA
        #     # matches = re.match(r'.*(\d+\.\d+)\s%.*ETA\s(\d+)h(\d+)m(\d+)s', line.decode('utf-8'))
        #     # if matches:
        #     #     print(matches.group())
        if "Encoding" in line:
            print(f'\r{profile}/{shortname} {line.rstrip()}', end='')
        else:
            # print(line.rstrip())
            pass

    cp.stdout.close()
    cp.wait()


def main():
    directory = Path('S:\TV Shows\Law and Order SVU')
    # filename = 'S:\TV Shows\Law and Order SVU\Law and Order SVU s05e18a.mkv'
    # x = get_video_data(filename)
    # encodefile(filename,'PAL')

    files_data = get_files_and_props_from_dir(directory)
    files_by_format = {}
    for filename, props in files_data.items():
        print(f"filename:[{filename}] - {description(props)}")
        codec = props['codec_name']
        if codec not in files_by_format:
            files_by_format[codec] = []
        files_by_format[codec].append(filename)

    # ['hevc', 'mpeg2video', 'h264', 'mpeg4']
    compressions_by_code = OrderedDict([('mpeg2video', 'PAL'), ('h264', 'HD')])
    for codec, format in compressions_by_code.items():
        for file in files_by_format[codec]:
            encodefile(file, format)


def get_files_and_props_from_dir(directory):
    files = [file for file in os.listdir(directory)]
    files_data = {}
    for file in files:
        try:
            if file.endswith('.srt'):
                continue
            full_file = str(Path(directory) / file)
            props = get_video_data(full_file)
            files_data[full_file] = props
        except:
            print(f"Cannot analyze file: {file}")
            continue
    return files_data


if __name__ == "__main__":
    main()
