#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from thumbor.loaders import LoaderResult
from thumbor.utils import logger
from datetime import datetime
from os import fstat
from os.path import join, exists, abspath
from urllib.parse import unquote
from contextlib import contextmanager

async def load(context, path):
    file_path = join(context.config.FILE_LOADER_ROOT_PATH.rstrip(
        '/'), unquote(path).lstrip('/'))
    file_path = abspath(file_path)

    inside_root_path = file_path.startswith(
        context.config.FILE_LOADER_ROOT_PATH)
    
    result = LoaderResult()

    if not exists(file_path):
        file_path = unquote(file_path)

    if inside_root_path:
        if is_video(file_path):
            # Extract a frame from the video and load it instead of the original path
            logger.info('processing video... %s', file_path)
            with get_video_frame(context, file_path) as image_path:
                if image_path:
                    with open(image_path, "rb") as source_file:
                        stats = fstat(source_file.fileno())

                        result.successful = True
                        result.buffer = source_file.read()

                        result.metadata.update(
                            size=stats.st_size,
                            updated_at=datetime.utcfromtimestamp(stats.st_mtime),
                        )
                    return result
        elif is_pdf(file_path):
            # Extract first page of pdf and load it
            logger.info('processing pdf... %s', file_path)
            with get_pdf_page(file_path) as image_path:
                if image_path:
                    with open(image_path, "rb") as source_file:
                        stats = fstat(source_file.fileno())

                        result.successful = True
                        result.buffer = source_file.read()

                        result.metadata.update(
                            size=stats.st_size,
                            updated_at=datetime.utcfromtimestamp(stats.st_mtime),
                        )
                    return result
        else:
            logger.info('processing image... %s', file_path)
            with open(file_path, "rb") as source_file:
                    stats = fstat(source_file.fileno())

                    result.successful = True
                    result.buffer = source_file.read()

                    result.metadata.update(
                        size=stats.st_size,
                        updated_at=datetime.utcfromtimestamp(stats.st_mtime),
                    )
            return result


    # If we got here, there was a failure
    result = LoaderResult()
    result.error = LoaderResult.ERROR_NOT_FOUND
    result.successful = False
    return result


def is_video(file_path):
    import mimetypes
    type = mimetypes.guess_type(file_path)[0]
    return type and type.startswith('video')


def is_pdf(file_path):
    import mimetypes
    type = mimetypes.guess_type(file_path)[0]
    return type and type == 'application/pdf'


@contextmanager
def get_video_frame(context, file_path):
    """
    A context manager that extracts a single frame out of a video file and 
    stores it in a temporary file. Returns the path of the temporary file
    or None in case of failure.
    Depends on FFMPEG_PATH from Thumbor's configuration.
    """
    import subprocess
    import tempfile
    import os
    # Fail nicely when ffmpeg cannot be found
    if not os.path.exists(context.config.FFMPEG_PATH):
        logger.error('%s does not exist, please configure FFMPEG_PATH',
                     context.config.FFMPEG_PATH)
        yield None
        return
    # Prepare temporary file
    f, image_path = tempfile.mkstemp('.jpg')
    os.close(f)
    # Extract image
    try:
        cmd = [
            context.config.FFMPEG_PATH,
            '-i', file_path,
            '-ss', '00:00:01.000',
            '-vframes', '1',
            '-y',
            '-nostats',
            '-loglevel', 'error',
            image_path
        ]
        subprocess.check_call(cmd)
        yield image_path
    except:
        logger.exception('Cannot extract image frame from %s', file_path)
        yield None
    finally:
        # Cleanup
        try_to_delete(image_path)


@contextmanager
def get_pdf_page(file_path):
    """
    A context manager that extracts a single page out of a pdf file and 
    stores it in a temporary file. Returns the path of the temporary file
    or None in case of failure.
    """
    import subprocess
    import tempfile
    import os

    gspath = '/usr/bin/gs'

    # Fail nicely when ffmpeg cannot be found
    if not os.path.exists(gspath):
        logger.error('%s does not exist, please configure Ghostscript',
                     gspath)
        yield None
        return
    # Prepare temporary file
    f, image_path = tempfile.mkstemp('.jpg')
    os.close(f)
    logger.info('creating temporary file... %s', image_path)
    # Extract image
    try:
        cmd = [
            gspath,
            '-sDEVICE=jpeg',
            '-dDOINTERPOLATE',
            '-dCOLORSCREEN',
            '-dFirstPage=1',
            '-dLastPage=1',
            '-dPDFFitPage',
            '-dBATCH',
            '-dJPEGQ=85',
            '-r120x120',
            '-dNOPAUSE',
            '-sOutputFile='+image_path,
            file_path
        ]
        subprocess.check_call(cmd)
        yield image_path
    except:
        logger.exception('Cannot extract image frame from %s', file_path)
        yield None
    finally:
        # Cleanup
        try_to_delete(image_path)


def try_to_delete(file_path):
    """
    Delete the given file path but do not raise any exception.
    """
    import os
    try:
        os.remove(file_path)
    except:
        pass