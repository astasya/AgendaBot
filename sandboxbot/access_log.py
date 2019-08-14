################################################################
#
# ファイル名：access_log.py
# 処理機能　：アクセスログ解析機能
#
# メ　　モ　：2018/12/13
#           前任者の段階で既に挙動がおかしかったらしい
#           一度コード全体見直し、確認が必要
#
# メ　　モ　：2019/08/13
#           見直したところ、メンバ追加処理等必要な関数が呼び出されていない。
#           このままでは動くはずがないので、この機能が必要になったら
#           作りなおす必要あり。
#
################################################################

################################################################
#
# ライブラリのインポート
#
################################################################
# Python標準ライブラリ
import re                   # 正規表現モジュール
import datetime             # 時間を扱うモジュール

# 有志制作のライブラリ
import discord              # discord用APIラッパー   ver1.0.1

################################################################
#
# Alog
#
################################################################
class Alog:
    ############################################################
    # 処理内容：コンストラクタ
    # 関数名　：__init__
    # 引数　　：self      / メソッドの仮引数
    # 戻り値　：なし
    ############################################################
    def __init__(self):
        self.today = datetime.date.today().day
        self.unique_member_list = []

    ############################################################
    # 処理内容：クラス変数の初期化処理
    # 関数名　：reset_val
    # 引数　　：self      / メソッドの仮引数
    # 戻り値　：なし
    ############################################################
    def reset_val(self):
        self.today = datetime.date.today().day
        self.unique_member_list = []
        
    ############################################################
    # 処理内容：message投稿時
    # 関数名　：alog_on_message
    # 引数　　：self        / メソッドの仮引数
    # 戻り値　：なし
    ############################################################
    async def alog_on_message(self,
                              message
                             ):
        
        if isinstance(message.channel, discord.DMChannel):
            # botへのDM送信時、処理を終了する
            return
        
        # log解析コマンド
        if re.match('\$logs', message.content):
            await self.debug_print_str()

    ############################################################
    # 処理内容：log解析結果表示?
    # 関数名　：print_logs_str
    # 引数　　：self      / メソッドの仮引数
    # 戻り値　：なし
    ############################################################
    async def print_logs_str(self):
        
        header = f"本日のアクセス人数は[{str(len(self.unique_member_list))}人でした。\r\n"
        member_table = "\r\n".join(self.unique_member_list)
        send_ms = header + member_table

        # クラス変数の初期化
        self.reset_val()
        await message.channel.send(send_ms)
    
    ## メモ : 2019/08/13
    ## なぜか以下の関数呼び出しないけど？
    ## これどう作りたかったの？　作り直しじゃねーか！

    ############################################################
    # 処理内容：メンバー追加処理?
    # 関数名　：add_member_list
    # 引数　　：self       / メソッドの仮引数
    #        ：member_tmp / 
    # 戻り値　：なし
    ############################################################
    def add_member_list(self, member_tmp):
        if not member_tmp.voice.voice_channel == None \
        and self.unique_member_list.count(member_tmp.name) == 0:
            self.unique_member_list.append(member_tmp.name)

    ############################################################
    # 処理内容：時刻更新処理?
    # 関数名　：is_update_time
    # 引数　　：self      / メソッドの仮引数
    # 戻り値　：なし
    ############################################################
    def is_update_time(self):
        now = datetime.date.today().day
        if not now == self.today:
            return True
