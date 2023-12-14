void setup() {
  Serial.begin(9600);
  Serial.setTimeout(100);
}

char board[3][3] = {
  {'-', '-', '-'},
  {'-', '-', '-'},
  {'-', '-', '-'}
};

String mode;
String action;
int coordX;
int coordY;
char turn;
int pushCount = 0;
int winsPlayerX = 0;
int winsPlayer0 = 0;

char player = '1', AI = '0';

void resetBoard() {
  for (int i = 0; i < 3; i++)
    for (int j = 0; j < 3; j++) 
      board[i][j] = '-';
}

void parse(String config) {
  config.replace("\r\n", "");
  config.replace("b'", "");
  config.replace("'", "");

  String key = "";
  String value = "";
  bool readKey = true;

  for (int i = 0; i < config.length(); i++) {
    char curr = config[i];

    if (curr != ';') {
      if (curr == '\n') {
        if (key == "mode") mode = value;
        if (key == "action") action = value;
        if (key == "coordX") coordX = value.toInt();
        if (key == "coordY") coordY = value.toInt();
        if (key == "turn") turn = value[0];

        key = "";
        value = "";
      }

      if (readKey) {
        if (curr != '=') {
          key += curr;
        } else {
          readKey = false;
        }
      } else {
        if (curr != '\n') 
          value += curr;
        else readKey = true;
      }
    }
  }
}

String generateConfig() {
  String config = "";

  return config;
}

bool checkWin() {
  // row
  for (int i = 0; i < 3; i++) {
    if (board[0][i] == board[1][i] && board[0][i] == board[2][i] && board[0][i] != '-') {
      return true;
    }
  }

  // col
  for (int i = 0; i < 3; i++) {
    if (board[i][0] == board[i][1] && board[i][0] == board[i][2] && board[i][0] != '-') {
      return true;
    }
  }

  // first diagonal
  if (board[0][0] == board[1][1] && board[0][0] == board[2][2] && board[0][0] != '-') {
    return true;
  }

  // second diagonal
  if (board[0][2] == board[1][1] && board[1][1] == board[2][0] && board[0][2] != '-') {
    return true;
  }

  return false;
}

// ---- AI START

struct Move 
{ 
    int row, col; 
};

bool isMovesLeft() 
{ 
    for (int i = 0; i<3; i++) 
        for (int j = 0; j<3; j++) 
            if (board[i][j]=='-') 
                return true; 
    return false; 
} 
  
int evaluate() 
{ 
    // Checking for Rows for X or O victory. 
    for (int row = 0; row<3; row++) 
    { 
        if (board[row][0]==board[row][1] && 
            board[row][1]==board[row][2]) 
        { 
            if (board[row][0]==AI) 
                return +10; 
            else if (board[row][0]==player) 
                return -10; 
        } 
    } 
  
    for (int col = 0; col<3; col++) 
    { 
        if (board[0][col]==board[1][col] && 
            board[1][col]==board[2][col]) 
        { 
            if (board[0][col]==AI) 
                return +10; 
  
            else if (board[0][col]==player) 
                return -10; 
        } 
    } 
  
    if (board[0][0]==board[1][1] && board[1][1]==board[2][2]) 
    { 
        if (board[0][0]==AI) 
            return +10; 
        else if (board[0][0]==player) 
            return -10; 
    } 
  
    if (board[0][2]==board[1][1] && board[1][1]==board[2][0]) 
    { 
        if (board[0][2]==AI) 
            return +10; 
        else if (board[0][2]==player) 
            return -10; 
    } 
  
    // Else if none of them have won then return 0 
    return 0; 
} 
  
int minimax(int depth, bool isMax) 
{ 
    int score = evaluate(); 
  
    // If Maximizer has won the game return his/her 
    // evaluated score 
    if (score == 10) 
        return score; 
  
    // If Minimizer has won the game return his/her 
    // evaluated score 
    if (score == -10) 
        return score; 
  
    // If there are no more moves and no winner then 
    // it is a tie 
    if (isMovesLeft()==false) 
        return 0; 
  
    // If this maximizer's move 
    if (isMax) 
    { 
        int best = -1000; 
  
        // Traverse all cells 
        for (int i = 0; i<3; i++) 
        { 
            for (int j = 0; j<3; j++) 
            { 
                // Check if cell is empty 
                if (board[i][j]=='-') 
                { 
                    // Make the move 
                    board[i][j] = AI; 
  
                    // Call minimax recursively and choose 
                    // the maximum value 
                    int val = minimax(depth+1, !isMax);
                    if (val > best)
                      best = val;
                         
  
                    // Undo the move 
                    board[i][j] = '-'; 
                } 
            } 
        } 
        return best; 
    } 
  
    // If this minimizer's move 
    else
    { 
        int best = 1000; 
  
        // Traverse all cells 
        for (int i = 0; i<3; i++) 
        { 
            for (int j = 0; j<3; j++) 
            { 
                // Check if cell is empty 
                if (board[i][j]=='-') 
                { 
                    // Make the move 
                    board[i][j] = player; 
   
                    int val = minimax(depth+1, !isMax); 
                    if (val < best)
                      best = val; 
                           
  
                    // Undo the move 
                    board[i][j] = '-'; 
                } 
            } 
        } 
        return best; 
    } 
} 
  
// This will return the best possible move for the player 
struct Move findBestMove() 
{ 
    int bestVal = -1000; 
    Move bestMove; 
    bestMove.row = -1; 
    bestMove.col = -1; 
  
    for (int i = 0; i<3; i++) 
    { 
        for (int j = 0; j<3; j++) 
        { 
            // Check if cell is empty 
            if (board[i][j]=='-') 
            { 
                board[i][j] = AI; 
  
                int moveVal = minimax(0, false); 
  
                // Undo the move 
                board[i][j] = '-'; 
  
                if (moveVal > bestVal) 
                { 
                    bestMove.row = i; 
                    bestMove.col = j; 
                    bestVal = moveVal; 
                } 
            } 
        } 
    } 
    return bestMove; 
} 

// ---- AI END

void loop() {
  String config = "";
  bool isWinner = false;
  
  while(true) {
    if (Serial.available() > 0) {
      config += Serial.readString();
      if (config[config.length() - 1] == ';') break;
    }
  }

  parse(config);

  if (action == "PUSH") {
    if (mode == "PvsP" || mode == "PvsAI") {
      board[coordY][coordX] = turn;
      pushCount++;
      isWinner = checkWin();
    }
  } 
  else if (action == "RESET" || action == "CHANGE_MODE") {
    resetBoard();
    winsPlayerX = 0;
    winsPlayer0 = 0;
    pushCount = 0;
  } 
  else if (action == "CONTINUE") {
    resetBoard();
    pushCount = 0;
  }  
  else if (action == "GET_AI_PUSH") {
    if (mode == "AIvsAI") {
      if (pushCount % 2 == 0) {
        player = '0', AI = '1';
      } else {
        player = '1', AI = '0';
      }

      Move bestMove = findBestMove();
      pushCount++;
      board[bestMove.row][bestMove.col] = AI;
      turn = AI;
      isWinner = checkWin();
      Serial.println("coordX=" + String(bestMove.col) + String("\ncoordY=") + String(bestMove.row)  + String("\n"));
    } 
    else {
      Move bestMove = findBestMove();
      pushCount++;
      board[bestMove.row][bestMove.col] = '0';
      turn = '0';
      isWinner = checkWin();
      Serial.println("coordX=" + String(bestMove.col) + String("\ncoordY=") + String(bestMove.row)  + String("\n"));
    }
  }

  if (isWinner == false && pushCount > 8) { // is draw
    Serial.println("status=DRAW;");
    pushCount = 0;
  }

  if (isWinner == true) {
    if (turn == '0') {
      winsPlayer0++;
    } else {
      winsPlayerX++;
    }
    Serial.println("status=END\nwinner=" + String(turn) + String("\nwinsPlayerX=") + String(winsPlayerX) + String("\nwinsPlayer0=") + String(winsPlayer0) + String(";"));
    pushCount = 0;
  } 

  if (isWinner == false && pushCount < 9) {
    Serial.println("status=IN_PROCESS" + String(";"));
  }
}
