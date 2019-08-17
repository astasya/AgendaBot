################################################################
#
# ファイル名：access_log.py
# 処理機能　：アクセスログ解析機能
#
################################################################

################################################################
#
# ライブラリのインポート
#
################################################################
# Python標準ライブラリ
import datetime             # 時間を扱うモジュール
import os                   # ファイルを扱うモジュール  
import re                   # 正規表現モジュール  
import sqlite3              # DBを扱うモジュール

# 有志制作のライブラリ
import discord              # discord用APIラッパー   ver1.0.1

################################################################
#
# 定数
#
################################################################
# DBのファイル名
DB_MES_FILEPATH = './mes.db'
DB_VC_FILEPATH  = './vc.db'

################################################################
#
# Alog
#
################################################################
class Alog:
    
    ############################################################
    # 処理内容：コンストラクタ
    # 関数名　：__init__
    # 引数　　：self     / メソッドの仮引数
    # 　　　　：vc_list  / 現在のVC接続者のリスト
    # 戻り値　：なし
    ############################################################
    def __init__(self):
        # DB生成処理
        self.create_db_for_mes()
        self.create_db_for_vc()

        # DBのConnection/Cursorオブジェクト
        self.mes_con = None
        self.mes_cur = None
        self.vc_con  = None
        self.vc_cur  = None
    
    ############################################################
    # 処理内容：VC接続時間管理用DB テスト出力
    # 関数名　：test_for_mes
    # 引数　　：self        / メソッドの仮引数
    # 戻り値　：なし
    ############################################################
    async def test_for_mes(self):
        query = 'SELECT * FROM mes'
        for row in self.mes_cur.execute(query):
            print(row)    
            
    ############################################################
    # 処理内容：VC接続時間管理用DB テスト出力
    # 関数名　：test_for_vc
    # 引数　　：self        / メソッドの仮引数
    # 戻り値　：なし
    ############################################################
    async def test_for_vc(self):
        query = 'SELECT * FROM vc'
        for row in self.vc_cur.execute(query):
            print(row)
        
    
    ############################################################
    # 処理内容：起動時処理
    # 関数名　：alog_on_ready
    # 引数　　：self   / メソッドの仮引数
    # 　　　　：guild  / guildクラス
    # 戻り値　：なし
    ############################################################
    async def alog_on_ready(self, guild):
        # connect_usersの初期化
        connect_users = []
        
        # AFK以外のVCチャンネルを取得
        vc_ch_list = guild.voice_channels
        for vc_ch in guild.voice_channels:
            if str(vc_ch.name) != str(guild.afk_channel):
                # AFKチャンネル以外の各VCチャンネルの接続者を取得
                members = vc_ch.members
                for member in members:
                    user = [member.id, vc_ch.id]
                    connect_users.append(user)
                
        # DBのConnection/Cursorオブジェクトの作成
        self.mes_con = sqlite3.connect(DB_MES_FILEPATH)
        self.mes_cur = self.mes_con.cursor()
        self.vc_con  = sqlite3.connect(DB_VC_FILEPATH)
        self.vc_cur  = self.vc_con.cursor()

        # Bot強制終了時用措置
        self.reboot_bot(connect_users)    
        
    ############################################################
    # 処理内容：message投稿時
    # 関数名　：alog_on_message
    # 引数　　：self        / メソッドの仮引数
    # 　　　　：message     / メッセージクラス
    # 　　　　：ROLE_SUBMIT / DBを閲覧可能な役職のリスト
    # 戻り値　：なし
    ############################################################
    async def alog_on_message(self, message, ROLE_SUBMIT):
        
        if isinstance(message.channel, discord.DMChannel):
            # botへのDM送信時、処理を終了する
            return

        # 投稿回数カウント
        self.insert_db_for_mes(message.author.id,
                               message.channel.id)
        # ヘルプコマンド
        if re.match('\$alog_help', message.content):
            await self.alog_help(message)
        
        # DB取得コマンド
        if re.match('\$alog_download', message.content):
            await self.alog_db_download(message, ROLE_SUBMIT)

    ############################################################
    # 処理内容：help表示
    # 関数名　：alog_help
    # 引数　　：self     / メソッドの仮引数
    #        : message / メッセージ構造体
    # 戻り値　：なし
    ############################################################
    async def alog_help(self, message):
        # ヘルプメッセージ
        HELP_MSG =['``` ### Sandbox鯖 アクセスログ解析機能 ###',
                   '$alog_download Textチャンネル及びVCチャンネルへの全アクセスログを取得する。(鯖管理者専用)',
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
    # 処理内容：DBダウンロード処理
    # 関数名　：alog_db_download
    # 引数　　：self        / メソッドの仮引数
    # 　　　　：message     / メッセージクラス
    # 　　　　：ROLE_SUBMIT / DBを閲覧可能な役職のリスト
    # 戻り値　：なし
    ############################################################
    async def alog_db_download(self, message, ROLE_SUBMIT):
        # ダウンロード実行フラグの初期化
        download_flag = False
            
        # 発言者の役職のチェック
        for submit_role_id in ROLE_SUBMIT:
            for author_role in message.guild.roles:
                if submit_role_id == int(author_role.id):
                    download_flag = True
        
        if download_flag == False:
            "この機能はあなたのクリアランスには許可されていません。"
            return

        # dmにてDBを送信
        dm = await message.author.create_dm()

        await dm.send('MESSAGE投稿管理用DB',
                      file=discord.File(DB_MES_FILEPATH)
                     )
        await dm.send('VC接続時間管理用DB',
                      file=discord.File(DB_VC_FILEPATH)
                     )        
                    
    ############################################################
    # 処理内容：VoiceChatIN/OUT時の処理
    # 関数名　：on_voice_state_update
    # 引数　　：self             / メンバーオブジェクト
    # 　　　　：member           / メンバーオブジェクト
    # 　　　　：before           / Channelオブジェクト
    # 　　　　：after            / Channelオブジェクト
    # 　　　　：AFK_CHANNEL_ID   / AFKチャンネル
    # 戻り値　：なし
    ############################################################    
    async def on_voice_state_update(self,member, before, after, AFK_CHANNEL_ID):
        # 現在時刻の取得
        JST = datetime.timezone(datetime.timedelta(hours=+9), 'JST')
        time = datetime.datetime.now(JST)

        # user_idの取得
        user_id = member.id
        
        in_ch_id  = None
        out_ch_id = None
        
        # VCチャンネルに接続したとき
        if before.channel == None:
            in_ch_id = after.channel.id
        
        # VCチャンネルから切断したとき
        elif after.channel == None:
            out_ch_id = before.channel.id
        
        # VCチャンネルを移動したとき
        else:
            in_ch_id = after.channel.id
            out_ch_id = before.channel.id
        
        if out_ch_id != None and out_ch_id != AFK_CHANNEL_ID:
            # レコード終了処理
            self.update_db_for_vc(user_id, time)
        if in_ch_id  != None and in_ch_id != AFK_CHANNEL_ID:
            # レコード追加処理
            self.insert_db_for_vc(user_id, in_ch_id, time)
            
    ############################################################
    # 処理内容：現在時刻取得処理
    # 関数名　：now_time
    # 引数　　：self         / メソッドの仮引数
    # 戻り値　：現在時刻(JST)
    ############################################################
    def generate_now_time(self):
        # 現在時刻の取得
        JST = datetime.timezone(datetime.timedelta(hours=+9), 'JST')
        time = datetime.datetime.now(JST)
        return time
        
    ############################################################
    # 処理内容：MESSAGE投稿数管理用DB 生成処理
    # 関数名　：create_db_for_mes
    # 引数　　：self / メソッドの仮引数
    # 戻り値　：なし
    ############################################################
    def create_db_for_mes(self):
        if os.path.exists(DB_MES_FILEPATH) == True:
            # DBファイルがある場合処理終了
            return

        self.mes_con = sqlite3.connect(DB_MES_FILEPATH)
        self.mes_cur = self.mes_con.cursor()

        # テーブルの作成
        self.mes_cur.execute('CREATE TABLE mes(user_id integer, channel_id integer, time datetime)')
            ## メモ : テーブルの作成は以下のSQL文を用いる
            ##          CREATE TABLE テーブル名(要素1、要素2…)
            ##
            ##      　ここで要素は以下のように記述する
            ##          要素名 データ型
            ##              ※ 型指定なしでもできるが、やらないよう統一すること!

        # DBへの反映
        self.mes_con.commit()

    ############################################################
    # 処理内容：VC接続時間管理用DB 生成処理
    # 関数名　：create_db_for_vc
    # 引数　　：self / メソッドの仮引数
    # 戻り値　：なし
    ############################################################
    def create_db_for_vc(self):
        if os.path.exists(DB_VC_FILEPATH) == True:
            # DBファイルがある場合処理終了
            return

        self.vc_con  = sqlite3.connect(DB_VC_FILEPATH)
        self.vc_cur  = self.vc_con.cursor()

        # テーブルの作成
        self.vc_cur.execute('CREATE TABLE vc(user_id integer, channel_id integer, connecting boolean, start_time datetime, end_time datetime)')

        # DBへの反映
        self.vc_con.commit()
        
    ############################################################
    # 処理内容：VC接続時間管理用DB BOT起動時処理
    # 関数名　：reboot_bot
    # 引数　　：self           / メソッドの仮引数
    # 　　　　：connect_users  / 現在のVC接続者のリスト(user_idとCH_id)
    # 戻り値　：なし
    ############################################################
    def reboot_bot(self, connect_users):
        # 現在時刻の取得
        time = self.generate_now_time()

        # 設定する値をタプルにする
        settings = tuple([False, time, True])
        
        # Bot強制終了時のVC接続者はBot再起動時まで接続していたとみなし、
        # VC接続時間がありVC切断時間がNULLのレコードに現在時刻を格納する
        
        # データの編集
        self.vc_cur.execute('UPDATE vc SET connecting = (?), end_time = (?) WHERE connecting = (?)', settings)

        # DBへの反映
        self.vc_con.commit()
        
        # 現在のVC接続者を現在時刻から接続しているとしてDBに追加
        for connect_users in connect_users:
            # 接続者の情報を追加
            self.insert_db_for_vc(connect_users[0],
                                  connect_users[1],
                                  time)
    
    ############################################################
    # 処理内容：MESSAGE投稿数管理用DB データ追加処理
    # 関数名　：insert_db_for_mes
    # 引数　　：self         / メソッドの仮引数
    # 　　　　：user_id      / ユーザID
    # 　　　　：ch_id        / CHID
    # 戻り値　：なし
    ############################################################
    def insert_db_for_mes(self, user_id, ch_id):
        # 現在時刻の取得
        time = self.generate_now_time()

        # 追加するデータの設定
        rows = tuple([user_id, ch_id, time])
        
        # データの追加
        self.mes_cur.execute('INSERT INTO mes VALUES(?,?,?)',rows)
            ## メモ : データの追加は以下のように記述する
            ##          INSERT INFO テーブル名 VALUES(値)
            ##
            ##     　 なおVALUES(1,2...)のように直接値を記述することも可能
            ##
            ##      　今回は変数を渡したいため、?を用いて引数から値を取得している
            ##      　このとき、?はテーブルの要素数(列数)と等しいことに注意。
            ##      　読み込ませるデータ数ではない。

        # DBへの反映
        self.mes_con.commit()
        
    ############################################################
    # 処理内容：VC接続時間数管理用DB VC接続開始処理
    # 関数名　：insert_db_for_vc
    # 引数　　：self         / メソッドの仮引数
    # 　　　　：user_id      / ユーザID
    # 　　　　：ch_id        / CHID
    # 　　　　：start_time   / 接続開始時刻
    # 戻り値　：なし
    ############################################################
    def insert_db_for_vc(self,
                         user_id,
                         ch_id,
                         start_time):
        rows = tuple([user_id, ch_id, True, start_time, None])
        # データの追加
        self.vc_cur.execute('INSERT INTO vc VALUES(?,?,?,?,?)',rows)

        # DBへの反映
        self.vc_con.commit()
        
    ############################################################
    # 処理内容：VC接続時間数管理用DB 接続終了処理
    # 関数名　：update_db_for_vc
    # 引数　　：self       / メソッドの仮引数
    # 　　　　：user_id    / ユーザID
    # 　　　　：end_time   / 接続終了時刻
    # 戻り値　：なし
    ############################################################
    def update_db_for_vc(self,
                         user_id,
                         end_time):
        # 設定する値をタプルにする
        settings = tuple([False, end_time, user_id, True])
        
        # データの編集
        self.vc_cur.execute('UPDATE vc SET connecting = (?), end_time = (?) WHERE user_id = (?) AND connecting = (?)', settings)

        # DBへの反映
        self.vc_con.commit()

    # 以下実装しようと思ったけど、実装したら個人情報にだれでもアクセスできることに気づいたので
    # 実装をやめた検索処理。管理者以上のみ活用できるようにローカルで実行可能にする予定。
    ############################################################
    # 処理内容：MESSAGE投稿数管理用DB 検索処理
    # 関数名　：select_db_for_mes
    # 引数　　：self        / メソッドの仮引数
    # 　　　　：user_id     / ユーザID
    # 　　　　：start_time  / 検索開始時刻
    # 　　　　：end_time    / 検索終了時刻
    # 戻り値　：なし
    ############################################################
    def select_db_for_mes(self,
                          user_id    : int = None,
                          ch_id      : int = None,
                          start_time : str = None,
                          end_time   : str = None) -> list:
        ## メモ : キーワード引数
        ##  ret = select_db_for_mes (user_id    = spam,
        ##                           start_time = ham,)
        ##  のように関数をCallする。指定のパラメータが無ければNoneが入る。

        ## メモ : type hinting
        ##  user_id = None : str
        ##      引数user_idがstr型であることを意味する。
        ##  def spam () -> list:
        ##      関数の戻り値がlist型であることを意味する。

        # SQL文
        query = 'SELECT * FROM mes'

        # SQL文に渡す変数のタプル
        columns = (user_id, start_time, end_time)
        criteria = tuple(c for c in columns if c)
            ## メモ：リスト内包表記
            ##  通常のループの例
            ##      for i in range(spam):
            ##          ham.append(i)
            ##  内包表記の例
            ##      ham = [i for i in range(spam)]

            ## メモ : 後置if
            ##  例：偶数のみリストに追加
            ##      ham = [i for i in range(spam) if (i % 2 == 0)]

            ## メモ : ジェネレータ式
            ##  ()で表す、()の実行を関数として実行し戻り値を得るイメージ？
            ##  今回だと、内包表記で得られたcのリストをジェネレータ式で得て、
            ##  その戻り値をtuple型にキャストしている
            ##  だから、イミュータブルなtuple型をなんかいい感じに値追加できてる。

        conditions = [] # SQLの条件式を初期化

        if user_id:
            conditions.append('user_id = (?)')
        if ch_id:
            conditions.append('channel_id = (?)')
        if start_time:
            if end_time:
                conditions.append('time BETWEEN datetime(?) AND datetime(?)')
            else:
                # start_timeが引数として渡されているとき、条件式を追加する
                conditions.append('time > datetime(?)')

        conditions = ' AND '.join(conditions)
        ## メモ : String.join(list)
        ##  '間に挿入する文字列'.join([連結したい文字列のリスト])

        # SQL文を条件式と結合
        query = f'{query} WHERE {conditions}'

        # SQLの検索結果をListとして戻す
        return [row for row in self.mes_cur.execute(query, criteria)]

    ############################################################
    # 処理内容：VC接続時間管理用DB 検索処理
    # 関数名　：select_db_for_vc
    # 引数　　：self        / メソッドの仮引数
    # 　　　　：user_id     / ユーザID
    # 　　　　：start_time  / 検索開始時刻
    # 　　　　：end_time    / 検索終了時刻
    # 戻り値　：なし
    ############################################################
    def select_db_for_vc(self,
                         user_id    = None,
                         ch_id      = None,
                         start_time = None,
                         end_time   = None):

        ### Nullに値を格納する処理
        # 現在時刻の取得
        time = self.generate_now_time()

        # 設定する値をタプルにする
        settings = tuple([time, True])
        
        # 接続中のユーザの終了時間を暫定的に現在値（検索実行時)に修正
        self.vc_cur.execute('UPDATE vc SET end_time = (?) WHERE connecting = (?)', settings)

        # DBへの反映
        self.vc_con.commit()
        
        ### 検索処理
        query = 'SELECT * FROM vc'

        # SQL文に渡す変数のタプル
        columns = []

        conditions = [] # SQLの条件式を初期化

        if user_id:
            conditions.append('user_id = (?)')
            columns.append(user_id)
        if ch_id:
            conditions.append('channel_id = (?)')
            columns.append(ch_id)
        if start_time:
            if end_time:
                conditions.append('NOT start_time < datetime(?) AND NOT end_time < datetime(?) AND NOT start_time > datetime(?) AND NOT end_time > datetime(?)')
                columns += [start_time, start_time, end_time, end_time]
            else:
                # start_timeが引数として渡されているとき、条件式を追加する
                conditions.append('NOT start_time < datetime(?) AND NOT end_time < datetime(?)')
                columns += [start_time, start_time]

        criteria = tuple(c for c in columns)

        conditions = ' AND '.join(conditions)

        # SQL文を条件式と結合
        query = f'{query} WHERE {conditions}'

        print(query)
        print(criteria)
        
        # SQLの検索結果をListとして戻す
        return [row for row in self.vc_cur.execute(query, criteria)]

