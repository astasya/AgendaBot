################################################################
#
# ファイル名：dice_bot.py
# 処理機能　：ダイスを振る機能
#
################################################################

################################################################
#
# ライブラリのインポート
#
################################################################
# Python標準ライブラリ
import re       # 正規表現モジュール
import random   # 乱数生成モジュール

# 有志制作のライブラリ
import discord              # discord用APIラッパー   ver1.0.1

################################################################
#
# DiceBot
#
################################################################
class DiceBot:
    
    ############################################################
    # 処理内容：コンストラクタ
    # 関数名　：__init__
    # 引数　　：self / メソッドの仮引数
    # 戻り値　：なし
    ############################################################
    def __init__(self):
        self.dice_ary = []
        self.dice_num  = ""
        self.dice_sort  = ""
        self.dice_total = ""
        self.dice_mean = ""

    ############################################################
    # 処理内容：クラス変数の初期化
    # 関数名　：dice_param_init
    # 引数　　：self / メソッドの仮引数
    # 戻り値　：なし
    ############################################################
    def dice_param_init(self):
        self.dice_ary = []
        self.dice_num  = ""
        self.dice_sort  = ""
        self.dice_total = ""
        self.dice_mean = ""
        return

    ############################################################
    # 処理内容：message投稿時
    # 関数名　：dice_on_message
    # 引数　　：self        / メソッドの仮引数
    #        : message    / message構造体
    # 戻り値　：なし
    ############################################################
    async def dice_on_message(self, message):

        if isinstance(message.channel, discord.DMChannel):
            # botへのDM送信時、処理を終了する
            return

        # Dicebotヘルプコマンド
        if re.match('\$dice_help', message.content):
            await self.dice_help(message)

        # ダイス(振るだけ)
        elif re.match('\$\d+d\d+', message.content):
            # 投稿メッセージからダイスの目と数を取得
            dice_cmd_list = re.findall('\d+',message.content)
            
            # ダイスを振った結果を取得する
            send_ms = self.dice_roll_str(int(dice_cmd_list[0]),
                                         int(dice_cmd_list[1])
                                        )
            
            # 結果を表示する
            await message.channel.send(send_ms)

        # ダイス(ソートして振る)
        elif re.match('\$[sS]\d+d\d+', message.content):
            # 投稿メッセージからダイスの目と数を取得
            dice_cmd_list = re.findall('\d+',message.content)

            # ダイスを振った結果を取得する
            send_ms = self.dice_roll_sort_str(int(dice_cmd_list[0]),
                                              int(dice_cmd_list[1])
                                             )
            # 結果を表示する
            await message.channel.send(send_ms)
            
        # 電卓機能
        elif re.match('\$calc', message.content):
            # 計算を行った結果を取得する
            send_ms = self.calulation(message.content)
            
            # 計算結果を表示する
            await message.channel.send(send_ms)

    ############################################################
    # 処理内容：message投稿時
    # 関数名　：dice_on_message
    # 引数　　：self        / メソッドの仮引数
    #        : message    / message構造体
    # 戻り値　：なし
    ############################################################
    async def dice_help(self, message):
        # ヘルプメッセージ
        HELP_MSG =['``` ### ダイスBotを利用する ###',
                   '$[整数]d[整数] ダイスを振った結果を表示する。',
                   '$s[整数]d[整数] ダイスを降った結果を昇順で表示する。期待値を表示する。',
                   '$calc(計算したい数式) 計算結果を表示する。',
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
    # 処理内容：ダイスを振る処理
    # 関数名　：dice_roll
    # 引数　　：self   / メソッドの仮引数
    #        : num   / ダイスを振る個数
    #        : sides / ダイスの面数
    # 戻り値　：なし
    ############################################################
    def dice_roll(self, num, sides):
        # ダイスを振った結果をrandintで生成し、
        # dice_aryリストにnum個追加する。
        for s in range(0, num):
            self.dice_ary.append(random.randint(1, sides))
        
        # ダイスを振った結果を文字列として生成
        self.dice_num = ','.join(map(str, self.dice_ary))
        
        # ダイスの出目をソート
        self.dice_ary.sort()
        
        # ダイスをソートした結果を文字列として生成
        self.dice_sort = ','.join(map(str, self.dice_ary))
        
        # 出目の合計を算出
        self.dice_total = str(sum(self.dice_ary))
        
        # 出目の平均を計算
        self.dice_mean = str(((sides + 1)) / 2 * num)

    ############################################################
    # 処理内容：ダイスを振り、振った順に結果を返却する処理
    # 関数名　：dice_roll_str
    # 引数　　：self   / メソッドの仮引数
    #        : num   / ダイスを振る個数
    #        : sides / ダイスの面数
    # 戻り値　：send_ms
    ############################################################
    def dice_roll_str(self, num, sides):
        # 変数初期化
        self.dice_param_init()
        
        # ダイスを振る
        self.dice_roll(num, sides)
        
        # 結果の文字列を返す
        send_ms = 'ころころ...' + '[' + self.dice_num + '] 合計:'+ self.dice_total
        return send_ms

    ############################################################
    # 処理内容：ダイスを振り、昇順にソートして結果を返却する処理
    # 関数名　：dice_roll_sort_str
    # 引数　　：self   / メソッドの仮引数
    #        : num   / ダイスを振る個数
    #        : sides / ダイスの面数
    # 戻り値　：send_ms
    ############################################################
    def dice_roll_sort_str(self, num, sides):
        # 変数初期化
        self.dice_param_init()

        # ダイスを振る
        self.dice_roll(num, sides)
        
        # 結果の文字列を返す
        send_ms = 'ころころ...' + '[' + self.dice_sort + '] 合計:'+ self.dice_total + ' 期待値:' + self.dice_mean
        return send_ms

    ############################################################
    # 処理内容：XdY+Zの結果を返却する
    # 関数名　：dice_roll_int
    # 引数　　：self          / メソッドの仮引数
    #        : num          / ダイスを振る個数
    #        : sides        / ダイスの面数
    #        : coefficient  / 補正値
    # 戻り値　：dice_result
    ############################################################
    def dice_roll_int(self, num, sides, coefficient):
        # ダイスの出目の結果を初期化
        dice_result = 0
        
        # XdYを振る
        for i in range(0, num):
            dice_result = dice_result + random.randint(1, sides)

        # 補正値を足す
        dice_result = dice_result + coefficient
        
        # 出目の結果を返す
        return dice_result

    ############################################################
    # 処理内容：D66の結果を返却する
    # 関数名　：dice_roll_D66
    # 引数　　：self          / メソッドの仮引数
    # 戻り値　：dice_result
    ############################################################
    def dice_roll_D66(self):
        #D66を振る
        dice_result = random.randint(1, 6) * 10 + random.randint(1, 6)
        
        # 出目の結果を返す
        return dice_result    
    
    ############################################################
    # 処理内容：計算処理
    # 関数名　：calulation
    # 引数　　：self   / メソッドの仮引数
    #        : com   / "calc(…)"という文字列
    # 戻り値　：send_ms
    ############################################################
    def calulation(self, com):
        
        ########################################################
        # 注意！注意！注意！！
        # evalをbotユーザが叩けることは、セキュリティ上非常に危険です！
        # 私の管理している鯖では許可していますが、
        # このコードを見た人は、本関数をオミットするのが無難です！
        ########################################################
        
        # 数式を取り出す
        formula = com.replace('$calc', '')

        # 数式の演算結果
        result = eval(formula)
        
        # 結果の文字列を返す
        send_ms = f"calc{formula} = {result}"
        return send_ms
