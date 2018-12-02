### import はしなくても動くが、あっても障害されるわけではないことを確認した
### これで、Google Cloud Functions でも一時ファイルを作成して、さらに
### Google Cloud Storage に書き出すことができることを確認できた。
### Google Cloud Functions を使ってファイルを生成する処理ができるようだ。

'''
#####################################################################
# ストレージ（GCS - Google Cloud Strage）認証を行う
# 以下の『#1』『#2』『#3』が
#####################################################################
# The first step is to create a bucket in your cloud project.
#
# Replace the assignment below with your cloud project ID.
#
# For details on cloud projects, see:
# https://cloud.google.com/resource-manager/docs/creating-managing-projects
# バケットを作るプロジェクトはどこでしょう。
# 1 #
project_id = 'aerobic-factor-216914'
# Authenticate to GCS.
# 2 #
from google.colab import auth
# 3 #
auth.authenticate_user()
# これが、google.colab からの認証。google-cloud-functionsからの認証は
# どのようにやればいいのだろうか。当面ここからやるか・・・
#####################################################################
'''

from googleapiclient import discovery
# from apiclient import discovery

from httplib2 import Http

from oauth2client import tools
from oauth2client import client
from oauth2client.client import GoogleCredentials

from oauth2client.file import Storage

import os
import sys

# import datetime
# import code
###

# !pip install flask
# import flask

def get_ebooks_by_author(request):
    # この関数を実行するように設定しておく。
    """ HTTP Cloud Function
    Prints available ebooks by "author" (optional: "lang")
    Arg: request (flask.Request)
    引数：request (flask.Request)
    例：以下のURLをショートカットで作っておき、クリックする
　https://us-central1-aerobic-factor-216914.cloudfunctions.net/function-3?author=芥川龍之介
    """
    #
    request_json = request.get_json()
    # author
    if request.args and 'author' in request.args:
        author = request.args.get('author')
    elif request_json and 'author' in request_json:
        author = request_json['author']
    else:
        author = '星 新一'
    # lang
    if request.args and 'lang' in request.args:
        lang = request.args.get('lang')
    elif request_json and 'lang' in request_json:
        lang = request_json['lang']
    else:
        lang = 'ja'
    #
    # 指定のauthorおよびlangでの著作名のリストを得るために
    # 以下の通りの呼び出し。結果を文字列として保管。
    author_books = print_author_books(author, lang)
    headers = {'Content-Type': 'text/plain; charset=utf-8'}
    #
    # 結果をファイルに書き出す。
    write_ebooks_by_author(author_books)
    #
    return author_books, headers

# 指定のauthorおよびlangでの著作名のリストを得る関数
#
def print_author_books(author, lang):
    # 著者名と対象言語を指定して get_google_books_data を呼び出す
    '''Returns book data in plain text table 
    著作名データ（book data）をプレーンテキストの表形式で作成して
    関数値として返す。
    '''
    # 内部でのみ使う関数：ページ数でのソート
    # 使い方：get_google_books_dataのsortメソッドでkeyとして指定する
    #
    def sort_by_page_count(book):
        return book['volumeInfo'].get('pageCount', 0)
    #
    books = get_google_books_data(author, lang)
    books.sort(key=sort_by_page_count, reverse=True)
    #
    # 右詰め４文字｜右詰め５文字｜小数点以下６５桁？？
    # 行番号　　　｜ページ数　　｜著作名
    line_fmt = '{:>4} | {:>5} | {:.65}\n'
    lines = [
        '{sep}{h1}{sep}{h2}'.format(
            h1='{:^80}\n'.format('"%s" ebooks (lang=%s)' % (author, lang)),
            h2=line_fmt.format('#', 'Pages', 'Title'),
            sep='{:=<80}\n'.format('')
        )]
    for idx, book in enumerate(books, 1):
        accessInfo = book['accessInfo']
        if not accessInfo['epub']['isAvailable']:
            continue
        volumeInfo = book['volumeInfo']
        title = volumeInfo['title']
        subtitle = volumeInfo.get('subtitle')
        if subtitle is not None:
            title += ' / ' + subtitle
        count = volumeInfo.get('pageCount')
        pages = '{:,}'.format(count) if count is not None else ''
        lines.append(line_fmt.format(idx, pages, title))

    return ''.join(lines)

def get_google_books_data(author, lang):
    # 著者名と言語指定から get を使って所定の URL にアクセスする。
    """ Fetches data from Google Books API """
    from requests import get

    books = []
    url = 'https://www.googleapis.com/books/v1/volumes'
    book_fields = (
        'items('
        'id'
        ',accessInfo(epub/isAvailable)'
        ',volumeInfo(title,subtitle,language,pageCount)'
        ')'
    )
    req_item_idx = 0  # Response is paginated
    req_item_cnt = 40  # Default=10, Max=40

    while True:
        params = {
            'q': 'inauthor:%s' % author,
            'startIndex': req_item_idx,
            'maxResults': req_item_cnt,
            'langRestrict': lang,
            'download': 'epub',
            'printType': 'books',
            'showPreorders': 'true',
            'fields': book_fields,
        }
        response = get(url, params=params)
        response.raise_for_status()
        book_items = response.json().get('items', None)
        if book_items is None:
            break
        books += book_items
        if len(book_items) != req_item_cnt:
            break  # Last response page
        req_item_idx += req_item_cnt

    return books

# request = flask.request()
# result = get_ebooks_by_author("")

def write_ebooks_by_author(result):
  import pickle
  with open('/tmp/list.pickle', 'wb') as f:
    # list = [リストを定義]
    pickle.dump(result, f)
  #
  import pprint
  import codecs
  with codecs.open('/tmp/list.txt','w','shift_jis') as f:
    # utf_8
    # shift_jis
    s  = pprint.pformat(result)
    f.write(s)
  #
  #with open('/tmp/result.txt', mode='w') as f:
  #  f.write(result)
  #
  ########
  #
  # あらかじめ認証をとってあるプロジェクトのID
  #
  project_id = 'aerobic-factor-216914'
  #
  # Authenticate to GCS.
  # from google.colab import auth
  # -# import auth
  # -# auth.authenticate_user()
  #
  # Create the service client.
  from googleapiclient.discovery import build
  gcs_service = build('storage', 'v1')
  #
  # Generate a random bucket name to which we'll upload the file.
  # バケットをつくる。
  import uuid
  bucket_name = 'gcf-sample' + str(uuid.uuid1())
  #
  body = {
      'name': bucket_name,
      # For a full list of locations, see:
      # https://cloud.google.com/storage/docs/bucket-locations
      'location': 'us',
  }
  ###
  # あらかじめ認証していた名前bucketsを
  #
  gcs_service.buckets().insert(project=project_id, body=body).execute()
  # print('Done')
  #
  # あらかじめ作られているバケットの隣に、このバケットができました。
  # バケットがあるときには消すことができるようにするといいかも。
  #
  from googleapiclient.http import MediaFileUpload
  #
  media = MediaFileUpload('/tmp/list.txt', 
                          mimetype='text/plain',
                          resumable=True)
  request = gcs_service.objects().insert(bucket=bucket_name, 
                                         name='list.txt',
                                         media_body=media)
  response = None
  while response is None:
    # _ is a placeholder for a progress object that we ignore.
    # (Our file is small, so we skip reporting progress.)
    _, response = request.next_chunk()
  #
  print('Upload complete')
  ########
#
