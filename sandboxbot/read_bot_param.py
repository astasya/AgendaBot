################################################################
#
# ファイル名：read_bot_param
# 処理機能　：botの起動オプション取得機能
#
################################################################
# Python標準ライブラリ
import argparse             # コマンドライン解析モジュール
import json                 # JSON形式ファイルを扱うライブラリ

################################################################
#
# 入力するJSONファイルの内容
#
################################################################
#{
#  "bot_status":[
#    {
#      "code":"Debug mode", # デバッグ環境の設定
#      "token"     :"---",  # botトークン、文字列で記述
#      "server_id" :---,    # サーバID、数値で記述(以前は文字列だった)
#      "ch_general":---,    # チャンネルID、数値で記述(以前は文字列だった)
#      "ch_agenda" :---,    # ... 以下Botで扱いたいCHだけ作る
#    },
#    {
#      "code":"Exe mode",   # 本番環境の設定
#      "token"     :"---",  # botトークン、文字列で記述
#      "server_id" :---,    # サーバID、数値で記述(以前は文字列だった)
#      "ch_general":---,    # チャンネルID、数値で記述(以前は文字列だった)
#      "ch_agenda" :---,    # ... 以下Botで扱いたいCHだけ作る
#    }
#  ]
#}

################################################################
# 処理内容：bot起動オプションに応じたDiscordの各パラメータの取得処理
# 関数名　：get_bot_options
# 引数　　：path / jsonファイルのパス
# 戻り値　：bot_status / 辞書型のDiscordの各パラメータ
################################################################
def get_bot_options(path):
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
    
    # BOTトークン、サーバID、CHIDを配列に格納
    bot_status = param_json['bot_status'][index]
    
    # 取得した情報を返却
    return bot_status
