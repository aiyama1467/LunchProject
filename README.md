# LunchProject
## データベースの初期化
makemigrations → migrateした後にアレルギーと好みを入れる
プログラムがあるので、使ってください

```
$ python init_database.py
```
で初期化できます。

## 昼食リストのデータベースへの入れ方
以下のコマンドを実行してください
```
$ sqlite3 db.sqlite3
sqlite> .separator ,
sqlite> .import output.csv menu_proposal_menu
sqlite> .import menu_genre.csv menu_proposal_menu_menu_genre
sqlite> .import menu_allergy.csv menu_proposal_menu_menu_allergies
sqlite> .quit
```
