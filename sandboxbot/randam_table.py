################################################################
#
# ファイル名：randam_table.py
# 処理機能　：ランダム表を振る機能
#
################################################################

################################################################
#
# ライブラリのインポート
#
################################################################
# Python標準ライブラリ
import csv  # CSVファイルを扱うモジュール

################################################################
#
# RandamTable
#
################################################################
class RandamTable:

    ############################################################
    # 処理内容：コンストラクタ
    # 関数名　：__init__
    # 引数　　：self / メソッドの仮引数
    # 戻り値　：なし
    ############################################################
    def __init__(self):
        pass
    
    ############################################################
    # 処理内容：ランダム表の結果をメッセージとして送信する
    # 関数名　：result_randam_table_message
    # 引数　　：self        / メソッドの仮引数
    # 　　　　：filename    / ランダム表のファイル名
    #                        ファイルはutf8で記述され、","区切りであること
    # 　　　　：read_raw    / 読み込む行
    # 　　　　：read_column / 読み込む列(リスト型)
    # 　　　　：delimiter   / 出力文字の区切り文字
    # 戻り値　：send_ms
    ############################################################
    def result_randam_table_message(self,
                                    filename,
                                    read_raw,
                                    read_column,
                                    delimiter
                                    ):
        # ランダム表の内容を取得
        line = self.result_randam_table(filename,
                                        read_raw
                                       )
        
        # 行を読み込めなかったとき
        if line == bool(False):
            return "csvファイルの読み込みに失敗しました。"
        
        # 出力メッセージの初期化
        send_ms = ''
        
        # 指定されたフィールドを結合してメッセージにする
        for s in range(0, len(read_column)):

            if send_ms == '':
                send_ms = line[read_column[s]]
            else:
                send_ms = send_ms + delimiter + line[read_column[s]]
        
        return send_ms
    
    ############################################################
    # 処理内容：ランダム表を振る
    # 関数名　：result_randam_table
    # 引数　　：self         / メソッドの仮引数
    # 　　　　：filename     / ランダム表のファイル名
    #                         ファイルはutf8で記述され、","区切りであること
    # 　　　　：read_raw     / 読み込む行
    # 　　　　：read_column  / 読み込む列(リスト型)
    # 　　　　：delimiter    / 出力文字の区切り文字
    # 戻り値　：send_ms
    ############################################################
    def result_randam_table(self,
                            filename,
                            read_raw
                           ):
        # CSV読み込み行数のクリア
        row_counter = 0
        
        # csvファイルの行読み込みバッファのクリア
        line = ''

        # csvファイルオープン
        with open(filename, "r", encoding="utf8") as f:
            # csvファイル内容取得
            reader = csv.reader(f)
            
            # 行ごとにデータ読み込み
            for row in reader:
                
                # 読み込んだ行が、指定行のとき
                if row_counter == read_raw:
                    # 読み込み指定行を取得して処理終了
                    line = row
                    break;
                    
                # 読み込み行数を1増やす
                row_counter = row_counter + 1
        
        # 行を読み込めなかったとき
        if line == '':
            return bool(False)
        
        return line