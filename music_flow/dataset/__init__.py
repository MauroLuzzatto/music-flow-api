import os

dir_path = os.path.dirname(os.path.realpath(__file__))


with open(os.path.join(dir_path, "VERSION")) as version_file:
    __version__ = version_file.read().strip()
