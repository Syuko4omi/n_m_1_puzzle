import random
import numpy as np
import tensorflow as tf
import copy

def tensor_to_array(tf_array):
    sess = tf.Session()
    a = sess.run(tf_array)
    b = a.tolist()
    return b

def only_show_next_board(board, num, player):
    cur = copy.deepcopy(board)
    stone_num = cur[7*player+num]
    if num < 0 or num > 5:
        return cur
    else:
        id = 7*player+num
        temp = cur[id]
        cur[id] = 0
        next_house = (id+1)%14
        while(temp > 0):
            if temp > 1:
                cur[next_house] += 1
                temp -= 1
                next_house = (next_house+1)%14
            else:
                if next_house == 7*player+6:
                    cur[next_house] += 1
                    temp -= 1
                elif 7*player <= next_house <= 7*player+5 and cur[next_house] == 0 and cur[12-next_house] != 0:
                    cur[7*player+6] += (1+cur[12-next_house])
                    cur[12-next_house] = 0
                    temp -= 1
                else:
                    cur[next_house] += 1
                    temp -= 1
                return cur

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
        opponent = 0 if player == 1 else 1
        if len(moveable) == 0:
            for i in range(6):
                self.board[7*opponent+6] += self.board[7*opponent+i]
                self.board[7*opponent+i] = 0
            return 0 #pass
        else:
            id = 7*player+num
            temp = self.board[id]
            self.board[id] = 0
            next_house = (id+1)%14
            check_flag = 0
            for i in range(6):
                if self.board[7*opponent+i] != 0:
                    check_flag = 1
            if check_flag == 1:
                while(temp > 0):
                    if temp > 1:
                        self.board[next_house] += 1
                        temp -= 1
                        next_house = (next_house+1)%14
                    else:
                        if next_house == 7*player+6:
                            self.board[next_house] += 1
                            temp -= 1
                            check_flag_dash = 0
                            for i in range(6):
                                if self.board[7*player+i] != 0:
                                    check_flag_dash = 1
                            if check_flag_dash == 1:
                                return 1 #continue player's turn
                            else:
                                for i in range(6):
                                    self.board[7*opponent+6] += self.board[7*opponent+i]
                                    self.board[7*opponent+i] = 0
                                return 0
                        elif 7*player <= next_house <= 7*player+5 and self.board[next_house] == 0 and self.board[12-next_house] != 0:
                            self.board[7*player+6] += (1+self.board[12-next_house])
                            self.board[12-next_house] = 0
                            temp -= 1
                            check_flag_dash = 0
                            for i in range(6):
                                if self.board[7*opponent+i] != 0:
                                    check_flag_dash = 1
                            if check_flag_dash == 1:
                                return 2 #ryoudori
                            else:
                                for i in range(6):
                                    self.board[7*player+6] += self.board[7*player+i]
                                    self.board[7*player+i] = 0
                                return 0
                        else:
                            self.board[next_house] += 1
                            temp -= 1
                            return 3 #normal
            else:
                for i in range(6):
                    self.board[7*player+6] += self.board[7*player+i]
                    self.board[7*player+i] = 0
                return 0 #pass


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

epsilon = tf.Variable(0.5)

with tf.compat.v1.Session() as sess:
    saver = tf.train.Saver()
    ckpt = tf.train.get_checkpoint_state('./')
    if ckpt:
        last_model = ckpt.model_checkpoint_path
        saver.restore(sess, last_model)
        print("successfully restored")
    else:
        sess.run(tf.global_variables_initializer())

    gamma = 0.9 #割引率
    episode_num = 13 #
    trial_num = 80 #各エピソードで何回移動を試すか

    for i in range(episode_num):
        print("episode", i)
        playout = Playout_Kalah()
        playouts = [] #一旦データを貯めておく
        for j in range(trial_num):
            if playout.is_finished():
                break
            player_name = playout.get_current_player()
            before_player_name = 1 if player_name == 1 else 0
            old_board = copy.deepcopy(playout.board)
            possible_choices = playout.list_houses_of_next_possible_move(player_name) #0~5が入る
            possible_choices = list(map(lambda x: 7*player_name+x, possible_choices)) #0~13が入る
            a = np.random.rand()
            next_action = 0 #どのハウスを選ぶか（0~13が入る）
            print(player_name)
            print(old_board)
            if a > sess.run(epsilon): #Q値に基づいて行動する場合
                [tensor_of_q] = sess.run(y, feed_dict = {X : [playout.board]})
                list_of_q = tensor_of_q.tolist()
                for k in range(14):
                    list_of_q[k] = [list_of_q[k], k]
                list_of_q.sort() #[Q値, house]がソートされて出てくる
                for k in range(14):
                    if list_of_q[13-k][1] in possible_choices:
                        next_action = list_of_q[13-k][1]
                        break
                #high_q = sess.run(tf.argmax(sess.run(y, feed_dict = {X : [pos]}), axis = 1))[0] #Q値の最も高い行動のindex
            else: #冒険する（ランダムに移動する）場合
                rand_move = np.random.randint(0, len(possible_choices))
                next_action = possible_choices[rand_move]
            new_board = only_show_next_board(playout.board, next_action-7*player_name, player_name)
            playout.move_stones(next_action-7*player_name, player_name)
            #max_next_q = γ*次の環境において最も高いQ値
            #max_next_qにおいては更新する前のネットワークを用いてQ値を計算するため、ここで計算しておく必要がある(Fixed Target Q-Network)
            max_next_q = tf.multiply(tf.constant(gamma), tf.reduce_max(sess.run(y, feed_dict = {X : [new_board]})))
            if playout.is_finished():
                #報酬のclipping(ゴールしたなら+1、そうでなければ+0)
                if before_player_name == playout.winner:
                    playouts.append([old_board, next_action, 1, new_board, max_next_q, 1]) #最後の1/0はfinish flag
                elif playout.winner == -1:
                    playouts.append([old_board, next_action, 0.5, new_board, max_next_q, 1])
                else:
                    playouts.append([old_board, next_action, -1, new_board, max_next_q, 1])
                playout = Playout_Kalah()
            else:
                if before_player_name == playout.get_current_player(): #手番が変化してたら次のターンで得られる報酬をマイナス
                    playouts.append([old_board, next_action, 0, new_board, max_next_q, 0]) #(s, a, r, s', max_next_q) 前から順に現在の環境,行動,報酬,新しい環境
                else:
                    playouts.append([old_board, next_action, 0, new_board, tf.multiply(tf.constant(-1, tf.float32), max_next_q), 0])

        epsilon = tf.math.maximum(tf.constant(0.1), tf.constant(0.99)*epsilon)

        random_index_list = [] #データをランダムな順番で取り出す
        L = [j for j in range(len(playouts))]
        for j in range(len(playouts)): #取り出す順番を決定
            cur = np.random.randint(0, len(playouts)-j)
            num = L[cur]
            random_index_list.append(num)
            L.pop(cur)
        for j in range(len(playouts)):
            print(j)
            cur = random_index_list[j]
            current_data = playouts[cur] #データの取り出し
            print(current_data)
            action_num = current_data[1] #どのハウスから移動させたか
            max_next_q = tf.constant(0, dtype = tf.float32)
            if current_data[5] == 0: #次の状態s'が終状態でなければmax_next_qを以前計算した値にする
                max_next_q = current_data[4]
            #(r+max_next_q-Q(s,a))^2を最小にするように学習. ここcurrent_data[2]をtf.float32に指定しないと型が合ってないぞって怒られが発生する
            train_step = tf.compat.v1.train.GradientDescentOptimizer(0.3).minimize(tf.reduce_sum(tf.square(tf.constant(current_data[2], dtype = tf.float32)+max_next_q-y[0][action_num])))
            sess.run(train_step, feed_dict={X : [current_data[0]]})
        print(sess.run(W_0))
        print(sess.run(W_1))
        print(sess.run(b_0))
        print(sess.run(b_1))
        if (i+1) % 5 == 0:
            saver = tf.train.Saver()
            saver.save(sess, "model.ckpt")

        if (i+1) % 5 == 0:
            DQN_0 = 0
            DQN_1 = 0
            RANDOM_0 = 0
            RANDOM_1 = 0
            DRAW = 0
            for j in range(100):
                playout = Playout_Kalah()
                while(True):
                    if playout.is_finished():
                        playout.show_board()
                        playout.show_score()
                        if playout.winner == -1:
                            print("DRAW")
                        else:
                            print("The winner is player", playout.winner)
                        if j%2 == 0:
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
                        if j%2 == 0:
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
            print("episode", i, "WIN:", DQN_0+DQN_1, [DQN_0, DQN_1], "LOSE:", RANDOM_1+RANDOM_0, [RANDOM_1, RANDOM_0], "DRAW:", DRAW)

    saver = tf.train.Saver()
    saver.save(sess, "model.ckpt")
