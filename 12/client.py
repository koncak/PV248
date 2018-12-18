import sys
import json
import aiohttp
import asyncio
from time import sleep


async def fetch(session, url):
    async with session.get(url) as response:
        assert response.status == 200
        return await response.text()


def empty_board(board):
    flat_board = [item for sublist in board for item in sublist]
    return flat_board.count(0) == 9


def print_board(board):
    for i in range(3):
        for j in range(3):
            if board[i][j] == 0:
                print("_", end="", sep="")

            if board[i][j] == 1:
                print("x", end="", sep="")

            if board[i][j] == 2:
                print("o", end="", sep="")

        print("")


async def waiting(session, game_id, player):
    player_waiting = True
    printed = True

    while True:
        json_response = await fetch(session, 'http://' + str(sys.argv[1]) + ":" +
                                    str(sys.argv[2]) + "/status?game=" + str(game_id))
        json_data = json.loads(json_response)

        if "next" in json_data:
            if printed:
                print_board(json_data["board"])
                printed = False

            if int(json_data["next"]) == player:
                print_board(json_data["board"])
                await play(session, game_id, player)

        elif "winner" in json_data:
            if int(json_data["winner"]) == player:
                print("Vyhravas")

            elif int(json_data["winner"]) == 0:
                print("Remiza")

            else:
                print("Prohravas")
            exit(0)

        if player_waiting:
            print("Cekam na druheho hrace")
            player_waiting = False

        sleep(1)


async def list_games(json_data, session):
    if len(json_data) > 0:
        print("Seznam her:")

        for game in json_data:
            response = await fetch(session, 'http://' + str(sys.argv[1]) + ":" +
                                            str(sys.argv[2]) + "/status?game=" + str(game["id"]))
            json_data = json.loads(response)

            if "board" in json_data:
                if empty_board(json_data["board"]):
                    print("{} {}".format(game["id"], game["name"]))

        print("Zadejte id hry, nebo zalozte novou hru napsanim: new a stisknete Enter ", sep='', end='')
        game_id = input()
        return game_id

    else:
        print("Zadne volne hry. Zalozte novou hru napsanim: new a stisknete Enter")
        game_id = input()
        return game_id


async def play(session, game_id, player):

    while True:
        next_player = "x" if player == 1 else "o"
        print("Jsi na tahu ({}):".format(next_player))

        player_move = input()
        player_move = player_move.strip()
        player_move = player_move.split(" ")

        if len(player_move) == 2:
            first = player_move[0]
            second = player_move[1]

            try:
                first = int(first)
                second = int(second)
            except:
                print("Neplatny tah!")
                continue

            response = await fetch(session, 'http://' + str(sys.argv[1]) + ":" + str(sys.argv[2]) +
                                            "/play?game=" + str(game_id) + "&player=" + str(player) + "&x=" +
                                            str(first) + "&y=" + str(second))
            json_data = json.loads(response)

            if "status" in json_data:
                if not json_data["status"] == "bad":
                    break

        print("Neplatny tah!")

    await waiting(session, game_id, player)


async def main():
    host = str(sys.argv[1])
    port = int(sys.argv[2])

    async with aiohttp.ClientSession() as session:
        print("Uspesne pripojeni k hernimu serveru", host + ":" + str(port))

        while True:
            json_response = await fetch(session, 'http://' + host + ":" + str(port) + "/list")
            json_data = json.loads(json_response)

            game_id = await list_games(json_data, session)

            if game_id.strip().isnumeric():
                player = 2
                try:
                    json_response = await fetch(session, 'http://' + host + ":" + str(port)
                                                + "/status?game=" + str(game_id))
                    json_data = json.loads(json_response)

                    if empty_board(json_data["board"]):
                        print("Pripojen ke hre id {}".format(game_id))
                        await waiting(session, game_id, player)
                    else:
                        print("Pripojeni ke hre {} se nezdarilo.".format(game_id))

                except AssertionError:
                    print("Pripojeni se nezdarilo.")

            else:
                game_id = game_id.strip()
                game_id = game_id.split(" ", 1)

                if game_id[0] == "new":
                    if len(game_id) == 2:
                        name = game_id[1]
                    else:
                        name = ""

                    player = 1
                    json_response = await fetch(session, 'http://' + host + ":" + str(port) + "/start?name="+str(name))
                    json_data = json.loads(json_response)
                    game_id = json_data["id"]

                    print("Byla zalozena nova hra s id {}.".format(game_id))
                    print("___\n___\n___")

                    await play(session, game_id, player)
                    break
                else:
                    print("Nekorektni vstup!")


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
