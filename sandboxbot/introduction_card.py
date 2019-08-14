################################################################
#
# ファイル名：introduction_card.py
# 処理機能　：自己紹介カード生成機能(作成途中で投げた)
#
################################################################

################################################################
#
# ライブラリのインポート
#
################################################################
# Python標準ライブラリ
import io                   # ファイルI/Oを扱うモジュール
import re                   # 正規表現モジュール
import requests             # HTTPリクエストを扱うモジュール

# 有志制作のライブラリ
import discord              # discord用APIラッパー   ver1.0.1
from   PIL import Image     # 画像処理モジュール       ver6.0.0

################################################################
#
# IntroductionCard
#
################################################################
class IntroductionCard:

    ############################################################
    # 処理内容：コンストラクタ
    # 関数名　：__init__
    # 引数　　：self        / メソッドの仮引数
    # 戻り値　：なし
    ############################################################
    def __init__(self):
        pass
        
    ############################################################
    # 処理内容：message投稿時
    # 関数名　：introduction_card_on_message
    # 引数　　：self        / メソッドの仮引数
    #        : message    / message構造体
    # 戻り値　：なし
    ############################################################
    async def introduction_card_on_message(self, message):
        if isinstance(message.channel, discord.DMChannel):
            # botへのDM送信時、処理を終了する
            return
        
        # 自己紹介カード生成コマンド
        if re.match('\$avatar', com):
            await self.introduction_card_create(message)
            
    ############################################################
    # 処理内容：message投稿時
    # 関数名　：introduction_card_on_message
    # 引数　　：self        / メソッドの仮引数
    #        : message    / message構造体
    # 戻り値　：なし
    ############################################################
    async def introduction_card_create(self, message):
        # com送信者のアバター画像のurlを取得
        avatar_url = message.author.avatar_url

        # ヴェノーさん作の自己紹介カードの画像URL
        card_url   = 'https://cdn.discordapp.com/attachments/425609740152995840/571361111325147185/712651fbc55cd866.png'

        # 各画像をimageオブジェクトに保存
        user_img   = Image.open(io.BytesIO(requests.get(avatar_url).content))
        card_image = Image.open(io.BytesIO(requests.get(card_url).content))

        # アバター画像を自己紹介カードの枠内にペースト
        card_image.paste(user_img, (6,10))

        # 自己紹介カードの画像を保存
        card_image.save('test.png', quality=95)

        # 保存した画像をdiscordへ送信
        await message.channel.send('Hello',
                                   file=discord.File('test.png')
                                  )

        # 画像を削除
        #os.remove('test.png') # できない！なじぇ！！
