import re


def format_chat_text(user_name: str, role_name: str, text: str):
    # 去除特殊字符 *、`user_name:`、`role_name：`
    pattern = r'\*.*?\*'
    text = text.replace(f'`', "")
    text = re.sub(pattern, '', text)
    text = text.replace(f'{role_name}：', "")
    text = text.replace(f'{user_name}：', "")
    text = text.replace(f'{role_name}:', "")
    text = text.replace(f'{user_name}:', "")
    text = text.replace(f'{role_name}说', "")
    text = text.replace(f'{user_name}说', "")
    text = text.replace(f'AI角色：', "")
    text = text.replace(f'AI（{role_name}）：', "")
    text = text.replace(f'AI:', "")
    text = text.replace(f'Ai：', "")
    text = text.replace(f'ai：', "")
    text = text.replace('[', "")
    text = text.replace(']', "")
    return text


def format_user_chat_text(text: str):
    text = text.replace('[', "")
    text = text.replace(']', "")
    return text


def format_message(user_name: str, user_text: str, role_name: str, role_text: str):
    user_message = format_user_message(
        user_name=user_name, user_text=user_text)
    role_message = format_role_message(
        role_name=role_name, role_text=role_text)
    chat_message = user_message + '\n' + role_message
    return chat_message


def format_user_message(user_name: str, user_text: str):
    user_message = f"{user_name}：{user_text}"
    return user_message


def format_role_message(role_name: str, role_text: str):
    role_message = f"你：{role_text}"
    return role_message
