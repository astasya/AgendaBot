from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar']

def main():
    # token.pickleを初期作成する際は外すこと。
    creds = None
    # token.pickleファイルには、ユーザーのアクセストークンと更新トークンが格納されています。
    # 許可フローが最初に完了したときに自動的に作成されます。

    # token.pickleの読み込み
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # token.pickleの読み込み失敗時
    # 利用可能な（有効な）認証情報がない場合は、ユーザーにログインさせます。
    if not creds or not creds.valid:
        ## ここなんのしょりしてる？条件わかんね
        if creds and creds.expired and creds.refresh_token:
            # ブラウザのリフレッシュ
            creds.refresh(Request())

        # ブラウザで認証URLを開く
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server()

        # 次回の実行のために資格情報を保存します
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

if __name__ == '__main__':
    main()