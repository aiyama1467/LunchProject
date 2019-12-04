import sqlite3

connection = sqlite3.connect('db.sqlite3')
c = connection.cursor()

allergies = ['卵（Egg）', '乳（Milk）', 'そば（Buckwheat）', '小麦（Wheat）', '落花生（Peanut）', 'エビ（Shrimp）', 'かに（Crab）',
             'あわび（Abalone）', 'いか（Squid）', 'いくら（Salmon roe）', 'さけ（Salmon）', 'さば（Mackerel）', 'くるみ（Walnut）',
             'ゼラチン（Gelatin）', '大豆（Soybean）', 'まつたけ（Matsutake mushroom）', 'やまいも（Yam）', '牛肉（Beef）',
             '豚肉（Pork）', '鶏肉（Chicken）', 'オレンジ（Orange）', 'キウイフルーツ（Kiwi fruit）', 'もも（Peach）',
             'バナナ（Banana）', 'リンゴ（Apple）', 'ゴマ（Sesame）', 'カシューナッツ（Cashew nut）']

genres = ['和食（Japanese food）', '洋食（Western food）', '肉（Meat）', '魚（Fish）', '野菜（Vegetables）', 'フルーツ（Fruits）',
          'デザート（Dessert）', '麺（Noodles）', '丼（Bowl）', '主菜（Main dish）', '副菜（Side dish）', 'ごはん（Rice）', '汁物（Soup）']


c.executemany('INSERT INTO menu_proposal_allergies VALUES (?, ?)',
              enumerate(allergies))
c.executemany('INSERT INTO menu_proposal_genres VALUES (?, ?)',
              enumerate(genres))


connection.commit()

connection.close()
