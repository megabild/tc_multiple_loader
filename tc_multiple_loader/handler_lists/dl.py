#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from typing import Any, cast

from thumbor.handler_lists import HandlerList
from tc_multiple_loader.handlers.dl import DlHandler


def get_handlers(context: Any) -> HandlerList:
    is_dl_enabled = cast(bool, context.config.USE_DL)
    if not is_dl_enabled:
        return []

    return [(r"/dl/(.*)", DlHandler, {"context": context})]