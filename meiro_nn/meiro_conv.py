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
W = tf.Variable(tf.truncated_normal([2, 4], dtype=tf.float32))
W_DASH = tf.Variable(tf.truncated_normal([4, 4], dtype=tf.float32)) #WとW_DASHがどちらも初期値オール1だとWとbが全く変化しなかった
b = tf.Variable(tf.zeros([4], dtype=tf.float32))
b_dash = tf.Variable(tf.zeros([4], dtype=tf.float32))

#ネットワーク
#y = tf.nn.softmax(tf.matmul(X, W)+b)
hidden_1 = tf.nn.tanh(tf.nn.softmax(tf.matmul(X, W)+b)) #重みにマイナスある時にrelu使うのはダメ
y = tf.nn.softmax(tf.matmul(hidden_1, W_DASH)+b_dash)

with tf.compat.v1.Session() as sess:
    sess.run(tf.global_variables_initializer()) #これがないとWとかbが初期化されないので演算ができない

    gamma = 0.9 #割引率
    epsilon = 1 #冒険する確率
    goal_list = [] #各エピソードでゴールした回数
    episode_num = 30
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
            #(r+max_next_q-Q(s,a))^2を最小にするように学習
            train_step = tf.compat.v1.train.GradientDescentOptimizer(1).minimize(tf.reduce_sum(tf.square(tf.constant(current_data[2], dtype = tf.float32)+max_next_q-y[0][action_num])))
            sess.run(train_step, feed_dict={X : [current_data[0]]})
        print(sess.run(W)) #[[ 0.08077717,  3.08161,    -1.4089478,  -0.05356812],[-0.04961805, -0.511309,    1.1895602,   0.13956545]]
        print(sess.run(W_DASH)) #[[ 1.7467699,  -0.8823008,   0.84874946,  1.5634651 ],[-1.4302096,  -0.22959879, -0.22891375,  1.5845747 ],[ 2.2296855,  -0.02334466, -0.09320528, -1.2810099 ],[ 0.5020116,  -1.842903,   -0.07275277,  0.6354583 ]]
        print(sess.run(b)) #[-0.1664129,   0.05462197,  0.6142375,  -0.5024468 ]
        print(sess.run(b_dash)) #[ 1.5636895, -0.5498089, -1.5310428,  0.517163 ]
        goal_list.append(goal_count)
        print("round", i, "goal:", goal_count)
    print(goal_list)


#import numpy as np
#W = np.matrix([[ 0.08077717,  3.08161,    -1.4089478,  -0.05356812],[-0.04961805, -0.511309,    1.1895602,   0.13956545]])
#W_DASH = np.matrix([[ 1.7467699,  -0.8823008,   0.84874946,  1.5634651 ],[-1.4302096,  -0.22959879, -0.22891375,  1.5845747 ],[ 2.2296855,  -0.02334466, -0.09320528, -1.2810099 ],[ 0.5020116,  -1.842903,   -0.07275277,  0.6354583 ]])
#b = np.matrix([-0.1664129,   0.05462197,  0.6142375,  -0.5024468 ])
#b_dash = np.matrix([ 1.5636895, -0.5498089, -1.5310428,  0.517163 ])
#direction = ["right", "left", "down", "up"]
#for i in range(3):
#    for j in range(3):
#        X = np.array([[i, j]])
#        Q_value_list = np.dot((np.dot(X, W)+b), W_DASH)+b_dash
#        print(Q_value_list, [i, j], direction[np.argmax(Q_value_list)])
#[[ 2.31220591  0.49609775 -1.70548516 -0.76259348]] [0, 0] right
#[[ 5.67922224  0.37229625 -1.75157986 -3.08552724]] [0, 1] right
#[[ 9.04623857  0.24849476 -1.79767455 -5.40846101]] [0, 2] right
#[[-5.12244546 -0.15109369 -2.20712988  6.01757582]] [1, 0] up
#[[-1.75542913 -0.27489518 -2.25322458  3.69464206]] [1, 1] up
#[[ 1.6115872  -0.39869667 -2.29931927  1.3717083 ]] [1, 2] right
#[[-12.55709683  -0.79828512  -2.7087746   12.79774513]] [2, 0] up
#[[-9.1900805  -0.92208661 -2.75486929 10.47481136]] [2, 1] up
#[[-5.82306418 -1.0458881  -2.80096399  8.1518776 ]] [2, 2] up
