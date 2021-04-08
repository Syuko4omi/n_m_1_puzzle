import tkinter
from tkinter import messagebox
import random
import tensorflow as tf

class Kalah_Board():
    def __init__(self):
        L = []
        for i in range(6*2+2):
            L.append(4)
        L[6] = 0
        L[13] = 0
        self.board = L

    def move_stones(self, num, player):
        moveable = self.list_houses_of_next_possible_move(player)
        if len(moveable) == 0:
            opponent = 0
            if player == 0:
                opponent = 1
            else:
                opponent = 0
            for i in range(6):
                self.board[7*opponent+6] += self.board[7*opponent+i]
                self.board[7*opponent+i] = 0
            return 0 #pass
        else:
            id = 7*player+num
            temp = self.board[id]
            self.board[id] = 0
            next_house = (id+1)%14
            while(temp > 0):
                if temp > 1:
                    self.board[next_house] += 1
                    temp -= 1
                    next_house = (next_house+1)%14
                else:
                    if next_house == 7*player+6:
                        self.board[next_house] += 1
                        temp -= 1
                        return 1 #continue player's turn
                    elif 7*player <= next_house <= 7*player+5 and self.board[next_house] == 0 and self.board[12-next_house] != 0:
                        self.board[7*player+6] += (1+self.board[12-next_house])
                        self.board[12-next_house] = 0
                        temp -= 1
                        return 2 #ryoudori
                    else:
                        self.board[next_house] += 1
                        temp -= 1
                        return 3 #normal


    def show_board(self):
        print("  ", end = "")
        for i in range(6):
            print(self.board[12-i], end = " ")
        print("  ", end = "")
        print("\n", end = "")

        print(self.board[13], end = " ")
        for i in range(6):
            print("  ", end = "")
        print(self.board[6], end = "")
        print("\n", end = "")

        print("  ", end = "")
        for i in range(6):
            print(self.board[i], end = " ")
        print("  ", end = "")
        print("\n", end = "")

    def list_houses_of_next_possible_move(self, player): #player is 0 or 1
        non_null_houses = []
        for i in range(6):
            if self.board[7*player+i] != 0:
                non_null_houses.append(i)
        return non_null_houses


class Playout_Kalah(Kalah_Board):
    def __init__(self, turn = 0, start_player = 0):
        super().__init__()
        self.player = start_player
        self.turn = turn
        self.winner = None

    def is_finished(self):
        return self.winner is not None

    def list_houses_of_next_possible_move(self, player):
        return super().list_houses_of_next_possible_move(self.player)

    def get_current_player(self):
        return self.player

    def get_next_player(self):
        if self.player == 0:
            return 1
        else:
            return 0

    def shift_player(self):
        self.player = self.get_next_player()

    def move_stones(self, num, player):
        cur = super().move_stones(num, player)
        if cur == 0:
            return self.finish_game()
        else:
            if self.board[6] > 24 or self.board[13] > 24:
                return self.finish_game()
            else:
                if cur == 1:
                    self.turn += 1
                else:
                    self.player = self.get_next_player()
                    self.turn += 1

    def show_score(self):
        print("player 0", self.board[6])
        print("player 1", self.board[13])

    def finish_game(self):
        points_of_player_0 = self.board[6]
        points_of_player_1 = self.board[13]
        if points_of_player_0 > points_of_player_1:
            self.winner = 0
        elif points_of_player_0 < points_of_player_1:
            self.winner = 1
        else:
            self.winner = -1

        return self.winner

#入力ベクトル（1行14列、現在の盤面を表す）
X = tf.placeholder(tf.float32, shape = (1,14))

#重み
W_0 = tf.Variable(tf.truncated_normal([14, 32], dtype=tf.float32))
W_1 = tf.Variable(tf.truncated_normal([32, 14], dtype=tf.float32))
b_0 = tf.Variable(tf.zeros([32], dtype=tf.float32))
b_1 = tf.Variable(tf.zeros([14], dtype=tf.float32))

#ネットワーク(4層)
hidden_1 = tf.sigmoid(tf.nn.softmax(tf.matmul(X, W_0)+b_0))
y = tf.nn.softmax(tf.matmul(hidden_1, W_1)+b_1)

with tf.compat.v1.Session() as sess:
    saver = tf.train.Saver()
    ckpt = tf.train.get_checkpoint_state('./')
    if ckpt:
        last_model = ckpt.model_checkpoint_path
        saver.restore(sess, last_model)
        print("successfully restored")
    else:
        sess.run(tf.global_variables_initializer())

    DQN_0 = 0
    DQN_1 = 0
    RANDOM_0 = 0
    RANDOM_1 = 0
    DRAW = 0
    for i in range(10000):
        playout = Playout_Kalah()
        while(True):
            if playout.is_finished():
                #playout.show_board()
                #playout.show_score()
                if playout.winner == -1:
                    print("DRAW")
                else:
                    print("The winner is player", playout.winner)
                if i%2 == 0:
                    if playout.winner == 0:
                        DQN_0 += 1
                    elif playout.winner == 1:
                        RANDOM_1 += 1
                    else:
                        DRAW += 1
                else:
                    if playout.winner == 0:
                        RANDOM_0 += 1
                    elif playout.winner == 1:
                        DQN_1 += 1
                    else:
                        DRAW += 1
                break

            #playout.show_board()
            player_name = playout.get_current_player()
            possible_choices = playout.list_houses_of_next_possible_move(player_name)
            #print("player", player_name)
            if possible_choices == []:
                playout.move_stones(-1, player_name)
            else:
                if i%2 == 0:
                    if player_name == 0:
                        possible_choices = list(map(lambda x: 7*player_name+x, possible_choices))
                        next_action = 0
                        [tensor_of_q] = sess.run(y, feed_dict = {X : [playout.board]})
                        list_of_q = tensor_of_q.tolist()
                        for k in range(14):
                            list_of_q[k] = [list_of_q[k], k]
                        list_of_q.sort() #[Q値, house]がソートされて出てくる
                        for k in range(14):
                            if list_of_q[13-k][1] in possible_choices:
                                next_action = list_of_q[13-k][1]
                                break
                        playout.move_stones(next_action, 0)
                    else:
                        cur = random.randint(0, len(possible_choices)-1)
                        playout.move_stones(possible_choices[cur], 1)
                else:
                    if player_name == 0:
                        cur = random.randint(0, len(possible_choices)-1)
                        playout.move_stones(possible_choices[cur], 1)
                    else:
                        possible_choices = list(map(lambda x: 7*player_name+x, possible_choices))
                        next_action = 7
                        [tensor_of_q] = sess.run(y, feed_dict = {X : [playout.board]})
                        list_of_q = tensor_of_q.tolist()
                        for k in range(14):
                            list_of_q[k] = [list_of_q[k], k]
                        list_of_q.sort() #[Q値, house]がソートされて出てくる
                        for k in range(14):
                            if list_of_q[13-k][1] in possible_choices:
                                next_action = list_of_q[13-k][1]
                                break
                        playout.move_stones(next_action-7, 1)
    print("WIN:", DQN_0, DQN_1, "LOSE:", RANDOM_1, RANDOM_0, "DRAW:", DRAW)
