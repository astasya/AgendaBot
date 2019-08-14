################################################################
#
# ファイル名：useful_link
# 処理機能　：便利サイトの紹介機能
#
################################################################

################################################################
#
# ライブラリのインポート
#
################################################################
# Python標準ライブラリ
import re       # 正規表現モジュール

# 有志制作のライブラリ
import discord  # discord用APIラッパー   ver1.0.1

################################################################
#
# 入力するTXTファイルの内容
#   1.ファイルはutf8で記述すること
#   2.各行は","区切りで最大3フィールドであること。
#   3.カテゴリ名を記述した行は、第2フィールドを"-"とすること。
#   4.最終行に改行を含めないこと。
#
################################################################
# カテゴリ名1,-
# ハイパーリンクテキスト1,URL1,説明1
# ハイパーリンクテキスト2,URL2,説明2
# カテゴリ名2,-
# ハイパーリンクテキスト1,URL1,説明1
# ハイパーリンクテキスト2,URL2,説明2
#   :
#   :

################################################################
#
# UsefulLink
#
################################################################
class UsefulLink:

    ############################################################
    # 処理内容：コンストラクタ
    # 関数名　：__init__
    # 引数　　：self        / メソッドの仮引数
    # 戻り値　：なし
    ############################################################
    def __init__(self):
        self.__fileLines = []
        
    ############################################################
    # 処理内容：message投稿時
    # 関数名　：usefullink_on_message
    # 引数　　：self        / メソッドの仮引数
    #        : message    / message構造体
    # 戻り値　：なし
    ############################################################
    async def usefullink_on_message(self, message, CH_BOT):

        if isinstance(message.channel, discord.DMChannel):
            # botへのDM送信時、処理を終了する
            return
        
        if re.match('\$useful_link', message.content):
            # 便利サイトの一覧を送信
            await self.output_useful_link(CH_BOT)
    
    ############################################################
    # 処理内容：ファイルを読み込む
    # 関数名　：file_read
    # 引数　　：self   / メソッドの仮引数
    # 戻り値　：なし
    ############################################################
    def file_read(self):
        # クラス変数の初期化
        self.__fileLines = []
        
        # ファイルをオープンする
        test_data = open("./UsefulLink.txt", "r", encoding="utf8")

        # 行ごとにすべて読み込んでリストデータにする
        self.__fileLines = test_data.readlines()

        # ファイルをクローズする
        test_data.close()

    ############################################################
    # 処理内容：UsefulLink出力
    # 関数名　：session_list_send
    # 引数　　：self / メソッドの仮引数
    #        : discord / discord構造体
    #        : client  / client構造体
    #        : chBot   / CH ID(#Bot)
    # 戻り値　：なし
    ############################################################   
    async def output_useful_link(self, CH_BOT):
        # send_messageの初期化
        send_message = ""
        category_name = ""
        
        # ファイル読み込み
        self.file_read()
        
        # ファイル内容からメッセージを作成
        for line in self.__fileLines:
            message = line.split(",")
            if message[1] == "-\n":
                if send_message is not "":
                    embed = discord.Embed(title=f"{category_name}",
                                          description=f"{send_message}"
                                         )
                    # メッセージの送信
                    await CH_BOT.send(embed=embed)
                    
                    # メッセージの初期化
                    send_message = ""
                    
                category_name = f"{message[0]}"
            else:
                links_row = f"[{message[0]}]({message[1]})" \
                            f":{message[2]}\n"
                send_message = send_message + links_row
        
        # 埋め込みメッセージの作成
        embed = discord.Embed(title=f"{category_name}",
                              description=f"{send_message}"
                             )

        # メッセージの送信
        await CH_BOT.send(embed=embed)

        
