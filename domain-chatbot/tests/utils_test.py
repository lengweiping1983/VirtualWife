import re
text = "篮球还行吧，不过我更喜欢看电影和旅行。你喜欢篮球吗？"

match = re.match(r"^(.+[。．！？\n]|.{10,}[、,])", text)
if match:
    message_text = match.group()

    print(message_text)