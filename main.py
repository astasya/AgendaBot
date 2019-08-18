################################################################
#
# ファイル名：main.py
# 処理機能　：メイン処理
# 開発環境　：python3.7.3
#
# メ　　モ　：本番環境へコミット時、
#           絶対にTEST_MODEがFalseになっていることを確認すること。
#
################################################################

################################################################
#
# ライブラリのインポート
#
################################################################
# Python標準ライブラリ
import asyncio              # 非同期処理フレームワーク
import re                   # 正規表現モジュール

# 有志制作のライブラリ
import discord              # discord用APIラッパー   ver1.0.1

# 自作モジュール
from sandboxbot import *    # 自作パッケージディレクトリ(./sandboxbot)に
                            # 存在する全モジュールをインポートする。

################################################################
#
# Botの情報を取得
#
################################################################
# Botトークン等を格納したJSONファイルから情報を取得
    ## メモ : JSONファイルの内容詳細はread_bot_param.pyを参照
bot_options = read_bot_param.get_bot_options('./bot_options.json')

# JSONファイルから取得した情報を各変数に格納
TOKEN        = bot_options["token"]             # BOTのトークン
SERVER_ID    = bot_options["server_id"]         # Discordの鯖ID
CH_GENERAL   = bot_options["ch_general"]        # 雑談用CHのID(#雑談)
CH_AGENDA    = bot_options["ch_agenda" ]        # TRPGセッション管理用CHのID(#agenda)
CH_BOT       = bot_options["ch_bot"    ]        # Bot用CHのID(#dicebot)
CH_ADMIN     = bot_options["ch_admin"  ]        # 管理者専用CHのID(#staff)

CAT_GENERAL  = bot_options["cat_general"]       # 雑談を行うVCのカテゴリ
CAT_SESSION  = bot_options["cat_session"]       # TRPGセッションを行うVCのカテゴリ
CAT_OTHER    = bot_options["cat_other"]         # ゲーム全般を行うVCのカテゴリ

ROLE_ADMIN   = bot_options["role_admin"]        # サーバの管理者の役職
ROLE_STAFF   = bot_options["role_staff"]        # サーバの管理権限保有者の役職

################################################################
#
# main
#
################################################################
if __name__ == '__main__': # 直接実行モジュールの指定

    ############################################################
    #
    # インスタンス生成
    #
    ############################################################
    # discord.py
    client = discord.Client()
    
    # サーバマネジメント系
    agenda  = agenda_control.AgendaControl()    # TRPGセッション管理機能
    link    = useful_link.UsefulLink()          # 便利サイト紹介
    alog    = access_log.Alog()                 # アクセスログ解析機能
    mgmt    = server_management.Mgmt()          # サーバ管理機能

    # TRPG系
    dice    = dice_bot.DiceBot()                # ダイスを振る機能
    sw      = sw_bot.SwBot()                    # SW2.0/2.5　キャラクター作成支援機能
    coc     = coc_bot.CoCBot()                  # CoC キャラクター作成支援機能
    dx3rd   = dx3rd_bot.Dx3rdBot()              # DX3rd キャラクター作成支援機能

    # 他お遊び機能
    # jinro_game = jinro.Jinro()                # 人狼を実行する機能(開発中)

    ############################################################
    # 処理内容：ヘルプ出力機能
    # 処理概要：CHにてヘルプコマンドが送信されたときに、
    #          ヘルプを出力する
    # 関数名　：send_bot_help
    # 引数　　：なし
    # 戻り値　：なし
    ############################################################
    async def send_bot_help(message):
        
        # DMに送られたメッセージは無視
        if isinstance(message.channel, discord.DMChannel):
            return
        
        # ヘルプコマンド送信時
        if re.match('\$help', message.content):
            # ヘルプメッセージ
            # 詳細なヘルプは各モジュールを参照させるようにする。
            HELP_MSG = ['``` ### 便利機能 ###',
                        '$list 卓の予定の一覧を#chatに表示する。',
                        '$useful_link 便利なサイトの一覧を出力する。',
                        '```',
                        '``` ### サーバ管理補助機能 ###',
                        '$mgmt_help Sandbox管理用の補助機能のヘルプを表示する。',
                        '```',
                        '``` ### アクセスログ解析機能 ###',
                        '$alog_help Textチャンネル及びVCチャンネルへのアクセスログ解析機能についてのヘルプを表示する。',
                        '```',
                        '``` ### TRPGを遊ぶ ###',
                        '$dice_help ダイスを振る機能についてのヘルプを表示する。',
                        '$sw_help SW2.0/2.5 キャラクター作成支援機能についてのヘルプを表示する。',
                        '$coc_help CoC キャラクター作成支援機能についてのヘルプを表示する。',
                        '$dx3rd_help DX3rd キャラクター作成支援機能についてのヘルプを表示する。',
                        '```',
                        #'``` ### その他面白い機能 ###',
                        #'$jinro_help 人狼を実行する機能についてのヘルプを表示する。',
                        #'```',
                       ]

            # 送信メッセージの初期化
            send_ms = ''

            # ヘルプメッセージの生成
            for help_row in HELP_MSG:
                # ヘルプの配列を順番にmesへ格納
                send_ms = send_ms + help_row + '\n'

            # ヘルプメッセージを入力されたCHへ送信
            await message.channel.send(send_ms)
            
    ############################################################
    #
    # Discord.pyの各イベント毎の処理を以下に記述
    #
    ############################################################
    
    ############################################################
    # 処理内容：bot起動時の処理
    # 関数名　：on_ready
    # 引数　　：なし
    # 戻り値　：なし
    ############################################################
    @client.event
    async def on_ready():
        # botの情報をコンソール出力
        dsp_ms = f"-----\n"    \
                 f"Login Bot Name : {client.user.name}\n" \
                 f"Login Bot ID   : {client.user.id}\n"   \
                 f"-----"
        print(dsp_ms)
        
        ########################################################
        #
        # Bot起動後、呼び出すスレッドを以下に記述
        #
        ########################################################
        # アクセスログ解析機能 Bot再起動時処理
        await alog.alog_on_ready(client.get_guild(SERVER_ID))

        # TRPGセッション管理機能 日付変更時処理
        asyncio.ensure_future(agenda.date_change(SERVER_ID,
                                                 client.get_channel(CH_AGENDA),
                                                 client.get_channel(CH_GENERAL)
                                                )
                             )
            # メモ : asyncioは同時に実行している処理を妨げないスレッド処理です。
        
        ######### Bot起動後、呼び出すスレッドの記述 ここまで #########

    ############################################################
    # 処理内容：メッセージ投稿時の処理
    # 関数名　：on_message
    # 引数　　：message / メッセージオブジェクト
    # 戻り値　：なし
    ############################################################       
    @client.event
    async def on_message(message):

        # 総合ヘルプ出力
        await send_bot_help(message)
        
        # サーバマネジメント系
        ### TRPGセッション管理機能
        await agenda.agenda_on_message(SERVER_ID,
                                       message,
                                       client.get_channel(CH_AGENDA),
                                       client.get_channel(CH_GENERAL)
                                      )
        ### 便利サイト紹介
        await link.usefullink_on_message(message,
                                         client.get_channel(CH_BOT)
                                         )
        ### サーバ管理補助機能
        await mgmt.mgmt_on_message(message)

        ### アクセスログ解析機能
        await alog.alog_on_message(message, [ROLE_ADMIN, ROLE_STAFF])
            
        # TRPG系
        ### ダイスを振る機能
        await dice.dice_on_message(message)
        ### SW2.0/2.5　キャラクター作成支援機能
        await sw.sw_on_message(message)
        ### CoC キャラクター作成支援機能
        await coc.coc_on_message(message)
        ### DX3rd キャラクター作成支援機能
        await dx3rd.dx3rd_on_message(message)
        
        # 他お遊び機能
        ### 人狼を実行する機能(開発中)
        #await jinro_game.jinro_on_message(client, message)

        # 試験時に使用するときのみTEST_MODEをTrueにすること
        # ！！！ 絶対に本番環境に持ち込まないこと ！！！
        TEST_MODE = False
        if TEST_MODE == True:
            # メッセージの全削除
            if message.content == '/cleanup':
                await message.channel.purge()

    ############################################################
    # 処理内容：メッセージ編集時の処理
    # 関数名　：on_message_edit
    # 引数　　：before / メッセージオブジェクト
    #        : after / メッセージオブジェクト
    # 戻り値　：なし
    ############################################################    
    @client.event
    async def on_message_edit(before, after):
        # TRPGセッション管理機能
        await agenda.agenda_on_message_edit(before,
                                            after,
                                            SERVER_ID,
                                            client.get_channel(CH_AGENDA),
                                            client.get_channel(CH_GENERAL)
                                           )
    
    ############################################################
    # 処理内容：メッセージ削除時の処理
    # 関数名　：on_message_delete
    # 引数　　：message / メッセージオブジェクト
    # 戻り値　：なし
    ############################################################      
    @client.event
    async def on_message_delete(message):
        # TRPGセッション管理機能
        await agenda.agenda_on_message_delete(message,
                                              client.get_channel(CH_AGENDA)
                                             )

    ############################################################
    # 処理内容：reaction付与時の処理
    # 関数名　：on_reaction_add
    # 引数　　：reaction / リアクションオブジェクト
    #        : user / ユーザーオブジェクト
    # 戻り値　：なし
    ############################################################   
    @client.event
    async def on_reaction_add(reaction, user):
        # TRPGセッション管理機能
        await agenda.agenda_on_reaction_add(user,
                                            reaction,
                                            client.get_channel(CH_AGENDA)
                                           )

    ############################################################
    # 処理内容：reaction消去時の処理
    # 関数名　：on_reaction_remove
    # 引数　　：reaction / リアクションオブジェクト
    #        : user / ユーザーオブジェクト
    # 戻り値　：なし
    ############################################################    
    @client.event
    async def on_reaction_remove(reaction, user):
        # TRPGセッション管理機能
        await agenda.agenda_on_reaction_remove(user,
                                               reaction,
                                               client.get_channel(CH_AGENDA)
                                              )

    ############################################################
    # 処理内容：VoiceChatIN/OUT時の処理
    # 関数名　：on_voice_state_update
    # 引数　　：reaction / リアクションオブジェクト
    #        : user / ユーザーオブジェクト
    # 戻り値　：なし
    ############################################################    
    @client.event
    async def on_voice_state_update(member, before, after):
        # アクセスログ解析機能
        guild = client.get_guild(SERVER_ID)
        afk_channel_id = None
        for row in guild.voice_channels:
            if str(row.name) == str(guild.afk_channel):
                afk_channel_id = row.id
        await alog.on_voice_state_update(member,
                                         before,
                                         after,
                                         afk_channel_id
                                        )

    client.run(TOKEN) # bot実行、discord鯖への接続
