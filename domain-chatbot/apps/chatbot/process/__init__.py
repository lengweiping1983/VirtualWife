import logging

from ..config import singleton_sys_config
from .process import ProcessCore, TopicBot, EmotionBot


logger = logging.getLogger(__name__)


# 单例
process_core = ProcessCore()
topic_bot = TopicBot()
emotion_bot = EmotionBot()

# from ..insight.bilibili_api.bili_live_client import lazy_bilibili_live
# # 加载直播配置
# sys_config_json = singleton_sys_config.get()
# enableLive = sys_config_json["enableLive"]
# if enableLive:
#     lazy_bilibili_live(sys_config_json, singleton_sys_config)
