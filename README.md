# CLAS -Connects LINE and Slack-

SNSアプリ「LINE」と「Slack」間でメッセージを共有できるアプリケーションです。

## Description

SNSアプリ「LINE」と「Slack」間でメッセージを共有できるアプリケーションです。

各SNSの既存のグループにCLASアプリケーション（BOT）を招待して利用します。

新たにCLASグループを作成することで、同一CLASグループにグループに所属しているメンバー間でメッセージが共有されるようになります。

※各SNSのグループは一つのCLASグループにしか所属できません

## Image

<img src="https://github.com/SuzuSho130/CLAS/blob/images/CLAS例.png" width="640px">

## Requirement

Flask 1.0.2

line-bot-sdk 1.15.0

slackbot 0.5.6

requests 2.21.0

## Usage

使用する準備

1. 各SNSのアクセストークンなどを取得し、サーバーの環境変数に設定
1. サーバーに[clas.py][slackbot_settings.py][plugins]をアップロード

アプリケーション利用方法

1. 各SNSのグループにてCLASアプリケーション（BOT）を招待する
1. [$create]と入力することで新規CLASグループ作成、または、[$join ID]と入力することで既存のCLASグループに参加
1. 同一CLASグループ内で送信されたメッセージが各SNSで共有されます

CLAS機能

|コマンド|機能|
----|----
|$info|機能表示|
|$create|新規CLASグループを作成|
|$getID|所属CLASグループのID表示|
|$join [ID]|CLASグループに参加|
|$leave|CLASグループを脱退|
|$searchText [キーワード]|[キーワード]:キーワードを用いて検索|
|$searchUser [ユーザー名]|[ユーザー名]:ユーザー名で検索|


## Author

[Suzusho130](https://github.com/Suzusho130)
