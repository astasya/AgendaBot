################################################################
#
# ファイル名：google_calendar.py
# 処理機能　：GoogleCalendar操作機能
#
################################################################

################################################################
#
# ライブラリのインポート
#
################################################################
# Python標準ライブラリ
import argparse     # コマンドライン解析モジュール
import datetime     # 時間を扱うモジュール
import json         # JSON形式ファイルを扱うライブラリ
import os.path      # パス名を扱うモジュール
import pickle       # オブジェクトを直列化・非直列化するモジュール
                    ## メモ : 2019/12/13
                    ## モジュールの詳細はよくわからないけど、
                    ## OAuth認可ファイル読込時に使うモジュールです。
import re           # 正規表現モジュール

# GoogleAPI のインポート
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
## メモ： バージョンは以下の通り
## google-api-python-client 1.7.8
## google-auth              1.6.3
## google-auth-httplib2     0.0.3
## google-auth-oauthlib     0.3.0

################################################################
#
# 入力するJSONファイルの内容
#
################################################################
#{
#  "google_calendar":[
#    {
#      "code":"Debug mode",                 # デバッグ環境の設定
#      "calendar_id":"---",                 # GoogleCalendarのID
#      "token_pickle_path":"./token.pickle" # GoogleOAuth認可ファイルのパス
#    },
#    {
#      "code":"Exe mode",                   # 本番環境の設定
#      "calendar_id":"---",                 # GoogleCalendarのID
#      "token_pickle_path":"./token.pickle" # GoogleOAuth認可ファイルのパス
#    }
#  ]
#}

################################################################
# 処理内容：変更する対象のカレンダーIDを取得
# 関数名　：get_google_calendar_id
# 引数　　：path        / jsonファイルのパス
# 戻り値　：calendar_id / 辞書型のGoogleCalendarのパラメータ
################################################################
def get_google_calendar_id(path):
    # パーサの作成
    parser = argparse.ArgumentParser()

    # パーサで扱う引数の設定
    # 今回は起動モードのフラグを扱う
    # 　--debug指定なし：true  / 本番環境
    # 　--debug指定あり：false / デバッグ環境
    parser.add_argument('--debug',
                        action = 'store_false',
                       )
    # 引数の解析を実行
    args = parser.parse_args()

    # ファイルオープン(utf8で読み込み専用)
    file = open(path, 'r', encoding = 'utf8')

    # JSONファイルの読み込み
    param_json = json.load(file)

    # ファイルクローズ
    file.close()

    # JSONファイルから取得したデータのうち
    # 扱うデータのIndexを指定
    index = 1 if args.debug else 0

    # GoogleCalendarのIDを取得
    calendar_id = param_json['google_calendar'][index]

    # 取得した情報を返却
    return calendar_id

################################################################
#
# GoogleCalendar
#
################################################################
class GoogleCalendar:
    
    ############################################################
    #
    # クラス変数
    #
    ############################################################
    # カレンダーへのRW権限(スコープ)を変更する
    # 変更する際はtoken.pickleを作成しなおすこと。
    __SCOPES = ['https://www.googleapis.com/auth/calendar']

    # GoogleCalendarIDとtoken.pickleファイルパスを
    # JSONファイルから情報を取得
    bot_options   = get_google_calendar_id('./google_calendar_id.json')

    # JSONファイルから取得した情報を各変数に格納
    __CARENDAR_ID  = bot_options["calendar_id"]       # 編集対象のGoogleCalendarのID
    __TOKEN_PICKLE = bot_options["token_pickle_path"] # OAuth認可ファイルのパス
    
    # 東京でのUTCとの誤差
    __ERR_UTC_TOKYO = 9

    # 時間の出力フォーマット
    __FORMAT_TIME = '%Y-%m-%dT%H:%M:%S%z'

    ############################################################
    # 処理内容：コンストラクタ
    # 関数名　：__init__
    # 引数　　：self / メソッドの仮引数
    ############################################################
    def __init__(self):
        pass

    ############################################################
    # 処理内容：GoogleCalendarとの接続
    # 関数名　：connect
    # 引数　　：self / メソッドの仮引数
    # 戻り値　：service / GoogleCalendarAPIとの接続用クラス
    ############################################################
    def connect(self):
        # token.pickleの読み込み
        # token.pickleの作成は以下のURL参照のこと
        # https://qiita.com/lobmto/items/c1a220a12ec9c1fad560 #
        with open(self.__TOKEN_PICKLE, 'rb') as token:
            creds = pickle.load(token)

        # カレンダーAPIとの接続
        service = build('calendar', 'v3', credentials = creds)

        return service

    ############################################################
    # 処理内容：GoogleCalendarのイベント削除
    # 関数名　：add_calendar_event
    # 引数　　：self / メソッドの仮引数
    #        : summary / イベントのタイトル
    #        : start_time / イベントの開始時刻
    #        : end_time / イベントの終了時刻
    # 戻り値　：なし
    # ##########################################################
    # # 入力する引数の例：
    # # add_calendar_event('test',
    # #                    '2019-05-11T21:00:00', 
    # #                    '2019-05-11T23:00:00')
    # ##########################################################
    ############################################################
    def add_calendar_event(self, summary, start_time, end_time):
        # APIとの接続
        service = self.connect()

        # カレンダ情報の格納
        body = {'summary': summary,
                'start': {  'dateTime': start_time,
                            'timeZone': 'Asia/Tokyo',
                         },
                'end':   {  'dateTime': end_time,
                            'timeZone': 'Asia/Tokyo',
                         },
                'attendees': '',
               }

        # カレンダへイベントの追加
        event = service.events().insert(calendarId = self.__CARENDAR_ID,
                                        body       = body
                                       ).execute()

    ############################################################
    # 処理内容：GoogleCalendarのイベント削除
    # 関数名　：del_calendar_event
    # 引数　　：self / メソッドの仮引数
    #        : summary / イベントのタイトル
    #        : start_time / イベントの開始時刻
    #        : end_time / イベントの終了時刻
    # 戻り値　：なし
    ############################################################
    def del_calendar_event(self, summary, start_time, end_time):
        # APIとの接続
        service = self.connect()

        # イベントIDの取得
        eventid = self.get_calendar_event(summary, start_time, end_time)

        # カレンダのイベントを削除
        service.events().delete(calendarId = self.__CARENDAR_ID,
                                eventId    = eventid
                               ).execute()

    ############################################################
    # 処理内容：GoogleCalendarのイベント取得
    # 関数名　：del_calendar_event
    # 引数　　：self / メソッドの仮引数
    #        : summary / イベントのタイトル
    #        : start_time / イベントの開始時刻
    #        : end_time / イベントの終了時刻
    # 戻り値　：イベントID
    # ##########################################################
    # # 入力する引数の例：
    # # del_calendar_event('test',
    # #                    '2019-05-11T21:00:00+09:00', 
    # #                    '2019-05-11T23:00:00+09:00')
    # ##########################################################
    ############################################################
    def get_calendar_event(self, summary, start_time, end_time):
        # APIとの接続
        service = self.connect()
        
        # イベントID
        eventid = 0

        # カレンダーの取得
        events = service.events().list(
            calendarId   = self.__CARENDAR_ID, # 検索するGoogleCalendarのID
            timeMin      = start_time,         # 検索するイベントの開始時刻
            timeMax      = end_time,           # 検索するイベントの終了時刻
            singleEvents = True                # Falseだと削除したイベントまで検索対象？
        ).execute()

        # 日付データ文字(引数)を置換
        startTime = datetime.datetime.strptime(start_time,
                                               self.__FORMAT_TIME
                                              )
        endTime = datetime.datetime.strptime(end_time,
                                             self.__FORMAT_TIME
                                            )

        # イベントの検索
        for event in events['items']:
            start = event['start']
            end   = event['end']

            # 日付と卓名が一致するイベントを検索
            if event['summary'] == summary \
            and datetime.datetime.strptime(start['dateTime'],self.__FORMAT_TIME) == startTime \
            and datetime.datetime.strptime(end['dateTime'],self.__FORMAT_TIME) == endTime:
                
                # eventidを取得
                eventid = event['id']

        # eventidを返す
        return eventid
