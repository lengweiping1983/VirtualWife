import logging

from .sys_config import SysConfig


singleton_sys_config = SysConfig()
logger = logging.getLogger(__name__)
