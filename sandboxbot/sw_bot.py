################################################################
#
# ファイル名：sw_bot.py
# 処理機能　：SW2.0/2.5 キャラクター作成支援機能
#
################################################################

################################################################
#
# ライブラリのインポート
#
################################################################
# Python標準ライブラリ
import random               # 乱数生成モジュール
import re                   # 正規表現モジュール

# 有志制作のライブラリ
import discord              # discord用APIラッパー   ver1.0.1

# 自作モジュール
from . import randam_table  # ランダム表を振るモジュール
from . import dice_bot      # ダイスを振るモジュール

################################################################
#
# SwBot
#
################################################################
class SwBot:
    def __init__(self):#インスタンス変数管理
        # randam_table.py
        self.__randam_table = randam_table.RandamTable()
        # dicebot.py
        self.__dicebot = dice_bot.DiceBot()

    ############################################################
    #
    # クラス変数
    #
    ############################################################
    # ステータスラベル
    __STAT_LABEL = ['器用：','敏捷：','筋力：','生命：','知力：','精神：']

    
    ### 定数指定
    # キャラ作成モード
    __STATUS_ONLY = 0
    __ALL_MAKING  = 1
    
    ### 各種表のファイルパス
    # 種族表のファイルパス
    __FILEPATH_RACE = "./randam_table/sw2.5/sw2.5_race.csv"
    # 経歴表のファイルパス
    __FILEPATH_CAREER = "./randam_table/sw2.5/sw2.5_career.csv"
    # 冒険にでた理由表のファイルパス
    __FILEPATH_REASON = "./randam_table/sw2.5/sw2.5_reason.csv"
    # アビスカース表のファイルパス
    __FILEPATH_ABYSS = "./randam_table/sw2.5/sw2.5_abyss.csv"

    # ランダム表を振るモード指定
    __CAREER_TABLE = 0
    __REASON_TABLE = 1
    __ABYSS_TABLE = 2
    
    ############################################################
    # 処理内容：message投稿時
    # 関数名　：sw_on_message
    # 引数　　：self        / メソッドの仮引数
    #        : message    / message構造体
    # 戻り値　：なし
    ############################################################
    async def sw_on_message(self, message):

        if isinstance(message.channel, discord.DMChannel):
            # botへのDM送信時、処理を終了する
            return

        # SWヘルプコマンド
        if re.match('\$sw_help', message.content):
            await self.sw_help(message)

        # 初期キャラ作成
        elif re.match('\$sw_\d+', message.content):
            await self.generate_stat_message(message,
                                             self.__ALL_MAKING
                                            )

        # 種族値生成
        elif re.match('\$sw_race_\d+', message.content):
            await self.generate_stat_message(message,
                                             self.__STATUS_ONLY
                                            )
        
        # 生まれ
        elif re.match('\$sw_ca\d*', message.content):
            await self.generate_sw25_randamtable_message(message,
                                                         self.__CAREER_TABLE
                                                        )
        
        # 冒険にでた理由
        elif re.match('\$sw_re\d*', message.content):
            await self.generate_sw25_randamtable_message(message,
                                                         self.__REASON_TABLE
                                                        )
        
        # アビスカース
        elif re.match('\$sw_ab\d*', message.content):
            await self.generate_sw25_randamtable_message(message,
                                                         self.__ABYSS_TABLE
                                                        )
            
    ############################################################
    # 処理内容：help表示
    # 関数名　：sw_help
    # 引数　　：self     / メソッドの仮引数
    #        : message / メッセージ構造体
    # 戻り値　：なし
    ############################################################
    async def sw_help(self, message):
        # ヘルプメッセージ
        HELP_MSG =['``` ### SWを遊ぶ ###',
                   '$sw_[整数] 各種族のキャラクターの初期作成を行います。',
                   '  人間：0,エルフ：1,ドワーフ：2,タビット：3',
                   '  ルーンフォーク：4,ナイトメア：5,リカント：6,',
                   '  リルドラケン：7,グラスランナー：8,メリア：9,',
                   '  ティエンス：10,レプラカーン：11',
                   '$sw_race_[整数] 各種族の初期ステータスを3回生成します。',
                   '  人間：0,エルフ：1,ドワーフ：2,タビット：3',
                   '  ルーンフォーク：4,ナイトメア：5,リカント：6,',
                   '  リルドラケン：7,グラスランナー：8,メリア：9,',
                   '  ティエンス：10,レプラカーン：11',
                   '$sw_ab[無しor整数] アビス強化表を振った結果を表示する。',
                   '$sw_ca[無しor整数] 整数の数だけ経歴表を振り、結果を表示する。',
                   '$sw_re[無しor整数] 冒険に出た理由表を振った結果を表示する。',
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
    # 処理内容：キャラクターの初期ステータスを3回生成する
    # 関数名　：generate_stat_message
    # 引数　　：self     / メソッドの仮引数
    #     　　：message / メッセージ構造体
    #     　　：flag    / 出力内容決定フラグ
    #                     0 : ステータスのみを出力
    #                     1 : 全データを出力
    # 戻り値　：なし
    ############################################################
    async def generate_stat_message(self, message, flag):
        # コマンドから種族番号を取得する
        race_cmd = re.findall('\d+', message.content)
        
        if race_cmd == []:
            # 種族番号取得失敗時
            send_ms = '\$helpを参照し、正しい数値を入力してください'

        else:
            # 初期ステータスの生成結果を取得
            result = self.roll_stat(int(race_cmd[0]))
        
            # 取得に失敗したとき
            if result == bool(False):
                # エラーメッセージを返却
                send_ms = '\$helpを参照し、正しい数値を入力してください'
        
            else:
                # ステータスの生成結果を返却する変数に格納
                send_ms = result
                
                # 全データ出力モードの場合、経歴表と冒険にでた理由表も振る
                if flag == self.__ALL_MAKING:
                    
                    # 経歴表を振る
                    temp = self.roll_career(3)
                    
                    if temp == bool(False):
                        send_ms = '経歴表の取得に失敗しました。'
                    else:
                        send_ms += '\r\n' + temp
                    
                    # 冒険にでた理由表を振る
                    temp = self.roll_reason(1)
                    if temp == bool(False):
                        send_ms = '理由表の取得に失敗しました。'
                    else:
                        send_ms += '\r\n' + temp

        # 実行結果をテキストチャンネルに送信
        await message.channel.send(send_ms)

    ############################################################
    # 処理内容：SW2.5のランダム表をふる
    # 関数名　：generate_sw25_randamtable_message
    # 引数　　：self     / メソッドの仮引数
    #     　　：message / メッセージ構造体
    #     　　：table   / 振る表の指定
    #                     self.__CAREER_TABLE:経歴表
    #                     self.__REASON_TABLE:冒険にでた理由表
    #                     self.__ABYSS_TABLE :アビス表
    # 戻り値　：なし
    ############################################################
    async def generate_sw25_randamtable_message(self, message, table):
        # コマンドからランダム表を振る回数を取得する
        table_cmd = re.findall('\d+', message.content)

        if table_cmd == []:
            # コマンドに数字が付与されてない場合、1回振る
            table_num = 1
        else:
            # コマンドに付与されている数字を変数に格納
            table_num = int(table_cmd[0])
            
        if table_num < 0:
            # エラーメッセージを出力
            send_ms = '1回以上の回数を指定してください。'
            
        else:
            # 出力メッセージの生成
            if table == self.__CAREER_TABLE:
                # 経歴表を振る
                send_ms = self.roll_career(table_num)
                
            if table == self.__REASON_TABLE:
                # 理由表を振る
                send_ms = self.roll_reason(table_num)
                
            if table == self.__ABYSS_TABLE:
                # アビスカース表を振る
                send_ms = self.roll_abyss(table_num)
            
            if send_ms == bool(False):
                send_ms = 'ランダム表の取得に失敗しました。'
        
        # 実行結果をテキストチャンネルに送信
        await message.channel.send(send_ms)

    ############################################################
    # 処理内容：キャラクターの初期ステータスを3回生成する
    # 関数名　：roll_stat
    # 引数　　：self      / メソッドの仮引数
    #     　　：race_num / 種族番号
    # 戻り値　：なし
    ############################################################
    def roll_stat(self, race_num):
        # 種族表から値を取得
        line = self.__randam_table.result_randam_table(self.__FILEPATH_RACE, race_num)
        
        # 行を読み込めなかったとき
        if line == bool(False):
            # Falseを返す
            return bool(False)
        
        # ステータス格納用配列の初期化
        stat_tmpary = []

        # 3回ステータスを生成
        for i in range(3):
            # ダイスを振る
            for j in range(6):
                # csvから取得したダイス数、補正値を変数にセット
                num         = int( line[j + 1] )
                sides       = 6
                coefficient = int( line[j + 1 + 6] )
                
                # ダイスを振る
                stat_result = self.__dicebot.dice_roll_int(num, sides, coefficient)
                
                # ステータスの出力メッセージを生成
                stat_tmp = str(self.__STAT_LABEL[j]) + str(stat_result)
                if j != 0:
                    # カンマ区切りを追加
                    stat_tmp = ',' + stat_tmp
                
                # ダイスを振った結果をstat_tmparyに追加
                stat_tmpary.append(stat_tmp)
            
        # 出力メッセージを初期化
        send_ms = ''
                
        # 種族名を出力メッセージに追加
        send_ms = '種族：' + line[0] + '\r\n'
        
        # ステータスの生成結果を出力メッセージに追加
        for i in range(3):
            for j in range(6):
                send_ms += stat_tmpary[i * 6 + j]
            send_ms += '\r\n'

        # 実行結果をテキストチャンネルに送信
        return send_ms
    
    ############################################################
    # 処理内容：経歴表を振る
    # 関数名　：roll_career
    # 引数　　：self        / メソッドの仮引数
    #     　　：career_num / ダイスを振る回数
    # 戻り値　：なし
    ############################################################
    def roll_career(self, career_num):
        # 経歴表の結果を一時保存する変数を初期化
        temp = ''
        
        for i in range(career_num):
            # csvファイルの参照する行数をランダムに生成
            row = random.randint(0,107)

            # 経歴表から値を取得
            line = self.__randam_table.result_randam_table(self.__FILEPATH_CAREER, row)

            # 行を読み込めなかったとき
            if line == bool(False):
                # Falseを返す
                return bool(False)

            # 経歴表の結果を格納
            career_name   = '**「' + line[2] + '」**'
            career_table  = '(経歴表' + line[0]  + ' ダイス目[' + line[1] + '] )\r\n'

            temp = temp + career_name + career_table
            
        # 出力メッセージの生成
        send_ms = 'あなたの経歴は…\r\n' + temp
        
        # 実行結果をテキストチャンネルに送信
        return send_ms

    ############################################################
    # 処理内容：理由表を振る
    # 関数名　：roll_reason
    # 引数　　：self        / メソッドの仮引数
    #     　　：reason_num / ダイスを振る回数
    # 戻り値　：なし
    ############################################################
    def roll_reason(self, reason_num):
        # 理由表の結果を一時保存する変数を初期化
        temp = ''
        
        for i in range(reason_num):
            # csvファイルの参照する行数をランダムに生成
            row = random.randint(0,35)

            # 理由表から値を取得
            line = self.__randam_table.result_randam_table(self.__FILEPATH_REASON, row)
            
            # 行を読み込めなかったとき
            if line == bool(False):
                # Falseを返す
                return bool(False)

            # 理由表の結果を格納
            reason = '**「' + line[1] + '」**'
            dice   = '(ダイス目[' + line[0] + '] )\r\n'

            temp = temp + reason + dice

        # 出力メッセージの生成
        send_ms = 'あなたはこんな理由で冒険に出ました\r\n' + temp

        # 実行結果をテキストチャンネルに送信
        return send_ms
    
    ############################################################
    # 処理内容：アビスカース表をふる
    # 関数名　：roll_abyss
    # 引数　　：self       / メソッドの仮引数
    #     　　：abyss_num / ダイスを振る回数
    # 戻り値　：なし
    ############################################################
    def roll_abyss(self, abyss_num):
        # 出力メッセージの初期化
        send_ms = ''
        
        for i in range(abyss_num):
            # csvファイルの参照する行数をランダムに生成
            row = random.randint(0,35)

            # アビスカース表から値を取得
            line = self.__randam_table.result_randam_table(self.__FILEPATH_ABYSS, row)

            # 行を読み込めなかったとき
            if line == bool(False):
                # Falseを返す
                return bool(False)

            # アビスカース表の結果を格納
            abyss_dice   = 'アビス強化ダイス:[' + line[0] + ']\r\n'
            abyss_name   = 'アビスカース名称>' + line[1] +'\r\n'
            abyss_timing = 'タイミング>' + line[2] + '\r\n'
            abyss_effect = '効果>' + line[3] + '\r\n'

            # 出力メッセージに結果を格納
            send_ms = send_ms + abyss_dice + abyss_name + abyss_timing + abyss_effect + '\r\n'
        
        # 実行結果をテキストチャンネルに送信
        return send_ms

