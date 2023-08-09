from pymongo import MongoClient

client = MongoClient("localhost", 27017)
db = client.dbjungle

def delete_existing_data():
    db.users.delete_many({})
    db.items.delete_many({})

def insert_initial_data():
    user_data = [
        {
            '_id' : 1,
            'user_id': 'song',
            'password' : 'song',
            'name': '송원',
            'friend': [2, 3],
            'my_item': [1],
            'received_item': [2, 3, 4, 5],
            'image' : 'https://i.pinimg.com/originals/a7/ee/b8/a7eeb85a1d27390ebdf770f8cf31e434.jpg',
            'mail' : 'bae@naver.com'
        },
        {
            '_id' : 2,
            'user_id': 'won',
            'password' : 'won',
            'name': '두번째 사용자',
            'friend': [1, 3],
            'my_item': [2],
            'received_item': [1, 3, 4, 5],
            'image' : 'https://mblogthumb-phinf.pstatic.net/MjAyMDA2MTBfMTY1/MDAxNTkxNzQ2ODcyOTI2.Yw5WjjU3IuItPtqbegrIBJr3TSDMd_OPhQ2Nw-0-0ksg.8WgVjtB0fy0RCv0XhhUOOWt90Kz_394Zzb6xPjG6I8gg.PNG.lamute/user.png?type=w800',
            'mail' : 'go@naver.com'
        },
        {
            '_id' : 3,
            'user_id': 'kim',
            'password' : 'kim',
            'name': '삼번',
            'friend': [1, 2],
            'my_item': [3,4,5],
            'received_item': [1,2],
            'image' : 'https://mblogthumb-phinf.pstatic.net/MjAyMDA2MTBfMTY1/MDAxNTkxNzQ2ODcyOTI2.Yw5WjjU3IuItPtqbegrIBJr3TSDMd_OPhQ2Nw-0-0ksg.8WgVjtB0fy0RCv0XhhUOOWt90Kz_394Zzb6xPjG6I8gg.PNG.lamute/user.png?type=w800',
            'mail' : 'pa@naver.com'
        }
    ]
    
    item_data = [
        {
            '_id': 1,
            'owner' : 1,
            'item_name': '사과',
            'price': 110000,
            'total_funding': 0,
            'd-day': '2023-12-31',
            'description': '맛있는사과',
            'img_url': 'http://thumbnail7.coupangcdn.com/thumbnails/remote/230x230ex/image/vendor_inventory/122e/9955ffdf377f1c42ab4b3f5c8c4d443124fe8f64d74878b28dcd26108c28.jpg',
            'achievement_rate': 0,
        },
        {
            '_id': 2,
            'owner' : 2,
            'item_name': '바나나',
            'price': 210000,
            'total_funding': 0,
            'd-day': '2023-12-31',
            'description': 'ㅋ_ㅋ',
            'img_url': 'http://thumbnail7.coupangcdn.com/thumbnails/remote/230x230ex/image/vendor_inventory/122e/9955ffdf377f1c42ab4b3f5c8c4d443124fe8f64d74878b28dcd26108c28.jpg',
            'achievement_rate': 0,
        },
        {
            '_id': 3,
            'owner' : 3,
            'item_name': '선인장',
            'price': 41000,
            'total_funding': 0,
            'd-day': '2023-12-31',
            'description': '배고파',
            'img_url': 'http://thumbnail7.coupangcdn.com/thumbnails/remote/230x230ex/image/vendor_inventory/122e/9955ffdf377f1c42ab4b3f5c8c4d443124fe8f64d74878b28dcd26108c28.jpg',
            'achievement_rate': 0,
        },
        {
            '_id': 4,
            'owner' : 3,
            'item_name': '튀김소보로',
            'price': 3000,
            'total_funding': 0,
            'd-day': '2023-12-31',
            'description': '맛있는튀소',
            'img_url': 'http://thumbnail7.coupangcdn.com/thumbnails/remote/230x230ex/image/vendor_inventory/122e/9955ffdf377f1c42ab4b3f5c8c4d443124fe8f64d74878b28dcd26108c28.jpg',
            'achievement_rate': 0,
        },
        {
            '_id': 5,
            'item_name': '우유',
            'owner' : 3,
            'price': 59000,
            'total_funding': 0,
            'd-day': '2023-12-31',
            'description': '맛있는우유',
            'img_url': 'http://thumbnail7.coupangcdn.com/thumbnails/remote/230x230ex/image/vendor_inventory/122e/9955ffdf377f1c42ab4b3f5c8c4d443124fe8f64d74878b28dcd26108c28.jpg',
            'achievement_rate': 0,
        }
    ]

    db.users.insert_many(user_data)
    db.items.insert_many(item_data)
