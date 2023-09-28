#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com
from thumbor.handlers import ContextHandler
from thumbor.utils import logger

from os.path import join, abspath
from urllib.parse import unquote


##
# Handler to download files from file loader root path
##
class DlHandler(ContextHandler):
    def download_file(self, path):
        logger.info("Attempting to download file... %s", path)

        file_path = join(self.context.config.FILE_LOADER_ROOT_PATH.rstrip(
            '/'), unquote(path).lstrip('/'))
        file_path = abspath(file_path)

        inside_root_path = file_path.startswith(
            self.context.config.FILE_LOADER_ROOT_PATH)
        
        new_file = path.rsplit("/")[-1]
        
        if inside_root_path:
            with open(file_path, "rb") as file_buffered_reader:
                import mimetypes
                file_type = mimetypes.guess_type(file_path)[0]
                self.set_header("Content-Type", file_type)
                self.set_header("Content-Disposition", "attachment; filename="+new_file)
                content = file_buffered_reader.read()
                self.write(content)

        else:
            self._error(403, "Download of file at the given URL is not allowed")
        
        self.finish()

    async def get(self, path):
        self.download_file(path)