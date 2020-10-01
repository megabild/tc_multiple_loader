# Thumbor Multiple Loader

This package provides a file loader that loads images, videos and pdf.
When asked to load a video file, it uses `ffmpeg` to extract a single frame
from the video, and returns it instead of the original video.

This allows Thumbor to create thumbnails from video files.

When asked to load a pdf file, it uses `ghostscript` to extract a single page image
from the pdf, and returns it instead of the original pdf.

This allows Thumbor to create thumbnails from pdf files.


## Installing

    $ pip install tc_multiple_loader

## Configuration

```
# Use the custom file loader
LOADER = 'tc_multiple_loader.loaders.multiple_loader'
# Full path to ffmpeg
FFMPEG_PATH = '/usr/bin/ffmpeg'
```

This project would not exists without the work of the thumbor community, especially https://github.com/thumbor-community/video.