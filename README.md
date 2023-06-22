# chess by *Adam Pawlowski*

## instalation

```
git clone https://github.com/adampawlowski22/chess.git
cd chess
pip3 install -r requirements.txt
python3 main.py
```

## example usage of ChessAI class

```
from oop_train import ChessAI
chess_ai = ChessAI()
chess_ai.load_model("chess_model.h5")
board = chess_ai.random_board(max_depth=100)
move = chess_ai.predict_move(board)
print(move)
```

## example usage of ChessGame class

```
chess_game = ChessGame()
chess_game.run()
```

