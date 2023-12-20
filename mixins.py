from lib import g_types, constants


class CopyBoardMixin:
  def copy_board(self):
    copied_board = []
    for row in self.board:
      copied_row = []
      for square in row:
        # Deep copy each Square instance in the board
        copied_square = square.copy()
        copied_row.append(copied_square)
      copied_board.append(copied_row)
    return copied_board


class GameplayMixin:
  def move_piece(self, obj_1, obj_2, **kwargs):
    piece_to_remove = None

    if obj_2.piece == None or obj_2.piece.turn != obj_1.piece.turn:
      is_legal = False

      for move in obj_1.piece.moves:
        is_legal = move.check(obj_1, obj_2, game=self)

        if is_legal:
          print(f"{move}: {obj_1} to {obj_2}" )
          break
      
      if is_legal:
        temp_board = self.copy_board()

        piece_to_move   = obj_1.remove_piece()
        piece_to_remove = obj_2.add_piece(piece_to_move)

        if self.pre_action != None:
          self.pre_action()
          self.pre_action = None

        # check if move exposes king of current player
        turn = piece_to_move.turn
        other = "white" if turn == "black" else "black"

        if len(self.fchecker(self.king_tiles[turn])) > 0:
          self.board = temp_board
          self.print_board()
          # self.fchecker(self.king_tiles[turn])

          self.play_sound("illegal")

        else:
          piece_to_move.num_of_moves += 1
          self.moves_count = self.moves_count + 1

          if self.post_action != None:
            self.post_action()
            self.post_action = None

          self.play_sound("capture") if piece_to_remove else self.play_sound("move")

          if len(self.fchecker(self.king_tiles[other])):
            self.play_sound("check")

    return piece_to_remove


  def add_to_played(self, square):
    self.should_highlight = True

    if len(self.playing) == 0 :
      if square.piece != None and square.piece.turn == self.turn:
        self.playing.append(square)

        return
      
      self.should_highlight = False
      self.playing.clear()


    elif len(self.playing) == 1:
      if square.piece != None and self.playing[0].piece.turn == square.piece.turn:
        self.playing.clear()

      self.playing.append(square)
      return
    
    self.playing.clear()


  def update(self):
    if len(self.playing) > 1:
      self.move_piece(*self.playing)
      self.should_highlight = False
      self.playing.clear()


  def print_board(self):
    string = ""
    c = 0
    while c < 8: 
      r = 0
      while r < 8:
        piece =  self.board[r][c].piece
        if piece:
          if piece.ptype == g_types.PieceType.KING:
            self.king_tiles = self.board[r][c]
          p = f" {piece.notation} "
        else:
          p = " - "
        string += p
        r += 1
      string += "\n"
      c += 1

    print(string)


  def fchecker(self, king_square):   
    [ i.set_highlight(None) for k, i in self.king_tiles.items() ]

    for i in self.selected:
      i.set_highlight(None)

    self.selected = []

    def func(step_count, tuple_to_check , x = None, y = None, ):
      cord  = (
        x if x is not None and x >= 0 else king_square.x, 
        y if y is not None and y >= 0 else king_square.y
      )
      square = self.get_square(*cord)
      square.highlight = None

      if square.piece != None:
        if square.piece.turn == king_square.piece.turn:
          return True
        
        elif square.piece.ptype not in tuple_to_check:
          return True

        
        elif step_count == 1 and square.piece.ptype in tuple_to_check[:2]:
          if square.piece.ptype == g_types.PieceType.PAWN:

            dir = -1 if square.piece.turn == "black" else 1
            if king_square.y - square.y != dir:
              self.selected.append(square)
              return True
            
          else:
            self.selected.append(square)
          return True
        
        elif square.piece.turn != king_square.piece.turn and square.piece.ptype in tuple_to_check[:2]:
          return True
        
        elif square.piece.ptype in tuple_to_check[2:]:
          self.selected.append(square)
          return True
        
      return False

    track = [ False ] * 8
    
    step_count = 1

    straights = [g_types.PieceType.KING, g_types.PieceType.KING, g_types.PieceType.QUEEN, g_types.PieceType.ROOK ]
    diagonals = [g_types.PieceType.PAWN, g_types.PieceType.KING, g_types.PieceType.QUEEN, g_types.PieceType.BISHOP ]

    while False in track:
      ypos = king_square.y + step_count
      xpos = king_square.x + step_count
      yneg = king_square.y - step_count
      xneg = king_square.x - step_count 

      # straights
      if not track[0] and ypos < 8:
        track[0] = func(step_count, straights, y=ypos)
      else:
        track[0] = True

      if not track[1] and yneg >= 0:
        track[1] = func(step_count, straights, y=yneg)
      else:
        track[1] = True

      if not track[2] and xpos < 8:
        track[2] = func(step_count, straights, x=xpos)
      else:
        track[2] = True
        
      if not track[3] and xneg >= 0:
        track[3] = func(step_count, straights, x=xneg)
      else:
        track[3] = True


      # diagonals 
      if not track[4] and ypos < 8 and xpos < 8:
        track[4] = func(step_count, diagonals, x=xpos, y=ypos)
      else:
        track[4] = True

      if not track[5] and yneg >= 0 and xneg >= 0:
        track[5] = func(step_count, diagonals, x=xneg, y=yneg)
      else:
        track[5] = True

      if not track[6] and xpos < 8 and yneg >= 0 :
        track[6] = func(step_count, diagonals, x=xpos, y=yneg)
      else:
        track[6] = True
        
      if not track[7] and xneg >= 0 and ypos < 8:
        track[7] = func(step_count, diagonals, x=xneg, y=ypos)
      else:
        track[7] = True

      step_count += 1

    # check_knights
    squares = [
      [1, 2], [1, -2], [2, 1], [2, -1],
      [-1, -2], [-1, 2], [-2, 1], [-2, -1]
    ]

    for cords in squares:
      square = self.get_square(king_square.x + cords[0], king_square.y + cords[1])
      if square is None :
        continue
      
      if square.piece == None:
        square.highlight = None
        continue

      if square.piece.turn != king_square.piece.turn and square.piece.ptype == g_types.PieceType.KNIGHT:
        self.selected.append(square)


    for i in self.selected:
      i.set_highlight(constants.SQUARE_HIGHLIGHT)

      print("check at: ", i)
    
    if len(self.selected):
      king_square.set_highlight(constants.SQUARE_HIGHLIGHT)

    return self.selected