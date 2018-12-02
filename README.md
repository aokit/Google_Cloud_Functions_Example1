# Google_Cloud_Functions_Example1
Google クラウドの functions の例題を見つけてきてやってみた。

Google Cloud Functions 面白いと思って、自分の Google Calendar の API に
アクセスして、特定の条件の日付を出力させてみようかな、と、思ったのだけれど
うまくやりかたがわからない。
httlib2がない、とかいっているけど、ソースコードの中で !pip が働かないし。

検索してみて近いことをやっているっぽい以下のURLに書いてあることをそのままやってみた。
https://medium.com/google-cloud/deploying-a-python-serverless-function-in-minutes-with-gcp-19dd07e19824

python 3.7 を選んで、ソースタブのコードのペインのなかの main.py のタブペインにソースコード（sample.py）の内容をコピペで書き込んだ。
requirements.txt のタブペインは、デフォルトのまま（以下）。

```
# Function dependencies, for example:
# package>=version
```

<image >

うまく動いたみたい。

Google Cloud Functions でもローカルファイルを作って使うことはできるみたい。
少なくとも、実行中はいったん書いたファイルは残ってくれている。残っているファイルを Google Cloud Storage に書き出してみた。
main.py
requirement.txt
を置いておきます。
