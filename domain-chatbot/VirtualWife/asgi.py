"""
ASGI config for VirtualWife project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from django.urls import path
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator

from apps.chatbot.output.routing import websocket_urlpatterns
from apps.chatbot.output.realtime_message_queue import RealtimeMessageQueryJobTask
from apps.chatbot.output.chat_history_queue import ChatHistoryMessageQueryJobTask
from apps.chatbot.insight.insight_message_queue import InsightMessageQueryJobTask
from apps.chatbot.schedule.summary_memory import run_summary_memory_job, summary_memory_job
from apps.chatbot.schedule.topic_memory import run_topic_memory_job, topic_memory_job
from apps.chatbot.schedule.emotion_memory import run_emotion_memory_job, emotion_memory_job
# from apps.chatbot.insight.bilibili.bili_live_client import bili_live_client_main


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VirtualWife.settings')

RealtimeMessageQueryJobTask.start()
ChatHistoryMessageQueryJobTask.start()
InsightMessageQueryJobTask.start()
run_summary_memory_job(180, summary_memory_job)
run_topic_memory_job(160, topic_memory_job)
run_emotion_memory_job(200, emotion_memory_job)
# bili_live_client_main()

# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(URLRouter(websocket_urlpatterns))
    ),
})
