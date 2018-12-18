import sys
import urllib
from socketserver import ThreadingMixIn
from http.server import HTTPServer
from http.server import CGIHTTPRequestHandler
import json


def wrong_parameters(self):
    out = {'bad': "Spatne parametry"}
    json_string = str(json.dumps(out))
    json_string = bytes(json_string, 'utf-8')

    self.send_response(200)
    self.send_header('Content-Type', 'application/json')
    self.end_headers()
    self.wfile.write(json_string)


def check_board(board):
    players = [1, 2]
    for p in players:
        #  RADKY
        if board[0][0] == p and board[0][1] == p and board[0][2] == p:
            return p
        if board[1][0] == p and board[1][1] == p and board[1][2] == p:
            return p
        if board[2][0] == p and board[2][1] == p and board[2][2] == p:
            return p

        #  SLOUPCE
        if board[0][0] == p and board[1][0] == p and board[2][0] == p:
            return p
        if board[0][1] == p and board[1][1] == p and board[2][1] == p:
            return p
        if board[0][2] == p and board[1][2] == p and board[2][2] == p:
            return p

        #  DIAGONALY
        if board[0][0] == p and board[1][1] == p and board[2][2] == p:
            return p
        if board[2][0] == p and board[1][1] == p and board[0][2] == p:
            return p

    flat_board = [item for sublist in board for item in sublist]
    if flat_board.count(0) == 0:
        return 0
    else:
        return -1


def new_game(self, dict, params):
    try:
        if len(dict) == 0:
            id = 1
        else:
            ids = list(dict.keys())
            id = max(ids) + 1

        name = "" if len(params) == 0 else params['name'][0]

        created_game = {"name": name,
                        "board": [[0, 0, 0] for _ in range(3)],
                        "next": 1,
                        "winner": -1}

        dict[id] = created_game

        json_string = str(json.dumps({"id": id}))
        json_string = bytes(json_string, 'utf-8')

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json_string)
    except:
        wrong_parameters(self)


def status_game(self, dict, params):

    try:
        try:
            game_id = int(params["game"][0])
            game = dict[game_id]
        except:
            self.send_error(404, 'Game not found')
            return

        out = {}

        if game["winner"] != -1:
            out["winner"] = game["winner"]
        else:
            out["board"] = game["board"]
            out["next"] = game["next"]

        json_string = str(json.dumps(out))
        json_string = bytes(json_string, 'utf-8')

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json_string)
    except:
        wrong_parameters(self)


def play_game(self, dict, params):

    try:
        try:
            game_id = int(params["game"][0])
            game = dict[game_id]
        except:
            self.send_error(404, 'Game not found')
            return

        player = int(params["player"][0])
        x = int(params["x"][0])
        y = int(params["y"][0])

        out = {}

        if not (game["winner"] == -1):
            if game['winner'] == 0:
                winner = "nikdo (remiza)"
            else:
                winner = 'hrac cislo ' + str(game['winner'])
            out["message"] = "Hra skoncila, vitezem je: " + winner + "\nnelze dale hrat!"
            out["status"] = "bad"

        elif not player == game["next"]:
            out["message"] = "Hrac " + str(player) + " neni na rade!"
            out["status"] = "bad"

        elif x < 0 or x > 2 or y < 0 or y > 2:
            out["message"] = "Mimo rozsah hraciho pole!"
            out["status"] = "bad"

        elif not game["board"][x][y] == 0:
            out["message"] = "Pole je jiz obsazeno!"
            out["status"] = "bad"

        else:
            game["board"][x][y] = player
            game["winner"] = check_board(game["board"])
            out["status"] = "ok"

            if player == 1:
                game["next"] = 2
            elif player == 2:
                game["next"] = 1

        json_string = str(json.dumps(out))
        json_string = bytes(json_string, 'utf-8')

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json_string)
    except:
        wrong_parameters(self)


def list_games(self, dict):

    try:
        dataForJson = []

        for id, game in dict.items():
            game_dict = {"id": id,
                         "name": game['name']}
            dataForJson.append(game_dict)

        json_string = str(json.dumps(dataForJson))
        json_string = bytes(json_string, 'utf-8')

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json_string)
    except:
        wrong_parameters(self)


def create_handler():

    dict = {}

    class Handler(CGIHTTPRequestHandler):

        def do_GET(self):
            request_path = urllib.parse.urlparse(self.path).path
            params = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(params)
            if request_path == "/start" or request_path == "/start/":
                new_game(self, dict, params)

            elif request_path == "/status" or request_path == "/status/":
                status_game(self, dict, params)

            elif request_path == "/play" or request_path == "/play/":
                play_game(self, dict, params)

            elif request_path == "/list" or request_path == "/list/":
                list_games(self, dict)

            else:
                out = {"bad": "Nespravny dotaz"}
                json_string = str(json.dumps(out))
                json_string = bytes(json_string, 'utf-8')

                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json_string)

    return Handler


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    pass


def main():
    port = int(sys.argv[1])

    handler = create_handler()

    server = ThreadedHTTPServer(('127.0.0.1', port), handler)

    server.serve_forever()

main()

