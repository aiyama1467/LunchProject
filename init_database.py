import sqlite3

connection = sqlite3.connect('db.sqlite3')
c = connection.cursor()

allergies = ['卵', '乳', 'そば', '小麦', '落花生', 'エビ', 'かに',
             'あわび', 'いか', 'いくら', 'さく', 'さば', 'くるみ',
             'ゼラチン', '大豆', 'まつたけ', 'やまいも', '牛肉',
             '豚肉', '鶏肉', 'オレンジ', 'キウイフルーツ', 'もも',
             'バナナ', 'リンゴ', 'ゴマ', 'カシューナッツ']

genres = ['和食', '洋食', '肉', '魚', '野菜', 'フルーツ',
          'デザート', '麺', '丼', '主菜', '副菜', 'ごはん', '汁物']


c.executemany('INSERT INTO menu_proposal_allergies VALUES (?, ?)', enumerate(allergies))
c.executemany('INSERT INTO menu_proposal_genres VALUES (?, ?)', enumerate(genres))


connection.commit()

connection.close()
