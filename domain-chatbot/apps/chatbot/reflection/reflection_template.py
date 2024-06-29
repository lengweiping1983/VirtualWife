import re
import json


class ReflectionTemplate():

    prompt: str = """Please help me deduce 5 advanced insights,and output it in the following format:
                    You Insights: Each Insight ends with #
                    Statements about {role_name}
                    {historys}
                    {input}
                 """
    
    def __init__(self) -> None:
        pass

    def format(self, historys: list[str]) -> str:
        if len(historys) == 0:
            raise TypeError("historys is null")

        historys_str = ""
        for i, insight in enumerate(historys):
            historys_str += f"{i+1}. {insight}\n"

        return self.prompt.format(role_name="{role_name}", historys=historys_str, input="{input}")

    def output_format(self, text: str) -> list[str]:
        insights = text.replace("You Insights:", "")
        insights_list = re.split(r'\s*#\s*', insights)
        # 去除编号
        for i in range(len(insights_list)):
            insights_list[i] = insights_list[i].replace(
                str(i+1) + ". ", "")

        # 移除空字符串
        insights_list = [item.strip() for item in insights_list if item.strip()]
        return insights_list
