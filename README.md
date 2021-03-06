# CLAS -Connects LINE and Slack-

SNSアプリ「LINE」と「Slack」間でメッセージを共有できるアプリケーションです。

## Description

SNSアプリ「LINE」と「Slack」間でメッセージを共有できるアプリケーションです。各SNSのAPIを利用することでメッセージのやり取りを行います。

各SNSの既存のグループにCLASアプリケーション（BOT）を招待して利用します。

新たにCLASグループを作成することで、同一CLASグループにグループに所属しているメンバー間でメッセージが共有されるようになります。

CLASグループはデータベースを持っており、SNSにメッセージ投稿されたとき、送信者名とメッセージ内容がデータベースに保存されます。
このデータベースを利用することで、ユーザー名やキーワードでメッセージを検索できます。

※各SNSのグループは一つのCLASグループにしか所属できません。
※CLASアプリケーションを招待しても、CLASグループに参加していない場合は[$create][$join]を除くCLASの機能を利用することができません。

## Image

<img src="https://github.com/SuzuSho130/CLAS/blob/images/CLAS例.png" width="640px">

## Requirement

Flask 1.0.2

line-bot-sdk 1.15.0

slackbot 0.5.6

requests 2.21.0

## Usage

### 使用する準備

1. 各SNSのアクセストークンなどを取得し、サーバーの環境変数に設定
1. サーバーに[clas.py][slackbot_settings.py][plugins]をアップロード

### アプリケーション利用方法

1. 各SNSのグループにてCLASアプリケーション（BOT）を招待する
1. [$create]と入力することで新規CLASグループ作成、または、[$join ID]と入力することで既存のCLASグループに参加
1. メンバーの一人がメッセージを投稿するとCLASグループ内の各SNSでメッセージが共有されます

### CLAS機能

|コマンド|機能|
----|----
|$info|CLASの使用可能な機能を表示|
|$create|新規CLASグループを作成|
|$getID|所属CLASグループのIDを表示|
|$join [ID]|CLASグループに参加|
|$leave|CLASグループを脱退|
|$searchText [キーワード]|キーワードを用いて検索|
|$searchUser [ユーザー名]|ユーザー名で検索|

### CLASグループについて

CLASグループが持つ属性

1. CLAS ID
1. CLASグループに所属しているLINEのグループのIDリスト
1. CLASグループに所属しているSlackのグループのIDリスト
1. CLASグループに投稿されたメッセージを保存するためのデータベース

LINEとSlackのグループを作成できる他、LINEグループ同士、Slackグループ同士でもCLASグループを作成できます。

## Author

[Suzusho130](https://github.com/Suzusho130)
