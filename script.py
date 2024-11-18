# -*- coding: utf-8 -*-
"""価格.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/17ajPHMt6M-6Xf37DZBc90_wQ08QsdYkY
"""

import json
import os
# import gspread # このimportをcredsを定義した後に移動しました
from oauth2client.service_account import ServiceAccountCredentials
import requests
import re
import gspread
from time import sleep

def authenticate_google_sheets():
    # 環境変数から資格情報ファイルのパスを取得
    credentials_file = os.getenv("GOOGLE_SHEETS_CREDENTIALS")
    
    # 資格情報ファイルが正しく指定されているかチェック
    if not credentials_file:
        raise ValueError("GOOGLE_SHEETS_CREDENTIALS environment variable is not set or the file path is invalid.")

    # 認証スコープの設定
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    # サービスアカウントの認証
    creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_file, scope)
    
    # 認証クライアントの生成
    client = gspread.authorize(creds)
    return client

def fetch_prices():
    # Google Sheetsの認証
    client = authenticate_google_sheets()
    sheet = client.open("PCパーツの価格").sheet1  # シート名を"PCパーツの価格"に変更

    # データの取得（ヘッダーを考慮せずにすべてのデータを取得）
    data = sheet.get_all_values()  # ヘッダーを認識せずにすべてのデータを取得
    print(data)

# Google Sheetsに書き込む関数
def update_google_sheet(sheet, cell, value):
    worksheet = sheet.get_worksheet(0)  # 最初のシート
    worksheet.update_acell(cell, value)  # 特定のセルに値を更新

# 価格を取得する関数
# 価格を取得する関数
def get_price_from_kakaku(url):
    try:
        # ページのHTMLを取得
        response = requests.get(url)
        response.encoding = 'shift_jis'  # 文字エンコーディングを指定
        html = response.text  # HTMLの内容を取得

        # data-price属性から価格を抽出する正規表現
        price_regex = r'data-price="([0-9,]+)"'
        match = re.search(price_regex, html)

        if match:
            return match.group(1)  # 価格を返す
        else:
            return "0"  # 価格が見つからなければ"0"を返す
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return "0"  # エラーが発生した場合は"0"を返す

# 複数のURLから価格を取得し、Google Sheetsに反映する関数
def fetch_prices():
    # Google Sheetsの認証
    client = authenticate_google_sheets()

    # スプレッドシートのURLを指定して開く
    sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1bx8hShkTDt1cOGNtCNHCa4XJ0hCveS_Znbyb0n9iYrg/edit?hl=ja&gid=0#gid=0")  # スプレッドシートのURL

    # 価格ドットコムのURLリスト
    kakaku_urls = [
      "https://www.dospara.co.jp/SBR1299/IC479652.html",
      "https://www.dospara.co.jp/SBR1753/IC502153.html",
      "https://www.dospara.co.jp/SBR282/IC478940.html",
      "https://www.dospara.co.jp/SBR1297/IC466703.html",
      "https://www.dospara.co.jp/SBR448/IC490205.html",
      "https://www.dospara.co.jp/SBR1144/IC497399.html",
      "https://www.dospara.co.jp/SBR83/IC510319.html",  
      "https://www.dospara.co.jp/SBR1017/IC482007.html"
    ]

    # URLごとに価格を取得し、Google Sheetsに反映
    for index, url in enumerate(kakaku_urls):
        price = get_price_from_kakaku(url)
        print(f"取得した価格 (価格.com): {price}")  # 取得した価格を表示

        # E列またはR列に価格を設定
        cell_range = f'F{6 + index}'  # E列の6行目からスタートして6行ずつ増加

        # Google Sheetsに価格を更新
        update_google_sheet(sheet, cell_range, price)

        sleep(10)

# 実行する
fetch_prices()
