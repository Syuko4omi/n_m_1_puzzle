import tensorflow as tf
import numpy as np
import random

action = [[0,1], [0, -1], [1, 0], [-1, 0]] #右、左、下、上

def possible_moves(current_pos): #ある位置から次に動ける方向を返却
    L = []
    for i in range(4):
        next_y = current_pos[0]+action[i][0]
        next_x = current_pos[1]+action[i][1]
        if 0 <= next_y <= 2 and 0 <= next_x <= 2:
            L.append([action[i][0], action[i][1]])
    return L

def is_terminate(board): #ゴール判定（右上に到達したか？）
    if board == [0,2]:
        return 1
    else:
        return 0

#入力ベクトル（1*2行列、現在位置を表す）
X = tf.placeholder(tf.float32, shape = (1,2))

#重み
W = tf.Variable(tf.ones([2, 4], dtype=tf.float32))
b = tf.Variable(tf.zeros([4], dtype=tf.float32))

#ネットワーク
y = tf.nn.softmax(tf.matmul(X, W)+b)

with tf.compat.v1.Session() as sess:
    sess.run(tf.global_variables_initializer()) #これがないとWとかbが初期化されないので演算ができない

    gamma = 0.9 #割引率
    epsilon = 1 #冒険する確率
    goal_list = [] #各エピソードでゴールした回数
    episode_num = 2
    trial_num = 20 #各エピソードで何回移動を試すか

    for i in range(episode_num):
        pos = [2,0] #開始位置
        playouts = [] #一旦データを貯めておく
        goal_count = 0
        for j in range(trial_num):
            a = np.random.rand()
            next_action = [0,0] #上下左右の移動が入る
            if a > epsilon: #Q値に基づいて行動する場合
                high_q = sess.run(tf.argmax(sess.run(y, feed_dict = {X : [pos]}), axis = 1))[0] #Q値の最も高い行動のindex
                next_action = action[high_q]
                if 0 <= pos[0]+next_action[0] <= 2 and 0 <= pos[1]+next_action[1] <= 2:
                    None
                else: #Q値の最も高い方向へ移動できなかった場合（ランダムに移動）
                    actions_list = possible_moves(pos)
                    rand_move = np.random.randint(0, len(actions_list))
                    next_action = actions_list[rand_move]
            else: #冒険する（ランダムに移動する）場合
                actions_list = possible_moves(pos)
                rand_move = np.random.randint(0, len(actions_list))
                next_action = actions_list[rand_move]
            new_pos = [pos[0]+next_action[0], pos[1]+next_action[1]]
            #max_next_q = γ*次の環境において最も高いQ値
            #max_next_qにおいては更新する前のネットワークを用いてQ値を計算するため、ここで計算しておく必要がある(Fixed Target Q-Network)
            max_next_q = tf.multiply(tf.constant(gamma), tf.reduce_max(sess.run(y, feed_dict = {X : [new_pos]})))
            if new_pos == [0, 2]:
                #報酬のclipping(ゴールしたなら+1、そうでなければ+0)
                playouts.append([pos, next_action, 1, new_pos, max_next_q]) #(s, a, r, s', max_next_q) 前から順に現在の環境,行動,報酬,新しい環境
                pos = [2, 0] #場所をリセット
                goal_count += 1
            else:
                playouts.append([pos, next_action, 0, new_pos, max_next_q])
                pos = new_pos
        epsilon = max(0.5, epsilon*0.9)
        #Experience Replay
        random_index_list = [] #データをランダムな順番で取り出す
        L = [j for j in range(trial_num)]
        for j in range(trial_num): #取り出す順番を決定
            cur = np.random.randint(0, trial_num-j)
            num = L[cur]
            random_index_list.append(num)
            L.pop(cur)
        for j in range(trial_num):
            print(j)
            cur = random_index_list[j]
            current_data = playouts[cur] #データの取り出し
            action_num = 0 #上下左右のどの移動に対応するか
            for k in range(4):
                if current_data[1] == action[k]:
                    action_num = k
            max_next_q = tf.constant(0, dtype = tf.float32)
            if not is_terminate(current_data[3]): #次の状態s'が終状態でなければmax_next_qを以前計算した値にする
                max_next_q = current_data[4]
            #(r+max_next_q-Q(s,a))^2を最小にするように学習. ここcurrent_data[2]をtf.float32に指定しないと型が合ってないぞって怒られが発生する
            train_step = tf.compat.v1.train.GradientDescentOptimizer(0.1).minimize(tf.reduce_sum(tf.square(tf.constant(current_data[2], dtype = tf.float32)+max_next_q-y[0][action_num])))
            sess.run(train_step, feed_dict={X : [current_data[0]]})
        print(sess.run(W)) #[[0.83810943, 1.0185969,  0.9006581, 1.2426375],[1.0777256, 0.62253964, 0.56709814, 1.7326373]]
        print(sess.run(b)) #[0.69636935, -0.30203688, -0.3140987,  -0.0802336]
        goal_list.append(goal_count) #[2, 3, 2, 5, 0, 2, 5, 2, 2, 5, 2, 5, 3, 5, 2, 5, 2, 5, 5, 5]
        print("round", i, "goal:", goal_count)
    print(goal_list)
    saver = tf.train.Saver()
    saver.save(sess, "model.ckpt")

#import numpy as np
#W = np.matrix([[0.83810943, 1.0185969,  0.9006581, 1.2426375],[1.0777256, 0.62253964, 0.56709814, 1.7326373]])
#b = np.matrix([0.69636935, -0.30203688, -0.3140987,  -0.0802336])
#direction = ["right", "left", "down", "up"]
#for i in range(3):
#    for j in range(3):
#        X = np.array([[i, j]])
#        Q_value_list = (np.dot(X, W)+b)
#        print(Q_value_list, [i, j], direction[np.argmax(Q_value_list)])
#Q値,マス目,最もQ値の高い方向
#[[ 0.69636935 -0.30203688 -0.3140987  -0.0802336 ]] [0, 0] right    <- Q値,マス目,最もQ値の高い方向
#[[1.77409495 0.32050276 0.25299944 1.6524037 ]] [0, 1] right
#[[2.85182055 0.9430424  0.82009758 3.385041  ]] [0, 2] up
#[[1.53447878 0.71656002 0.5865594  1.1624039 ]] [1, 0] right
#[[2.61220438 1.33909966 1.15365754 2.8950412 ]] [1, 1] up
#[[3.68992998 1.9616393  1.72075568 4.6276785 ]] [1, 2] up
#[[2.37258821 1.73515692 1.4872175  2.4050414 ]] [2, 0] up
#[[3.45031381 2.35769656 2.05431564 4.1376787 ]] [2, 1] up
#[[4.52803941 2.9802362  2.62141378 5.870316  ]] [2, 2] up
