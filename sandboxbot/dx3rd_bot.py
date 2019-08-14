################################################################
#
# ファイル名：dx3rd_bot.py
# 処理機能　：DX3rd キャラクター作成支援機能
# メ　　モ　：作成中だけど利用者がいないから作成中断
#
################################################################

################################################################
#
# ライブラリのインポート
#
################################################################
# Python標準ライブラリ
import re                   # 正規表現モジュール
import random               # 乱数生成モジュール
import math                 # 数学処理モジュール

# 有志制作のライブラリ
import discord              # discord用APIラッパー   ver1.0.1

# 自作モジュール
from . import dice_bot       # ダイスを振る
from . import randam_table  # 指定したランダム表を振る

################################################################
#
# Dx3rdBot
#
################################################################
class Dx3rdBot:
    ############################################################
    # 処理内容：コンストラクタ
    # 関数名　：__init__
    # 引数　　：self        / メソッドの仮引数
    # 戻り値　：なし
    ############################################################
    def __init__(self):
        # randam_table.py
        self.__randam_table = randam_table.RandamTable()
        # dicebot.py
        self.__dicebot = dice_bot.DiceBot()

    ############################################################
    #
    # クラス変数
    #
    ############################################################
    # 邂逅表のファイルパス
    __FILEPATH_MOTH = "./randam_table/dx3rd/dx3rd_moth.csv"
    
    ############################################################
    # 処理内容：message投稿時
    # 関数名　：dx3rd_on_message
    # 引数　　：self        / メソッドの仮引数
    #        : message    / message構造体
    # 戻り値　：なし
    ############################################################
    async def dx3rd_on_message(self, message):

        if isinstance(message.channel, discord.DMChannel):
            # botへのDM送信時、処理を終了する
            return

        # DX3rdヘルプコマンド
        if re.match('\$dx3rd_help', message.content):
            await self.dx3rd_help(message)

        # DX3rd 邂逅表を振る
        elif re.match('\$dx3rd_moth', message.content):
            send_ms = self.dx3rd_moth()
            await message.channel.send(send_ms)
            
    ############################################################
    # 処理内容：help表示
    # 関数名　：dx3rd_help
    # 引数　　：self     / メソッドの仮引数
    #        : message / メッセージ構造体
    # 戻り値　：なし
    ############################################################
    async def dx3rd_help(self, message):
        # ヘルプメッセージ
        HELP_MSG =['``` ### DX3rdを遊ぶ(現在作成中) ###',
                   '$dx3rd_moth 邂逅表を振り、結果を表示する。',
                   '``` ']

        # 送信用メッセージ
        send_ms = ''

        # ヘルプメッセージの生成
        for ele_help in HELP_MSG:
            # ヘルプの配列を順番にmesへ格納
            send_ms = send_ms + ele_help + '\n'

        # 実行結果をテキストチャンネルに送信
        await message.channel.send(send_ms)
        
    ############################################################
    # 処理内容：邂逅表を振る
    # 関数名　：dx3rd_moth
    # 引数　　：self   / メソッドの仮引数
    # 戻り値　：なし
    ############################################################
    def dx3rd_moth(self):
        # 邂逅表を振る 1d100
        roll = self.__dicebot.dice_roll_int(1, 100, 0)
        
        # 邂逅表の何行目を見ればいいか、行数を指定
        ## dx3rdの邂逅表はダイス目5づつ1行が指定される。
        ## プログラミング上表の始まりは0行なので
        ## ダイスの出目/5から-1する。
        row = math.ceil(roll / 5) - 1
        
        # 邂逅表の何列目を取得するか指定
        ## 今回は1～5列目
        column = [0,1,2,3,4]
        
        # 邂逅表の値を取得
        send_ms = self.__randam_table.result_randam_table_message(self.__FILEPATH_MOTH,
                                                                  row,
                                                                  column,
                                                                  ","
                                                                  )
        # 結果を返却する
        return send_ms

