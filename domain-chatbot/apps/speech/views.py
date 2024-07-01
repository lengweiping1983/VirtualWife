from io import BytesIO

from django.shortcuts import render
import os
import json
import logging
from django.http import FileResponse
from .translation import translationClient
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .tts import single_tts_driver
from django.http import HttpResponse, StreamingHttpResponse
from ..chatbot.utils.str_utils import remove_special_characters, remove_emojis


logger = logging.getLogger(__name__)

@api_view(['POST'])
def generate(request):
    """
    Generate audio from text.
    """
    try:
        data = json.loads(request.body.decode('utf-8'))
        text = data["text"]
        voice_id = data["voice_id"]
        type = data["type"]

        # 删除表情符号和一些特定的特殊符号，防止语音合成失败
        text = remove_emojis(text)
        # text = remove_special_characters(text)
        print(f"generate text: {text}")

        # file_name = single_tts_driver.synthesis(
        #     type=type, text=text, voice_id=voice_id)
        file_name = "output.wav"
        file_path = os.path.join("tmp", file_name)

        import requests

        # 请求的 URL
        url = "http://127.0.0.1:9880/"  # 替换为实际的 URL

        # 要发送的数据
        payload = {
            "text": text,
            "text_language": "zh"
        }

        # 请求头，可选
        headers = {
            "Accept": "audio/wav",
            "Content-Type": "application/json"
        }

        # 发送 POST 请求
        response = requests.post(url, json=payload, headers=headers, stream=True)

        # 检查响应状态码
        if response.status_code == 200:
            print("POST 请求成功，开始下载音频流...")
            
            # 将音频流保存到文件
            with open(file_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"音频已保存为 {file_path}")
        else:
            print(f"请求失败，状态码: {response.status_code}")


        audio_file = BytesIO()
        with open(file_path, 'rb') as file:
            audio_file.write(file.read())

        delete_file(file_path)
        logger.debug(f"delete file :{file_path}")

        audio_file.seek(0)

        # Create the response object.
        response = HttpResponse(content_type='audio/mpeg')
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        response.write(audio_file.getvalue())
        return response
    except Exception as e:
        logger.error(f"generate_audio error: {e}")
        return HttpResponse(status=500, content="Failed to generate audio.")


def delete_file(file_path):
    os.remove(file_path)

@api_view(['POST'])
def get_voices(request):
    data = json.loads(request.body.decode('utf-8'))
    type = data["type"]
    return Response({"response": single_tts_driver.get_voices(type=type), "code": "200"})

@api_view(['POST'])
def translation(request):
    """
    translation
    """
    try:
        data = json.loads(request.body.decode('utf-8'))
        text = data["text"]
        target_language = data["target_language"]
        target_result = translationClient.translation(
            text=text, target_language=target_language)
        return Response({"response": target_result, "code": "200"})
    except Exception as e:
        logger.error(f"translation error: {e}")
        return HttpResponse(status=500, content="Failed to translation error.")
