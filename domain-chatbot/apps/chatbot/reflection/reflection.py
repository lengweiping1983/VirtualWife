import json
import logging

from ..config import singleton_sys_config
from ..llms.llm_model_strategy import LlmModelDriver


logger = logging.getLogger(__name__)





# class ReflectionGeneration():
#     reflection_template: ReflectionTemplate

#     def __init__(self) -> None:
#         self.reflection_template = ReflectionTemplate()

#     def generation(self, role_name: str) -> None:
#         timestamp = time.time()
#         expr = f'timestamp <= {timestamp}'
#         result = memory_storage_driver.pageQuery(
#             1, 100, expr)

#         result = [item['text'] for item in result]
#         prompt = self.reflection_template.format(result)

#         reflection_result = memory_storage_driver.chat(type=singleton_sys_config.reflection_llm_model_driver_type,
#                                                                             prompt=prompt,
#                                                                             user_name="",
#                                                                             user_text="",
#                                                                             role_name=role_name, 
#                                                                             short_history="")
#         reflection_result_arr = self.reflection_template.output_format(reflection_result)

#         # 批量写入到向量数据库中
#         for i in range(len(reflection_result_arr)):
#             item = reflection_result_arr[i].strip()
#             pk = memory_storage_driver.get_current_entity_id()
#             memory_storage_driver.save(pk, item, role_name)



