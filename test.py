from requests import get, post, delete, put
from pprint import pprint

'''Тест пользователей'''
print('Тест модели пользователя')
print()

pprint(get('http://localhost:8080/users').json())

print(post('http://localhost:8080/users',
           json={'user_name': 'Заголовок'}).json())
print(post('http://localhost:8080/users',
           json={'user_name': 'user1',
                 'password': 'pass1'}).json())

print(post('http://localhost:8080/users',
           json={'user_name': 'testuser',
                 'password': 'testpass',
                 'email': 'test@mail.ru'}).json())

pprint(get('http://localhost:8080/users').json())

pprint(get('http://localhost:8080/users/1').json())
pprint(get('http://localhost:8080/users/9').json())

print(put('http://localhost:8080/users/5',
          json={'user_name': 'testuser1'}).json())

print(put('http://localhost:8080/users/5',
          json={'email': 'testmail@mail.ru'}).json())

print(put('http://localhost:8080/users/1',
          json={}).json())

pprint(get('http://localhost:8080/users').json())

print(delete('http://localhost:8080/users/15').json())
print(delete('http://localhost:8080/users/5').json())

pprint(get('http://localhost:8080/users').json())

'''Тест модели игр'''

print()
print('Тест модели игр')
print()

pprint(get('http://localhost:8080/games').json())

pprint(get('http://localhost:8080/game/1').json())
pprint(get('http://localhost:8080/game/14').json())
