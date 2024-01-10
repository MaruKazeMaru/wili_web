# wili_web
## 概要
WiLIのなくしもの位置推定機能や各種パラメータの確認をブラウザから行うためのwebアプリケーションです。<br>
WiLIとはなくしもの位置推定用のプログラム群です。詳細は近日中に[wili_documents](https://github.com/MaruKazeMaru/wili_documents)に書きます。<br>
webアプリケーションのフレームワークにFlaskを使っています。


## 依存
### pythonパッケージ
* Flask
* NumPy
* matplotlib
* Pillow
* wilitools
  * なくしもの位置推定、各種パラメータのDBへの保存が可能<br>
  * GitHubのリポジトリ：[wilitools](https://github.com/MaruKazeMaru/wilitools)

### その他
* SQLite3


## webアプリの起動方法
### 準備
間取りの画像等を保管するためのディレクトリを作成します。場所はどこでも構いません。<br>
次に本リポジトリのルートディレクトリ直下にconsts.pyというファイルを作成し、以下のように起動に必要な事項を書き込みます。
```python
MEDIA_ROOT_DIR = 'XXXXXXXXX'
STATIC_ROOT_DIR = 'XXXXXXXXX'
TEMPLATE_ROOT_DIR = 'XXXXXXXXX'
DB_PATH = 'XXXXXXXXX'
```
各変数は以下の通りです。
|||
|:--|:--|
|MEDIA_ROOT_DIR    |間取りの画像など利用者依存のメディアファイルを保存するディレクトリのパス|
|STATIC_ROOT_DIR   |CSS等の静的ファイルを保存するディレクトリのパス|
|TEMPLATE_ROOT_DIR |HTMLを保存するディレクトリのパス|
|DB_PATH           |WiLIの各種パラメータが保存されたSQLite3のDBファイルのパス|


### サーバを起動
WSGI対応のwebサーバにWSGIでapp.pyのappというインスタンスを接続します。
例えばwebサーバとしてGunicornを使う場合は以下のコマンドで起動します。
```shell
gunicorn app:app
```


## ライセンス
MITライセンスです。<br>
[LICENSE](./LICENSE)をお読みください。
