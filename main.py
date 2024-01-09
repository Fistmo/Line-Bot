from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import requests

app = Flask(__name__)

# Line Bot的Channel Secret和Channel Access Token
line_bot_api = LineBotApi('')
handler = WebhookHandler('')

# ChatGPT的API密钥和API URL
chatgpt_api_key = ''
chatgpt_api_url = 'https://api.openai.com/v1/chat/completions'


@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text

    # 使用ChatGPT API处理用户消息
    chatgpt_response = get_chatgpt_response(user_message)

    # 发送ChatGPT的回复到Line
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=chatgpt_response)
    )


def get_chatgpt_response(user_message):
    headers = {'Authorization': f'Bearer {chatgpt_api_key}'}
    data = {'messages': [{'role': 'system', 'content': 'You are a helpful assistant.'}, {
        'role': 'user', 'content': user_message}], 'model': 'gpt-3.5-turbo'}

    response = requests.post(chatgpt_api_url, json=data, headers=headers)
    response_json = response.json()
    print(' ')
    print(response_json)
    print(' ')

    chatgpt_response = response_json['choices'][0]['message']['content']

    return chatgpt_response


if __name__ == "__main__":
    app.run()
