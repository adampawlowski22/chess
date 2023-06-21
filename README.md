# chess by Adam Pawlowski

## instalation

```dupa```

## usage of ChessAI class

```
from oop_train import ChessAI
chess_ai = ChessAI()
chess_ai.load_model("chess_model.h5")
board = chess_ai.random_board(max_depth=100)
move = chess_ai.predict_move(board)
print(move)
```

