from player import Player
from bot import Bot

print('1.Player')
print('2.Bot')
CLIENTS = {
    1: Player,
    2: Bot
}
selected = int(input())
try:
    client = CLIENTS[selected]()
    client.run_server()
except Exception as e:
    print(e)
