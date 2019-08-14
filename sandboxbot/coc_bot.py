################################################################
#
# ファイル名：coc_bot.py
# 処理機能　：CoC キャラクター作成支援機能
#
################################################################

################################################################
#
# ライブラリのインポート
#
################################################################
# Python標準ライブラリ
import re               # 正規表現モジュール
import random           # 乱数生成モジュール
import math             # 数学処理モジュール

# 有志制作のライブラリ
import discord              # discord用APIラッパー   ver1.0.1

# 自作ライブラリ
from . import dice_bot  # ダイスを振る

################################################################
#
# CoCBot
#
################################################################
class CoCBot:

    ############################################################
    # 処理内容：コンストラクタ
    # 関数名　：__init__
    # 引数　　：self        / メソッドの仮引数
    # 戻り値　：なし
    ############################################################
    def __init__(self):#インスタンス変数管理
        # dice_bot.py
        self.__dicebot = dice_bot.DiceBot()

    ############################################################
    # 処理内容：message投稿時
    # 関数名　：coc_on_message
    # 引数　　：self        / メソッドの仮引数
    #        : message    / message構造体
    # 戻り値　：なし
    ############################################################
    async def coc_on_message(self, message):

        if isinstance(message.channel, discord.DMChannel):
            # botへのDM送信時、処理を終了する
            return

        # CoCBotヘルプコマンド
        if re.match('\$coc_help', message.content):
            await self.coc_help(message)

        # CoCキャラ作成コマンド
        elif re.match('\$coc_stat', message.content):
            await self.coc_stat(message)

    ############################################################
    # 処理内容：help表示
    # 関数名　：coc_help
    # 引数　　：self     / メソッドの仮引数
    #        : message / メッセージ構造体
    # 戻り値　：なし
    ############################################################
    async def coc_help(self, message):
        # ヘルプメッセージ
        HELP_MSG =['``` ### CoCを遊ぶ ###',
                   '$coc_stat 探索者の初期値を3回生成し、結果を表示する。',
                   '```']

        # 送信用メッセージ
        send_ms = ''

        # ヘルプメッセージの生成
        for ele_help in HELP_MSG:
            # ヘルプの配列を順番にmesへ格納
            send_ms = send_ms + ele_help + '\n'

        # 実行結果をテキストチャンネルに送信
        await message.channel.send(send_ms)
            
    ############################################################
    # 処理内容：ステータスを3回振る
    # 関数名　：coc_stat
    # 引数　　：self     / メソッドの仮引数
    #        : message / メッセージ構造体
    # 戻り値　：なし
    ############################################################
    async def coc_stat(self, message):
        # メッセージの初期化
        send_ms = ""
        
        # 3回キャラ作成実行
        for i in range(0,3):
            ret_ms = self.coc_stat_sub()
            send_ms = send_ms + \
                      f"{i + 1}回目\n" \
                      f"{ret_ms}\n\n"
        
        # 実行結果をテキストチャンネルに送信
        await message.channel.send(send_ms)

    ############################################################
    # 処理内容：ステータスを決定する
    # 関数名　：coc_stat_sub
    # 引数　　：self   / メソッドの仮引数
    # 戻り値　：なし
    ############################################################
    def coc_stat_sub(self):
        stat = []
        
        # STR/CON/POW/DEX/APP 5回3d6を振る
        for i in range(0, 5):
            dice_result = self.__dicebot.dice_roll_int(3, 6, 0)
            stat.append(dice_result)
        
        # SIZ/INT 2回2d6+6を振る
        for i in range(0, 2):
            dice_result = self.__dicebot.dice_roll_int(2, 6, 6)
            stat.append(dice_result)

        #EDU 3d6+3
        dice_result = self.__dicebot.dice_roll_int(3, 6, 3)
        stat.append(dice_result)

        #DBポイントはSTR+SIZ
        tmp_db = stat[0]+stat[5]

        #DBダイスはDBポイントに合わせてp.46に合わせて決定
        #なお初期作成ではDBポイントは最大36
        db = ""
        if tmp_db <= 12:
            db = "-1d6"
        elif tmp_db <= 16:
            db = "-1d4"
        elif tmp_db <= 24:
            db = "-0"
        elif tmp_db <= 32:
            db = "+1d4"
        else:
            db = "+1d6"

        # 結果の文字列を返す
        send_ms =   f"STR:{stat[0]}, " \
                    f"CON:{stat[1]}, " \
                    f"POW:{stat[2]}, " \
                    f"DEX:{stat[3]}, " \
                    f"APP:{stat[4]}, " \
                    f"SIZ:{stat[5]}, " \
                    f"INT:{stat[6]}, " \
                    f"EDU:{stat[7]}\n" \
                    f"HP:{math.ceil((stat[1]+stat[5])/2)}, " \
                    f"MP:{stat[2]}, " \
                    f"SAN:{stat[2]*5}\n" \
                    f"幸運P:{stat[2]*5}, " \
                    f"アイデアP:{stat[6]*5}, " \
                    f"知識P:{stat[7]*5}\n" \
                    f"職業P:{stat[7]*20}, " \
                    f"趣味P:{stat[6]*10}, " \
                    f"DB:{db}" \
        
        return send_ms

        
