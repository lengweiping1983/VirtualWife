import os
import json
import logging

from ..llms.llm_model_strategy import LlmModelDriver
from ..models import CustomRoleModel, SysConfigModel
from ..character.default_character import default_character
from ..utils.json_utils import read_json, dumps_json


config_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(config_dir, "sys_config.json")
sys_code = "adminSettings"
logger = logging.getLogger(__name__)


class SysConfig:
    llm_model_driver: LlmModelDriver
    conversation_llm_model_driver_type: str
    enable_longMemory: bool
    enable_summary: bool
    summary_llm_model_driver_type: str
    enable_reflection: bool
    reflection_llm_model_driver_type: str
    zep_url: str
    zep_optional_api_key: str
    short_memory_num: int = 15
    long_memory_num: int = 10
    summary_memory_num: int = 15
    topic_memory_num: int = 20
    emotion_memory_num: int = 25
    character: int
    character_name: str
    userNameSet = set()
    room_id: str
    
    def __init__(self) -> None:
        self.bilibili_live_listener = None
        self.thread_pool_manager = None
        self.load()

    def get(self):
        sys_config_obj = None
        sys_config_json = read_json(config_path)
        try:
            sys_config_obj = SysConfigModel.objects.filter(code=sys_code).first()
            if sys_config_obj == None:
                logger.debug("=> save sys config to db")
                sys_config_model = SysConfigModel(
                    code=sys_code,
                    config=dumps_json(sys_config_json)
                )
                sys_config_model.save()
            else:
                sys_config_json = json.loads(sys_config_obj.config)
        except Exception as e:
            logger.debug("=> load sys config error: %s" % str(e))
        return sys_config_json

    def save(self, sys_config_json: any):
        sys_config_obj = SysConfigModel.objects.get(code=sys_code)
        sys_config_obj.config = dumps_json(sys_config_json)
        sys_config_obj.save()

    def load(self):
        logger.debug("======================== Load SysConfig ========================")

        sys_config_json = self.get()

        os.environ['TOKENIZERS_PARALLELISM'] = "false"

        # 加载大语言模型配置
        os.environ['OPENAI_API_KEY'] = sys_config_json["languageModelConfig"]["openai"]["OPENAI_API_KEY"]
        os.environ['OPENAI_BASE_URL'] = sys_config_json["languageModelConfig"]["openai"]["OPENAI_BASE_URL"]
        ollama = sys_config_json["languageModelConfig"].get("ollama")
        if ollama:
            os.environ['OLLAMA_API_BASE'] = ollama.get("OLLAMA_API_BASE", "http://localhost:11434")
            os.environ['OLLAMA_API_MODEL_NAME'] = ollama.get("OLLAMA_API_MODEL_NAME", "qwen:7b")
        else:
            os.environ['OLLAMA_API_BASE'] = "http://localhost:11434"
            os.environ['OLLAMA_API_MODEL_NAME'] = "qwen:7b"

        # 加载对话模块配置
        logger.debug("=> Chat Config")
        self.llm_model_driver = LlmModelDriver()
        self.conversation_llm_model_driver_type = sys_config_json["conversationConfig"]["languageModel"]
        logger.debug(f"conversation_llm_model_driver_type:" + self.conversation_llm_model_driver_type)

        # 是否开启记忆摘要
        logger.debug("=> Memory Config")
        self.enable_longMemory = sys_config_json["memoryStorageConfig"]["enableLongMemory"]
        self.enable_summary = sys_config_json["memoryStorageConfig"]["enableSummary"]
        logger.debug("=> enable_longMemory：" + str(self.enable_longMemory))
        logger.debug("=> enable_summary：" + str(self.enable_summary))
        if self.enable_summary:
            self.summary_llm_model_driver_type = sys_config_json["memoryStorageConfig"]["languageModelForSummary"]
            logger.debug("=> summary_llm_model_driver_type：" + self.summary_llm_model_driver_type)

        self.enable_reflection = sys_config_json["memoryStorageConfig"]["enableReflection"]
        logger.debug("=> enableReflection：" + str(self.enable_reflection))
        if self.enable_reflection:
            self.reflection_llm_model_driver_type = sys_config_json["memoryStorageConfig"]["languageModelForReflection"]
            logger.debug("=> reflection_llm_model_driver_type" + self.reflection_llm_model_driver_type)

        # 初始化默认角色
        try:
            result = CustomRoleModel.objects.all()
            if len(result) == 0:
                logger.debug("=> load default character")
                custom_role = CustomRoleModel(
                    role_name=default_character.role_name,
                    persona=default_character.persona,
                    personality=default_character.personality,
                    scenario=default_character.scenario,
                    examples_of_dialogue=default_character.examples_of_dialogue,
                    custom_role_template_type=default_character.custom_role_template_type,
                    role_package_id=default_character.role_package_id
                )
                custom_role.save()
        except Exception as e:
            logger.error("=> load default character error: %s" % str(e))
        
        # 加载角色配置
        character = sys_config_json["characterConfig"]["character"]
        character_name = sys_config_json["characterConfig"]["character_name"]
        self.character = character
        self.character_name = character_name
        logger.debug("=> character Config")
        logger.debug(f"character:{character}")
        logger.debug(f"character_name:{character_name}")
        
        # 是否开启proxy
        enableProxy = sys_config_json["enableProxy"]
        logger.debug("=> Proxy Config ")
        logger.debug(f"enableProxy:{enableProxy}")
        if enableProxy:
            os.environ['HTTP_PROXY'] = sys_config_json["httpProxy"]
            os.environ['HTTPS_PROXY'] = sys_config_json["httpsProxy"]
            os.environ['SOCKS5_PROXY'] = sys_config_json["socks5Proxy"]
            logger.info(f"=> HTTP_PROXY:" + os.environ['HTTP_PROXY'])
            logger.info(f"=> HTTPS_PROXY:" + os.environ['HTTPS_PROXY'])
            logger.info(f"=> SOCKS5_PROXY:" + os.environ['SOCKS5_PROXY'])
        else:
            os.environ['HTTP_PROXY'] = ""
            os.environ['HTTPS_PROXY'] = ""
            os.environ['SOCKS5_PROXY'] = ""
        
        logger.info("=> Load SysConfig Success")

        # # 加载直播配置
        # if self.bili_live_client is not None:
        #     self.bili_live_client.stop()
        # room_id = str(sys_config_json["liveStreamingConfig"]["B_ROOM_ID"])
        # logger.info("=> liveStreaming Config")
        # self.room_id = room_id
        # self.bili_live_client = BiliLiveClient(room_id=room_id)
        # # 创建后台线程
        # background_thread = threading.Thread(
        #     target=asyncio.run(self.bili_live_client.start()))
        # # 将后台线程设置为守护线程，以便在主线程结束时自动退出
        # background_thread.daemon = True
        # # 启动后台线程
        # background_thread.start()
