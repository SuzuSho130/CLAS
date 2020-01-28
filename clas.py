from flask import Flask, request, abort
from slackbot.bot import Bot
from slackbot.bot import listen_to      # チャネル内発言で反応するデコーダ
import requests
import threading
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os
import pickle

class CLAS:

    def __init__(self, _token):
        self._slack_token = _token  # Slackのアクセストークン
        self._slack_headers = {'Content-Type': 'application/json'} 
        self.clas_group_list = {}   # 作成されたCLASグループのリスト
        self.clas_index = {}    # 各SNSのグループが所属しているCLASのIDの辞書
        self.clas_group_id = 0  # 現在のCLASグループのID
        self.read_clas_data()    # 保存されているファイルから情報を読み取る

    # 新規のCLASグループを作成
    def create_group(self, channel_id, sns_name):
        if channel_id in self.clas_index:
            return 'すでにグループに所属しています。\n一つのグループにしか所属はできません'
        clas_id = str(self.clas_group_id)
        self.clas_group_list[clas_id] = {'slack':[], 'line':[], 'database':[]}
        self.join_group(clas_id, sns_name, channel_id)
        self.clas_group_id += 1
        return clas_id
    
    # 既存のCLASグループに参加
    def join_group(self, clas_id, channel_id, sns_name):
        if channel_id in self.clas_index:
            return 'すでにグループに所属しています。\n一つのグループにしか所属はできません'
        if clas_id in self.clas_group_list:
            if channel_id in self.clas_group_list[clas_id][sns_name]:
                return 'そのグループはすでに登録されています'
            else:
                self.clas_group_list[clas_id][sns_name].append(channel_id)
                self.clas_index[channel_id] = clas_id
                return '追加が完了しました'
        else:
            return 'そのIDのグループは存在しません'

    # CLASグループから抜ける
    def leave_group(self, channel_id, sns_name):
        clas_id = self.get_clas_id(channel_id)
        self.clas_group_list[clas_id][sns_name].remove(channel_id)
        del self.clas_index[channel_id]
        return "グループ{}を抜けました".format(clas_id)

    # SNSのグループが既にCLASグループに所属しているかを判定
    def check_belong_to(self, channel_id):
        if channel_id in self.clas_index:
            return 'すでにグループに所属しています。\n一つのグループにしか所属はできません'

    # SNSのグループがどのCLASグループに所属しているかを取得
    def get_clas_id(self, channel_id):
        return self.clas_index[channel_id]

    # Line側のグループにメッセージを送信
    def send2line(self, channel_id, text):
        clas_id = self.get_clas_id(channel_id)

         # 送信元を除いたリストを生成
        send_list = [line_id for line_id in self.clas_group_list[clas_id]['line'] if line_id != channel_id]

        # 空のリストの場合スキップ
        if len(send_list) == 0:
            return
        try:
            line_bot_api.multicast(send_list, messages=TextSendMessage(text))
        except:
            pass

    # スラック側のグループにメッセージを送信
    def send2slack(self, channel_id, text):
        clas_id = self.get_clas_id(channel_id)
        for slack_channel in self.clas_group_list[clas_id]['slack']:
            if slack_channel == channel_id: # 送信元と同じ場合スキップ
                continue
            params = {"token": self._slack_token, "channel": slack_channel, "text": text}
            r = requests.get('https://slack.com/api/chat.postMessage',
                            headers=self._slack_headers,
                            params=params)
            print("return ", r.json())

    # データベースの中から条件に該当するメッセージをリストにして返す
    def search_database(self, channel_id, sns_name, text, count=10):
        search_list = []
        clas_id = self.get_clas_id(channel_id)
        for data in reversed(self.clas_group_list[clas_id]['database']):
            if text in data[sns_name]:
                search_list.append(str(data))
                if len(search_list)>=count:
                    break
        return search_list

    # 外部ファイルからCLASの情報を読み込む
    def read_clas_data(self, fname='clas.data'):
        if not os.path.exists(fname):
            return
        with open(fname, 'rb') as f:
            self.clas_group_list = pickle.load(f)

    # CLASの情報を外部ファイルに保存
    def write_clas_data(self, fname='clas.data'):
        with open(fname, 'wb') as f:
            pickle.dump(self.clas_group_list, f)

    # データベースにメッセージ情報を取得
    def add_database(self, channel_id, text):
        data = text.split(':')
        clas_id = self.get_clas_id(channel_id)
        self.clas_group_list[clas_id]['database'].append(data)
        self.write_clas_data()

    # コマンドメッセージを処理
    def command_message(self, sns_name, channel_id, text):
        message = ''
        if text[0:5] == '$info':            # 使用可能なコマンドを表示
            message = '$info:機能表示\n'\
                '$create:新規CLASグループを作成\n'\
                '$getID:所属CLASグループのID表示\n'\
                '$join [ID]:CLASグループに参加\n'\
                '$leave:CLASグループを脱退\n'\
                '$searchText [キーワード]:キーワードを用いて検索\n'\
                '$searchUser [ユーザー名]:ユーザー名で検索'
        elif text[0:8] == '$create':        # 新規CLASグループの作成
            message = str(self.create_group(sns_name, channel_id))
        elif text[0:7] == '$getID':         # 所属しているCLASグループのIDを取得
            message = str(self.get_clas_id(channel_id))
        elif text[0:6] == '$join ':         # CLASグループに参加
            message = self.join_group(text[6:], sns_name, channel_id)
        elif text[0:6] == '$leave':         # 参加しているCLASグループから脱退
            message = self.leave_group(channel_id, sns_name)
        elif text[0:12] == '$searchText ':  # データベースからテキスト内容が一致するメッセージを取得
            message = '\n'.join(self.search_database(channel_id, 1, text[12:]))
        elif text[0:12] == '$searchUser ':  # データベースからユーザー名が一致するメッセージを取得
            message = '\n'.join(self.search_database(channel_id, 0, text[12:]))
        else:
            message = 'そのコマンドは存在しません'
        return message

app = Flask(__name__)

# 環境変数取得
LINE_CHANNEL_ACCESS_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
LINE_CHANNEL_SECRET = os.environ["LINE_CHANNEL_SECRET"]
slack_token = os.environ["SLACK_CHANNEL_ACCESS_TOKEN"]

# Line Botのインスタンスを生成しWebhookの設定を行う
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# CLASのインスタンスを生成
clas = CLAS(slack_token)

# Lineのコールバックメソッド
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

# Slackで入力した内容をCLASグループに送信するメソッド
@listen_to('^(.*)$')
def listen_func(message, text):

    # Clasアプリケーションからの投稿の場合何もしない
    try:
        if 'OpenSNS' == message.body['username']:
            return
    except:
        pass

    try:
        # SlackチャンネルのIDを取得
        channel_id = message.body['channel']

        # コマンドメッセージの場合
        if text[0] == "$":
            clas.send2slack(channel_id, clas.command_message('slack', channel_id, text))

        # 送信者名とテキスト内容をCLASグループに送信し、グループのデータベースに保存  
        else:
            send_text = '[{}]:'.format(str(message.body['user'])) + text
            clas.add_database(channel_id, send_text)
            clas.send2line(channel_id, send_text)
            clas.send2slack(channel_id, send_text)
    except LineBotApiError as e:
        print(e)

# Lineで入力した内容をSlackに送信するメソッド
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    # 投稿されたメッセージの情報を取得
    profile = line_bot_api.get_profile(event.source.user_id)

    # Clasアプリケーションからの投稿の場合、何もしない
    if 'OpenSNS' == str(profile.display_name):
        return
    
    # LineグループのIDを取得
    channel_id = profile.user_id

    # コマンドメッセージの場合
    if event.message.text[0] == '$':
        clas.send2line(channel_id, clas.command_message('line', channel_id, event.message.text))
    
    # 送信者名とテキスト内容をCLASグループに送信し、グループのデータベースに保存
    else:
        send_text = '[{}]:'.format(str(profile.display_name)) + event.message.text
        clas.add_database(channel_id, send_text)
        clas.send2slack(channel_id, send_text)
        clas.send2line(channel_id, send_text)

# Line Botを起動する関数
def run_line_bot():
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

# Slack Botを起動する関数
def run_slack_bot():
    bot = Bot()
    bot.run()

if __name__ == "__main__":

    # 各botを同時に実行するために並列処理
    slack_thread = threading.Thread(target=run_slack_bot)
    line_thread = threading.Thread(target=run_line_bot)
    slack_thread.start()
    line_thread.start()
