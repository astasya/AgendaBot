################################################################
#
# ファイル名：server_management.py
# 処理機能　：サーバー管理機能
#
################################################################

################################################################
#
# ライブラリのインポート
#
################################################################
# Python標準ライブラリ
import re                           # 正規表現モジュール
import datetime                     # 時刻を扱うモジュール

# 有志制作のライブラリ
import discord                      # discord用APIラッパー   ver1.0.1

################################################################
#
# 定数
#
################################################################

################################################################
#
# Mgmt
#
################################################################
class Mgmt:
    
    ############################################################
    # 処理内容：コンストラクタ
    # 関数名　：__init__
    # 引数　　：self     / メソッドの仮引数
    # 　　　　：vc_list  / 現在のVC接続者のリスト
    # 戻り値　：なし
    ############################################################
    def __init__(self):
        # DB生成処理
        pass

    ############################################################
    # 処理内容：message投稿時
    # 関数名　：alog_on_message
    # 引数　　：self     / メソッドの仮引数
    # 　　　　：guild    / ギルドクラス
    # 　　　　：message  / メッセージクラス
    # 戻り値　：なし
    ############################################################
    async def mgmt_on_message(self, guild, message):
        
        if isinstance(message.channel, discord.DMChannel):
            # botへのDM送信時、処理を終了する
            return

        if(message.author.bot):
            # メッセージの投稿者がBotの場合、処理を終了する
            return

        # ヘルプコマンド
        if re.match('\$mgmt_help', message.content):
            await self.mgmt_help(message)
            
        # サーバ所属人数取得
        if re.match('\$mgmt_members', message.content):
            await self.mgmt_members(message)
        
        # 対象者の鯖加入日検索
        if re.match('\$mgmt_id', message.content):
            await self.mgmt_join_date(guild, message)

    ############################################################
    # 処理内容：help表示
    # 関数名　：mgmt_help
    # 引数　　：self     / メソッドの仮引数
    # 　　　　：message  / メッセージクラス
    # 戻り値　：なし
    ############################################################
    async def mgmt_help(self, message):
        # ヘルプメッセージ
        HELP_MSG =['``` ### Sandbox鯖 管理機能 ###',
                   '$mgmt_members 現在のSandbox参加者数を表示します。',
                   '$mgmt_id_[整数] 指定ユーザのSandbox加入日を表示します。',
                   '```',]

        # 送信用メッセージ
        send_ms = ''

        # ヘルプメッセージの生成
        for ele_help in HELP_MSG:
            # ヘルプの配列を順番にmesへ格納
            send_ms = send_ms + ele_help + '\n'

        # 実行結果をテキストチャンネルに送信
        await message.channel.send(send_ms)

    ############################################################
    # 処理内容：サーバのユーザ総数取得
    # 関数名　：mgmt_members
    # 引数　　：self     / メソッドの仮引数
    # 　　　　：message  / メッセージクラス
    # 戻り値　：なし
    ############################################################
    async def mgmt_members(self, message):
        # 参加人数の初期化
        num = 0
        
        # botではないユーザ数をカウント
        for member in message.guild.members:
            if member.bot == False:
                num += 1
            
        await message.channel.send(f'現在のSandbox参加者は{num}人です。')
        
    ############################################################
    # 処理内容：解析処理
    # 関数名　：mgmt_join_date
    # 引数　　：self     / メソッドの仮引数
    # 　　　　：guild    / ギルドクラス
    # 　　　　：message  / メッセージクラス
    # 戻り値　：なし
    ############################################################
    async def mgmt_join_date(self, guild, message):
        # 送信メッセージの初期化
        send_ms = None
        
        # idの取得
        user_id = int( ((message.content).split("_"))[2] )
        
        # memberの取得
        member = guild.get_member(user_id)
        
        if member == None:
            # member取得失敗時、エラーを返す
            send_ms = 'エラー：IDを確認してください。'
            
        else:
            # member取得成功時、加入日時をを返す
            date = (member.joined_at).strftime('%Y/%m/%d %H:%M')
            name = member.nick
            if name == None:
                name = member.name

            send_ms = f'{name}さんのSandbox加入日時は{date}です。'

        await message.channel.send(send_ms)
