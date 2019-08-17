################################################################
#
# ファイル名：agenda_control.py
# 処理機能　：TRPGセッション管理機能
# 処理概要　：
#   1.  #Agendaへ投稿されたTRPGセッションの予定をGoogleCalendarに転記し
#       投稿文をピン留めする。
#   2.  #Agendaへ投稿されたTRPGセッションの予定が不正形式の場合は
#       投稿文を削除する
#   3.  #Agendaへ投稿されたTRPGセッションの予定が編集/削除されたとき
#       GoogleCalendarを更新する
#   4.  TRPGセッションの予定一覧を#雑談(CH_GENERAL)に送信する
#
################################################################

################################################################
#
# ライブラリのインポート
#
################################################################
# Python標準ライブラリ
import asyncio                  # 非同期処理フレームワーク
import datetime                 # 時間を扱うモジュール
import re                       # 正規表現モジュール
import time                     # 時間を扱うモジュール
                                    ## メモ:2019/07/01
                                    ## 時間を扱う際はdatetimeモジュールを使う方が一般的らしい
                                    ## datetimeモジュール利用方式に変えた方が無難?

# 有志作成のライブラリ
import discord                  # discord用APIラッパー   ver1.0.1

# 自作ライブラリ
from .google_calendar import *  # GoogleCalendarを操作する
calendar = GoogleCalendar()     # calendarインスタンスの生成

################################################################
#
# AgendaControl
#
################################################################
class AgendaControl:
    
    ############################################################
    # 処理内容：コンストラクタ
    # 関数名　：__init__
    # 引数　　：self / メソッドの仮引数
    # 戻り値　：なし
    ############################################################
    def __init__(self):
        # Agenda構造体
        self.__agenda_dict = {
            "種別" : None ,
            "開始日時" : None,
            "終了日時" : None,
            "システム" : None,
            "シナリオ名" : None,
            "ツール" : None,
            "募集人数" : None,
            "概要" : None,
        }

        # GoogleCalendarイベント名構造体
        self.__calendar_dict = {
            "件名" : None,
            "開始日時" : None,
            "終了日時" : None,
        }
        
        # セッション一覧
        self.__single_session_list = []
        self.__campain_session_list = []
        self.__allways_session_list = []

        # 卓種別
        self.__SESSION_SINGLE = 0
        self.__SESSION_CAMPAIN = 1
        self.__SESSION_ALLWAYS = 2
        self.__SESSION_NONE = (-1)

        # 関数動作分岐定義定数
        ## Agenda登録/削除モード
        self.__SESSION_ADD_MODE = 0
        self.__SESSION_DEL_MODE = 1

        ## Agenda投稿エラーモード
        self.__AGENDA_FORMAT_ADD_ERROR = 0   # 投稿文不正形式
        self.__AGENDA_FORMAT_EDIT_ERROR = 1   # 編集文不正形式
        self.__AGENDA_CALENDAR_ADD_ERROR = 2 # カレンダー追加失敗
        self.__AGENDA_CALENDAR_DEL_ERROR = 3 # カレンダー削除失敗

        ## セッション参加申請/辞退モード
        self.__ATTENDANCE_ENTORY_MODE = 0
        self.__ATTENDANCE_DECLINE_MODE = 1

    ############################################################
    # 処理内容：クラス変数の初期化
    # 関数名　：agenda_param_init
    # 引数　　：self / メソッドの仮引数
    # 戻り値　：なし
    ############################################################
    def agenda_param_init(self):
        # Agenda構造体の初期化
        self.__agenda_dict["種別"] = None
        self.__agenda_dict["開始日時"] = None
        self.__agenda_dict["終了日時"] = None
        self.__agenda_dict["システム"] = None
        self.__agenda_dict["シナリオ名"] = None
        self.__agenda_dict["ツール"] = None
        self.__agenda_dict["募集人数"] = None
        self.__agenda_dict["概要"] = None

        # GoogleCalendarイベント名構造体
        self.__calendar_dict["件名"] = None
        self.__calendar_dict["開始日時"] = None
        self.__calendar_dict["終了日時"] = None
        
        return

    ############################################################
    #
    # Discordで発生するイベントに対するコールバック処理
    #
    ############################################################
    
    ############################################################
    # 処理内容：message投稿時
    # 関数名　：agenda_on_message
    # 引数　　：self        / メソッドの仮引数
    #        : SERVER_ID  / 鯖ID
    #        : message    / message構造体
    #        : CH_AGENDA  / #agenda channel()
    #        : CH_GENERAL / #雑談 channel()
    # 戻り値　：なし
    ############################################################
    async def agenda_on_message(self,
                                SERVER_ID,
                                message,
                                CH_AGENDA,
                                CH_GENERAL
                               ):

        if isinstance(message.channel, discord.DMChannel):
            # botへのDM送信時、処理を終了する
            return
        
        if re.match('\$list', message.content):
            # 卓一覧出力処理
            await self.session_list_mes_send(SERVER_ID,
                                             CH_AGENDA,
                                             CH_GENERAL
                                            )

        # @everyoneからメッセージが始まるとき
        if re.match('\@everyone', message.content):
            if not message.channel == CH_AGENDA:
                # 投稿先がCH_AGENDAでなければ処理終了
                print("test2")
                return

            # 変数初期化
            self.agenda_param_init()

            # Agenda登録処理
            nRet = await self.agenda_add_sub(message)

            if nRet == bool(False):
                # Agenda登録処理失敗時、投稿文を削除する
                await message.delete()
            else:
                # Agenda登録処理成功時、登録メッセージをピンどめする
                await message.pin()

    ############################################################
    # 処理内容：message編集時
    # 関数名　：agenda_on_message_edit
    # 引数　　：self        / メソッドの仮引数
    #        : before     / #Agendaへの投稿文(編集前)
    #        : after      / #Agendaへの投稿文(編集後)
    #        : SERVER_ID  / サーバID
    #        : CH_AGENDA  / #AgendaCHのCHID
    #        : CH_GENERAL / #雑談CHのCHID
    # 戻り値　：なし
    ############################################################
    async def agenda_on_message_edit(self,
                                     before,
                                     after,
                                     SERVER_ID,
                                     CH_AGENDA,
                                     CH_GENERAL
                                    ):
        
        # pin留めが#Agenda CHにておこなわれたとき
        if  before.pinned != after.pinned \
        and after.channel == CH_AGENDA:
            
            # 卓一覧出力処理
            await self.session_list_mes_send(SERVER_ID,
                                             CH_AGENDA,
                                             CH_GENERAL)

        # #Agenda Chにてメッセージの編集が行われたとき
        elif before.channel == CH_AGENDA \
        and  after.channel  == CH_AGENDA:

            if re.match('\@everyone', before.content):
                # 編集前のAgendaの投稿文を検査
                await self.agenda_edit(before,
                                       self.__SESSION_DEL_MODE)
            if re.match('\@everyone', after.content):
                # 編集後のAgendaの投稿文を検査
                await self.agenda_edit(after,
                                       self.__SESSION_ADD_MODE)
    
    ############################################################
    # 処理内容：message削除時
    # 関数名　：agenda_on_message_delete
    # 引数　　：self        / メソッドの仮引数
    #        : message    / message構造体
    #        : CH_AGENDA  / #Agendaのchannel
    # 戻り値　：なし
    ############################################################
    async def agenda_on_message_delete(self,
                                       message,
                                       CH_AGENDA
                                      ):
        
        # Agendaのメッセージが削除されたとき
        if message.channel == CH_AGENDA:
            # @everyoneからはじまるメッセージが削除されたとき
            if re.match('\@everyone', message.content):
                # 変数初期化
                self.agenda_param_init()

                # Agenda削除処理
                await self.agenda_del_sub(message)

    ############################################################
    # 処理内容：リアクション押下時
    # 関数名　：agenda_on_reaction_add
    # 引数　　：self        / メソッドの仮引数
    #        : user       / user構造体
    #        : reaction   / reaction構造体
    #        : CH_AGENDA  / #Agendaのchannel
    # 戻り値　：なし
    ############################################################
    async def agenda_on_reaction_add(self, user, reaction, CH_AGENDA):
        # リアクションが#Agenda CHに付与されたとき
        if reaction.message.channel == CH_AGENDA:
            # DMに参加申請した旨送信
            await self.dm_attendance_mes_send(user,
                                              self.__ATTENDANCE_ENTORY_MODE,
                                              reaction.message.content
                                             )

    ############################################################
    # 処理内容：リアクション削除時
    # 関数名　：agenda_on_reaction_remove
    # 引数　　：self        / メソッドの仮引数
    #        : user       / user構造体
    #        : reaction   / reaction構造体
    #        : CH_AGENDA  / #Agendaのchannel
    # 戻り値　：なし
    ############################################################
    async def agenda_on_reaction_remove(self, user, reaction, CH_AGENDA):
        # リアクションが#Agenda CHから消去されたとき
        if reaction.message.channel == CH_AGENDA:
            # DMに参加辞退した旨送信
            await self.dm_attendance_mes_send(user,
                                              self.__ATTENDANCE_DECLINE_MODE,
                                              reaction.message.content
                                             )

    ############################################################
    # 処理内容：日付変更時のタイマー処理
    # 関数名　：date_change
    #        : SERVER_ID  / サーバID
    #        : CH_AGENDA  / #AgendaCHのCHID
    #        : CH_GENERAL / #雑談CHのCHID
    # 戻り値　：なし
    ############################################################
    async def date_change(self, SERVER_ID, CH_AGENDA, CH_GENERAL):
        while True: # bot実行中無限ループ
            if time.strftime('%H:%M',time.localtime())=='00:00':
                # 現在時刻が00:00のとき、卓一覧出力処理を実行
                await self.session_list_mes_send(SERVER_ID,
                                                 CH_AGENDA,
                                                 CH_GENERAL
                                                )

            await asyncio.sleep(60) #60sスリープ

    ############################################################
    #
    # コールバック処理から呼び出されるサブルーチン
    #
    ############################################################
    
    ############################################################
    # 処理内容：Agenda登録処理
    # 関数名　：agenda_add_sub
    # 引数　　：self     / メソッドの仮引数
    #        : message / message構造体
    # 戻り値　：なし
    ############################################################
    async def agenda_add_sub(self, message):
        nRet = bool(True) # 戻り値格納用処理(True/False)

        # 投稿文から卓情報を構造体に格納する
        if self.data_create(message.content) == False:
            # 格納失敗時は処理終了
            nRet = bool(False)

        # 卓情報を検査する
        if self.message_check() == False:
            # 卓情報の形式不正時は処理終了
            nRet = bool(False)

        # 投稿文不正形式時
        if nRet == bool(False):
            # 不正の旨をdmで投稿者に送信
            await self.dm_err_mes_send(message,
                                       self.__AGENDA_FORMAT_ADD_ERROR
                                      )

        # 投稿文正常形式時
        else:
            # GoogleCalendar更新処理(追加)
            nRet = self.calendar_event_refresh(self.__SESSION_ADD_MODE,
                                               message
                                              )

            # GoogleCalendarへセッション情報登録失敗時
            if nRet == bool(False):
                # 不正の旨をdmで投稿者に送信
                await self.dm_err_mes_send(message,
                                           self.__AGENDA_CALENDAR_ADD_ERROR
                                          )

        return nRet

    ############################################################
    # 処理内容：Agenda投稿メッセージ編集時
    # 関数名　：agenda_edit
    # 引数　　：self     / メソッドの仮引数
    #        : message / message構造体
    #        : mode    / 編集前か後か
    #            編集前(self.__SESSION_DEL_MODE)
    #            編集後(self.__SESSION_ADD_MODE)
    # 戻り値　：なし
    ############################################################
    async def agenda_edit(self, message, mode):
        # 変数初期化
        self.agenda_param_init()

        if mode == self.__SESSION_DEL_MODE:
            # 編集前のメッセージに対して、Agenda削除処理
            await self.agenda_del_sub(message)
        else:
            # 編集後のメッセージに対して、Agenda登録処理
            nRet = await self.agenda_add_sub(message)
            
            # Agenda登録処理成功時
            if nRet == bool(True):
                # 登録メッセージをピンどめする
                await message.pin()

    ############################################################
    # 処理内容：Agenda削除処理
    # 関数名　：agenda_del_sub
    # 引数　　：self     / メソッドの仮引数
    #        : message / message構造体
    # 戻り値　：なし
    ############################################################
    async def agenda_del_sub(self, message):
        nRet = bool(True) # 戻り値格納用処理(True/False)

        # 投稿文から卓情報を構造体に格納する
        if self.data_create(message.content) == False:
            # 格納失敗時は処理終了
            nRet = bool(False)

        # 卓情報を検査する
        if self.message_check() == False:
            # 卓情報の形式不正時は処理終了
            nRet = bool(False)

        # 投稿文が正常時
        if nRet == bool(True):
            # GoogleCalendar更新処理(削除)
            nRet = self.calendar_event_refresh(self.__SESSION_DEL_MODE,
                                               message
                                              )

            # GoogleCalendarのセッション削除失敗時
            if nRet == bool(False):
                # 削除失敗の旨をdmで投稿者に送信
                await self.dm_err_mes_send(message,
                                           self.__AGENDA_CALENDAR_DEL_ERROR
                                          )

        return nRet

    ############################################################
    # 処理内容：卓情報を検査する処理
    # 関数名　：message_check
    # 引数　　：self     / メソッドの仮引数
    # 戻り値　：True     / 卓情報正常形式時
    #          Falese  / 卓情報不正形式時
    ############################################################
    def message_check(self):
        # 卓の種別の入力が正常化の検査
        if self.__agenda_dict["種別"] == (self.__SESSION_NONE):
            return bool(False)

        # 卓の種別が単発卓(0)のとき、開始日時のフォーマットが正しいかの検査
        if  self.__agenda_dict["種別"] == self.__SESSION_SINGLE \
        and self.date_check(self.__agenda_dict["開始日時"]) == bool(False):
            return bool (False)

        # 卓の種別が単発卓(0)のとき、終了日時のフォーマットが正しいかの検査
        if  self.__agenda_dict["種別"] == self.__SESSION_SINGLE \
        and self.date_check(self.__agenda_dict["終了日時"]) == bool(False):
            return bool (False)

        # システム/シナリオ/ツール/募集人数が空でないか検査
        if self.__agenda_dict["システム"] == None \
        or self.__agenda_dict["シナリオ名"] == None \
        or self.__agenda_dict["ツール"] == None \
        or self.__agenda_dict["募集人数"] == None:
            return bool (False)

        return bool(True)

    ############################################################
    # 処理内容：Agendaの投稿文から卓情報を構造体に格納する処理
    # 関数名　：data_create
    # 引数　　：self      / メソッドの仮引数
    #        : contents / #Agendaへの投稿文(文字列)
    # 戻り値　：True      / 投稿文を構造体に追加成功
    #          Falese   / 投稿文を構造体に追加失敗
    ############################################################
    def data_create(self, contents):
        #投稿文(contents)からAgendaの値を取得

        # 投稿文を|で分割
        split_contents = contents.split('｜')

        # データ格納配列を用意
        arrMes = list()
        
        # 投稿文のデータのみ抽出
        for i in range(len(split_contents)):
            # データを格納
            if i % 2 == 0:
                arrMes.append(split_contents[i])
        # @everyone行を削除
        del arrMes[0]

        # 投稿文のデータの要素数から不正形式かを判別
        if (len(arrMes) != len(self.__agenda_dict)):
            return bool(False)

        #投稿文の各要素を格納
        ## 種別は単発(0)/キャンペーン(1)/常時(2)/それ以外(-1)を設定
        nKindSession = self.__SESSION_NONE;

        if arrMes[0].find("単発") >= 0:
            nKindSession = self.__SESSION_SINGLE
        elif arrMes[0].find("キャンペーン") >= 0:
            nKindSession = self.__SESSION_CAMPAIN
        elif arrMes[0].find("常時") >= 0:
            nKindSession = self.__SESSION_ALLWAYS

        self.__agenda_dict["種別"] = nKindSession
        
        ## セッションの種別の入力が不正な場合Falseを返す
        if self.__agenda_dict["種別"] == self.__SESSION_NONE:
            return bool(False)

        try:
        
            ## 開始/終了日時/システム/シナリオ/ツール名は改行を消して格納
            self.__agenda_dict["開始日時"] = arrMes[1].replace('\n', '')
            self.__agenda_dict["終了日時"] = arrMes[2].replace('\n', '')
            self.__agenda_dict["システム"] = arrMes[3].replace('\n', '')
            self.__agenda_dict["シナリオ名"] = arrMes[4].replace('\n', '')
            self.__agenda_dict["ツール"] = arrMes[5].replace('\n', '')

            # 募集人数は数値として格納
            ## 半角数字以外ではエラーが発生
            self.__agenda_dict["募集人数"] = int(arrMes[6])
            
            # 概要は改行ありでそのまま取得
            self.__agenda_dict["概要"] = arrMes[7]

            return bool(True)
        
        except:
            return bool(False)

    ############################################################
    # 処理内容：GoogleCalendar更新処理
    # 関数名　：calendar_event_refresh
    # 引数　　：self     / メソッドの仮引数
    #        : mode    / カレンダー登録(0) / カレンダー削除(1)
    #        : message / message構造体
    # 戻り値　：True     / 更新処理正常終了
    #          Falese  / 更新処理異常終了
    ############################################################
    def calendar_event_refresh(self, mode, message):
        # 単発卓のみGoogleCalendarの操作を実施
        if self.__agenda_dict["種別"] != self.__SESSION_SINGLE:
            return bool(True) #
        
        # GoogleCalendarイベント名生成
        if self.calendar_event_name_create(message, mode) == bool(False):
            return bool(False)

        # カレンダーへの操作でエラーが発生した場合except文へ飛ぶ
        try:
            # カレンダーにイベントを追加
            if mode == self.__SESSION_ADD_MODE:
                calendar.add_calendar_event(self.__calendar_dict["件名"],
                                            self.__calendar_dict["開始日時"],
                                            self.__calendar_dict["終了日時"]
                                           )

                # カレンダーからイベントを削除
            else:
                calendar.del_calendar_event(self.__calendar_dict["件名"],
                                            self.__calendar_dict["開始日時"],
                                            self.__calendar_dict["終了日時"]
                                           )

            # 正常を返す
            return bool(True)

        # カレンダーAPIを叩いた結果エラーが発生したとき
        # 異常を返す
        except:
            return bool(False)

    ############################################################
    # 処理内容：GoogleCalendarイベント名生成処理
    # 関数名　：calendar_event_name_create
    # 引数　　：self     / メソッドの仮引数
    #        : message / message構造体
    #        : mode    / 登録/ 削除
    # 戻り値　：True     / 変換成功
    #          Falese  / 変換失敗
    ############################################################
    def calendar_event_name_create(self, message, mode):#カレンダーイベント名の生成処理
        # 件名の作成
        strAuthor = message.author.nick
        if strAuthor == None:
            strAuthor = message.author.name
        
        strSystem = self.__agenda_dict["システム"]
        # システム名がNoneのとき
        if strSystem == None:
            # 異常を返す
            return bool(False)

        strTitle  = strAuthor + "卓" + strSystem
        self.__calendar_dict["件名"] = strTitle

        # 日時の生成
        self.__calendar_dict["開始日時"] = self.date_format_convert_for_calendar(self.__agenda_dict["開始日時"])
        self.__calendar_dict["終了日時"] = self.date_format_convert_for_calendar(self.__agenda_dict["終了日時"])

        # GoogleCalendarAPIを叩くための情報が不足しているとき
        if self.__calendar_dict["件名"] == bool(False) \
                or self.__calendar_dict["開始日時"] == bool(False) \
                or self.__calendar_dict["終了日時"] == bool(False):
            # 異常を返す
            return bool(False)

        # GoogleCalendar削除時
        if mode == self.__SESSION_DEL_MODE:
            # 時刻の生成(削除時は時差の情報が必要)
            self.__calendar_dict["開始日時"] = self.date_format_convert_for_calendar(self.__agenda_dict["開始日時"]) + '+09:00'
            self.__calendar_dict["終了日時"] = self.date_format_convert_for_calendar(self.__agenda_dict["終了日時"]) + '+09:00'

        return bool(True)

    ############################################################
    # 処理内容：Agenda日付形式("YYYY/MM/DD HH:mm:SS")
    #           -> GoogleCalendar日付形式(YYMMDD"T"HHmmSS) 変換処理
    # 関数名　：date_format_convert_for_calendar
    # 引数　　：self     / メソッドの仮引数
    #        : date    / 日付文字列
    # 戻り値　：True     / 変換成功
    #          Falese  / 変換失敗
    ############################################################
    def date_format_convert_for_calendar(self, date):
        # 文字列操作に失敗したらexcept文へ飛ぶ
        try :
            # "YYYYMMDD"と"HHmmSS"へ分割
            result_time = str(date).split(' ')
            # "YYYY"と"MM"と"DD"へ分割
            result_ymd = result_time[0].split('/')
            # "HH"と"mm"と"SS"へ分割
            result_hms = result_time[1].split(':')

            # 時間の結合
            strTime = \
                result_ymd[0] + '-' \
                + result_ymd[1] + '-' \
                + result_ymd[2] + 'T' \
                + result_hms[0] + ':' \
                + result_hms[1] + ':' \
                + result_hms[2]

            # 改行を削除（何故かこれをやらないとうごかない）
            retTime  = strTime.split('\n')

            # 変換結果を返す
            return retTime[0]

        # エラー時異常を返す
        except :
            return bool(False)

    ############################################################
    # 処理内容：投稿文の日付検査処理
    # 関数名　：date_check
    # 引数　　：self     / メソッドの仮引数
    #        : date    / 日付文字列
    # 戻り値　：True     / 日付文字列が正常形式時
    #          Falese  / 日付文字列が正常形式時
    ############################################################
    def date_check(self, date):
        # 日付が"YYYY/MM/DD HH:mm:SS"形式かの検査
        # Agenda日付形式->GoogleCalendar日付形式が変換可能ならば
        # 形式は正常である。
        if (self.date_format_convert_for_calendar(date) == bool(False)):
            return bool(False)

        return bool(True)

    ############################################################
    # 処理内容：エラーメッセージ送信
    # 関数名　：dm_err_mes_send
    # 引数　　：self     / メソッドの仮引数
    #        : message / message構造体
    #        : mode    / エラーメッセージ作成モード
    #                      投稿文　不正形式時 /__AGENDA_FORMAT_ADD_ERROR
    #                      編集結果不正形式時 /__AGENDA_FORMAT_EDIT_ERROR
    #                      GoogleCalendar登録操作失敗時 /__AGENDA_CALENDAR_ADD_ERROR
    #                      GoogleCalendar削除操作失敗時 /__AGENDA_CALENDAR_DEL_ERROR
    # 戻り値　：なし
    ############################################################
    async def dm_err_mes_send(self, message, mode):
        # 投稿者に対して送信するdm構造体を生成
        dm = await message.author.create_dm()

        # 送信するエラーメッセージを生成
        send_ms = self.dm_err_mes_create(message.content, mode)

        # dmを送信
        await dm.send(send_ms)

    ############################################################
    # 処理内容：エラーメッセージ生成
    # 関数名　：dm_err_mes_send
    # 引数　　：self      / メソッドの仮引数
    #        : contents / #Agendaへの投稿文(文字列)
    #        : mode     / エラーメッセージ作成モード
    #                       投稿文　不正形式時 /__AGENDA_FORMAT_ADD_ERROR
    #                       編集結果不正形式時 /__AGENDA_FORMAT_EDIT_ERROR
    #                       GoogleCalendar登録操作失敗時 /__AGENDA_CALENDAR_ADD_ERROR
    #                       GoogleCalendar削除操作失敗時 /__AGENDA_CALENDAR_DEL_ERROR
    # 戻り値　：送信するエラーメッセージ
    ############################################################
    def dm_err_mes_create(self, contents, mode):
        AGENDA_STANDARD = '```\n@everyone\n｜　種　別　｜単発/キャンペーン/常時\n｜開始日時　｜2019/05/15 19:00:00 (' \
                          '半角で入力してください)\n｜終了日時　｜2019/05/15 23:00:00 (' \
                          '半角で入力してください)\n｜システム　｜SW2.5\n｜シナリオ名｜シナリオ名\n｜ツール　　｜どどんとふ\n｜募集人数　｜2(半角数字のみを入力願います)\n｜　概　要　｜\n卓の説明、その他。\n``` '

        err_message = ""

        # 投稿文不正形式時
        if mode == self.__AGENDA_FORMAT_ADD_ERROR:
            err_message = "以下の投稿文の形式が不正のため、Agendaの投稿に失敗しました。\n"
            err_message = err_message + "```\n"
            err_message = err_message + contents + "```\n"
            err_message = err_message + "以下の形式で投稿願います。\n"
            err_message = err_message + AGENDA_STANDARD

        # 編集結果不正形式時
        if mode == self.__AGENDA_FORMAT_EDIT_ERROR:
            err_message = "以下の投稿文の形式が不正のため、Agendaの編集に失敗しました。\n"
            err_message = err_message + "```\n"
            err_message = err_message + contents + "```\n"
            err_message = err_message + "以下の形式で投稿願います。\n"
            err_message = err_message + AGENDA_STANDARD

        # GoogleCalendar登録操作失敗時
        if mode == self.__AGENDA_CALENDAR_ADD_ERROR:
            err_message = "以下の卓の予定をカレンダーに追加することに失敗しました。\n"
            err_message = err_message + "```\n"
            err_message = err_message + contents + "```\n"
            err_message = err_message + " 開始日時/終了日時が半角で入力されていませんか。\n"
            err_message = err_message + " 時間をあけて投稿し直してください。何度も失敗する場合は管理者に連絡をお願いします。\n\n"

        # GoogleCalendar削除操作失敗時
        if mode == self.__AGENDA_CALENDAR_DEL_ERROR:
            err_message = "以下の卓の予定をカレンダーから削除することに失敗しました。\n"
            err_message = err_message + "```\n"
            err_message = err_message + contents + "```\n"
            err_message = err_message + " お手数ですが管理者に連絡をお願いします。\n\n"

        return err_message

    ############################################################
    # 処理内容：卓参加/辞退メッセージ送信
    # 関数名　：dm_attendance_mes_send
    # 引数　　：self      / メソッドの仮引数
    #        : user     / user構造体
    #        : mode     /
    #           卓参加 __ATTENDANCE_ENTORY_MODE
    #           卓辞退 __ATTENDANCE_DECLINE_MODE
    #        : contents / #Agendaへの投稿文(文字列)
    # 戻り値　：なし
    ############################################################
    async def dm_attendance_mes_send(self, user, mode, contents):
        # 投稿者に対して送信するdm構造体を生成
        dm = await user.create_dm()

        # 送信するエラーメッセージを生成
        send_ms = self.dm_attendance_mes_create(mode, contents)

        # dmを送信
        await dm.send(send_ms)

    ############################################################
    # 処理内容：卓参加/辞退メッセージ生成
    # 関数名　：dm_attendance_mes_create
    # 引数　　：self      / メソッドの仮引数
    #        : mode     /
    #           卓参加 __ATTENDANCE_ENTORY_MODE
    #           卓辞退 __ATTENDANCE_DECLINE_MODE
    #        : contents / #Agendaへの投稿文(文字列)
    # 戻り値　：送信するメッセージ
    ############################################################
    def dm_attendance_mes_create(self, mode, contents):
        # 変数初期化
        self.agenda_param_init()

        # 投稿文から卓情報を構造体に格納する
        self.data_create(contents)

        attendance_mes = "" # 送信メッセージ格納用変数

        # 卓参加申請
        if mode == self.__ATTENDANCE_ENTORY_MODE:
            if self.__agenda_dict["開始日時"] != "":
                attendance_mes = self.__agenda_dict["開始日時"] + "のセッションに参加申し込みました。"
            else:
                attendance_mes = "日時不明のセッションに参加申し込みました。"

        # 卓参加辞退
        else:
            if self.__agenda_dict["開始日時"] != "":
                attendance_mes = self.__agenda_dict["開始日時"] + "のセッションへの参加を辞退しました。"
            else:
                attendance_mes = "日時不明のセッションへの参加を辞退しました。"

        return attendance_mes

    ############################################################
    # 処理内容：卓一覧取得
    # 関数名　：session_list_send
    # 引数　　：self        / メソッドの仮引数
    #        : serverId   / Server ID
    #        : CH_AGENDA  / CH ID(#Agenda)
    #        : CH_GENERAL / CH ID(#General)
    # 戻り値　：なし
    ############################################################   
    async def session_list_mes_send(self,
                                    serverId,
                                    CH_AGENDA,
                                    CH_GENERAL):
        # 変数
        session_single_list = "";
        session_campain_list = "";
        session_allways_list = "";
        
        # メッセージURL https://discordapp.com/channels/[ServerID]/[ChId]/[MessageId]
        url_begin = "https://discordapp.com/channels/"
        
        # #AgendaChの取得
        channel = CH_AGENDA
        
        # ピンどめされたSession情報一覧を取得
        pin_mes_list = [await channel.fetch_message(message.id) for message in await channel.pins()]

        # セッション一覧の初期化
        self.__single_session_list = []
        self.__campain_session_list = []
        self.__allways_session_list = []
        
        # 各Session情報を閲覧
        for pin_mes_line in pin_mes_list:
            # クラス変数初期化
            self.agenda_param_init()            
            
            # pin留めされたメッセージ本文を取得
            mes_content = pin_mes_line.content

            # pin留めされたメッセージから卓情報を生成
            # 卓情報の項目数が不足している場合処理終了
            if self.data_create(mes_content) == bool(False):
                continue
            
            # 卓情報を検査する
            # 異常のとき処理終了
            if self.message_check() == bool(False):
                continue
            
            # session_listを作成
            await self.session_list_mes_create(pin_mes_line);

        # session_listをソート
        # 単発卓は日付順にソート
        self.__single_session_list.sort(key=lambda x: x[ "開始日時" ])
        
        # 常時卓はシステム順にソート
        self.__allways_session_list.sort(key=lambda x: x['システム'])
        
        # 現在の卓総数を出力
        send_message ='現在開催予定のセッションは'+str( len(pin_mes_list) - 1 )+'件です。\n\n'
        
        # 単発卓の追加
        if len(self.__single_session_list) != 0:
            send_message = send_message + "\n単発卓\n"

        # 単発卓のリストを出力
        for event_data in self.__single_session_list:
            messageUrl = f"{url_begin}{serverId}/{CH_AGENDA.id}/{event_data['メッセージID']}"
            message_row = f"{event_data['開始日時'].strftime('%Y/%m/%d %H:%M')}～ " \
                          f"[{event_data['GM名']}卓" \
                          f"{event_data['システム']}]({messageUrl}) " \
                          f"{event_data['参加人数']} / "\
                          f"{event_data['募集人数']}\n"
            send_message = send_message + message_row

        # キャンペーン卓の追加
        if len(self.__campain_session_list) != 0:
            send_message = send_message + "\nキャンペーン卓\n"
            
        # キャンペーン卓のリストを出力
        for event_data in self.__campain_session_list:
            messageUrl = f"{url_begin}{serverId}/{CH_AGENDA.id}/{event_data['メッセージID']}"
            message_row = f"[{event_data['GM名']}卓" \
                          f"{event_data['システム']}]({messageUrl}) " \
                          f"{event_data['参加人数']} / "\
                          f"{event_data['募集人数']}\n"
            send_message = send_message + message_row
            
        # 常時卓の追加
        if len(self.__allways_session_list) != 0:
            send_message = send_message + "\n常時卓\n"

        # 常時卓のリストを出力
        for event_data in self.__allways_session_list:
            messageUrl = f"{url_begin}{serverId}/{CH_AGENDA.id}/{event_data['メッセージID']}"
            message_row = f"[{event_data['GM名']}卓" \
                          f"{event_data['システム']}]({messageUrl}) " \
                          f"{event_data['参加人数']} / "\
                          f"{event_data['募集人数']}\n"
            send_message = send_message + message_row
        
        # 埋め込みメッセージの作成
        embed = discord.Embed(title="卓情報",
                              description=f"{send_message}")

        # メッセージの送信
        await CH_GENERAL.send(embed=embed)

    ############################################################
    # 処理内容：卓一覧作成
    # 関数名　：session_list_send
    # 引数　　：self     / メソッドの仮引数
    #        : message / message構造体
    # 戻り値　：なし
    ############################################################   
    async def session_list_mes_create(self, message):
        # ピンどめされたメッセージが単発卓のとき
        if self.__agenda_dict["種別"] == self.__SESSION_SINGLE:
            await self.single_session_list_mes_create(message)
            
        # ピンどめされたメッセージがキャンペーン卓のとき
        if self.__agenda_dict["種別"] == self.__SESSION_CAMPAIN:
            self.campain_session_list_mes_create(message)

        # ピンどめされたメッセージが常時卓のとき
        if self.__agenda_dict["種別"] == self.__SESSION_ALLWAYS:
            self.allways_session_list_mes_create(message)
            
    ############################################################
    # 処理内容：単発卓一覧作成
    # 関数名　：single_session_list_create
    # 引数　　：self     / メソッドの仮引数
    #        : message / message構造体
    # 戻り値　：なし
    ############################################################   
    async def single_session_list_mes_create(self, message):
        # 辞書型の宣言
        session_dict = {
            "開始日時" : None,
            "GM名" : None,
            "システム" : None,
            "セッション名" : None,
            "参加人数" : None,
            "募集人数" : None,
            "メッセージID" : None,
        }
        
        # 今日の日時の取得
        today_date = datetime.datetime.now()
        
        # 開始日時の取得
        start_date = self.convert_start_time()
        if start_date == bool(False):
            return
                
        # 今日より開始日が古い場合pin留めを外す
        if start_date < today_date:
            await message.unpin()
            return
        
        # 日付を詰める
        session_dict["開始日時"] = start_date
        
        # GM名取得
        session_dict["GM名"] = message.author.nick
        if session_dict["GM名"] == None:
            session_dict["GM名"] = message.author.name

        # システム名取得
        session_dict["システム"] = self.__agenda_dict["システム"]
        
        # 募集人数取得
        session_dict["募集人数"]  = self.__agenda_dict["募集人数"]
        
        # 参加者数取得
        session_dict["参加人数"]  = sum(reaction.count for reaction in message.reactions)
        
        # メッセージidを追加
        session_dict["メッセージID"] = message.id
        
        # __session_listに卓情報を追加
        self.__single_session_list.append(session_dict)

    ############################################################
    # 処理内容：開始日を時間型に変換
    # 関数名　：convert_start_time
    # 引数　　：self            / メソッドの仮引数
    #        : message        / message構造体
    # 戻り値　：開始日時(時間型)　/ 変換成功時 
    #        : False          /　変換失敗時
    ############################################################
    def convert_start_time(self):
        try:
            start_date = datetime.datetime.strptime(self.__agenda_dict["開始日時"],
                                                    '%Y/%m/%d %H:%M:%S'
                                                   )
            return start_date
        
        except:
            return bool(False)

    ############################################################
    # 処理内容：キャンペーン卓一覧作成
    # 関数名　：campain_session_list_mes_create
    # 引数　　：self     / メソッドの仮引数
    #        : message / message構造体
    # 戻り値　：なし
    ############################################################   
    def campain_session_list_mes_create(self, message):
        # 辞書型の宣言
        session_dict = {
            "GM名" : None,
            "システム" : None,
            "セッション名" : None,
            "参加人数" : None,
            "募集人数" : None,
            "メッセージID" : None,
        }
        
        # GM名取得
        session_dict["GM名"] = message.author.nick
        if session_dict["GM名"] == None:
            session_dict["GM名"] = message.author.name

        # システム名取得
        session_dict["システム"] = self.__agenda_dict["システム"]
        
        # 募集人数取得
        session_dict["募集人数"]  = self.__agenda_dict["募集人数"]
        
        # 参加者数取得
        session_dict["参加人数"]  = sum(reaction.count for reaction in message.reactions)
        
        # メッセージidを追加
        session_dict["メッセージID"] = message.id
    
        # __session_listに卓情報を追加
        self.__campain_session_list.append(session_dict)

    ############################################################
    # 処理内容：常時卓一覧作成
    # 関数名　：allways_session_list_mes_create
    # 引数　　：self     / メソッドの仮引数
    #        : message / message構造体
    # 戻り値　：なし
    ############################################################   
    def allways_session_list_mes_create(self, message):
        # 辞書型の宣言
        session_dict = {
            "GM名" : None,
            "システム" : None,
            "セッション名" : None,
            "参加人数" : None,
            "募集人数" : None,
            "メッセージID" : None,
        }
        
        # GM名取得
        session_dict["GM名"] = message.author.nick
        if session_dict["GM名"] == None:
            session_dict["GM名"] = message.author.name

        # システム名取得
        session_dict["システム"] = self.__agenda_dict["システム"]
        
        # 募集人数取得
        session_dict["募集人数"]  = self.__agenda_dict["募集人数"]
        
        # 参加者数取得
        session_dict["参加人数"]  = sum(reaction.count for reaction in message.reactions)
        
        # メッセージidを追加
        session_dict["メッセージID"] = message.id
    
        # __session_listに卓情報を追加
        self.__allways_session_list.append(session_dict)
        
        