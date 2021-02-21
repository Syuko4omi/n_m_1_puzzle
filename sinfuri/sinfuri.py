import numpy as np
import heapq
import itertools
import math
import matplotlib.pyplot as plt

#第一段階と第二段階をシミュレート
def gale_shapley(tentative_list, wished_list, capacity_list, score_list, n, k, steps, show_flag): #steps = 希望する数(第一段階は2回、第二段階は2*k+2回)
    counter = 0 #マッチングの回数
    T = tentative_list #現在の仮志望状況　[内定しているかどうかのフラグ, 仮内定先]を各要素に持つ
    W = wished_list #希望する学科の順番
    temp_list = [[0,0] for i in range(k)] #指定科類、全科類で現在埋まっている席の数
    current_wish_num = [0 for i in range(n)] #これから第何希望を見るか
    tentative_candidates = [] #各学科に内定している人の情報
    for i in range(k):
        selected_dep = []
        all_deps = []
        heapq.heapify(selected_dep)
        heapq.heapify(all_deps)
        tentative_candidates.append([selected_dep, all_deps])
    for i in range(steps):
        for j in range(n):
            while T[j][0] != True:
                if current_wish_num[j] > steps-1:
                    break
                else:
                    counter += 1
                    wish = wished_list[j][current_wish_num[j]] #wish = [希望する学科, 指定科類か全科類か]
                    if wish[0] == k: #どこにも行かないことを選択
                        T[j][0] = True
                        T[j][1] = k
                        break
                    if wish[1] == 'S': #指定科類
                        flag = 0
                    elif wish[1] == 'A': #全科類
                        flag = 1
                    if capacity_list[wish[0]][flag] == 0:
                        current_wish_num[j] += 1
                        continue
                    elif temp_list[wish[0]][flag] < capacity_list[wish[0]][flag]:
                        T[j][0] = True
                        T[j][1] = wish[0]
                        temp_list[wish[0]][flag] += 1
                        heapq.heappush(tentative_candidates[wish[0]][flag], score_list[j])
                    else:
                        if len(tentative_candidates[wish[0]][flag]) != 0:
                            t = heapq.heappop(tentative_candidates[wish[0]][flag])
                            if score_list[j][0] < t[0]:
                                current_wish_num[j] += 1
                                heapq.heappush(tentative_candidates[wish[0]][flag], t)
                            elif score_list[j][0] > t[0]:
                                heapq.heappush(tentative_candidates[wish[0]][flag], score_list[j])
                                T[j][0] = True
                                T[j][1] = wish[0]
                                T[t[1]][0] = False
                                T[t[1]][1] = -1
                                current_wish_num[t[1]] += 1
                        else:
                            current_wish_num[j] += 1
    if show_flag == 1:
        print("各学科の定員:" ,capacity_list)
        print("実際に何人が内定したか:", temp_list)
        print("最終的に第何希望まで見たのか:", current_wish_num)
        print("内定状況:")
        for i in range(n):
            print(tentative_list[i], score_list[i][0])
        print("学科別の内定状況:")
        for i in range(k):
            print(tentative_candidates[i])
        print("各学生の志望先:")
        for i in range(n):
            print(wished_list[i])
        print()
        show_flag = 0
    return T, counter

def capacity_of_each_departments(n, k): #学科の定員を決定
    total_capacity = []
    first_capacity = []
    second_capacity = [] #第一志望、第二志望それぞれ、指定科類枠と全科類枠で二つ用意
    temp = n
    total_capacity_of_i_th_department = 0
    for i in range(k):
        if i != (k-1):
            total_capacity_of_i_th_department = int(np.random.normal(temp//(k-i), temp//((k-i)*3)))
        else:
            total_capacity_of_i_th_department = temp
        total_capacity.append(total_capacity_of_i_th_department)
        ratio_of_first = np.random.randint(3, 5) #二割から三割を第一段階で選ぶ
        first = total_capacity_of_i_th_department//ratio_of_first
        second = total_capacity_of_i_th_department-first
        L = [first, second]
        designated_dep = 0
        if i <= (k//3-1):
            designated_dep = 0
        elif i <= (k//3-2):
            designated_dep = 1
        else:
            designated_dep = 2
        capacity_of_dep = []
        for j in range(2):
            ratio_of_designated_dep = np.random.randint(5, 11)
            designated_dep_num = (L[j]*ratio_of_designated_dep)//10
            all_dep_num = L[j]-designated_dep_num
            if j == 0:
                first_capacity.append([designated_dep_num, all_dep_num])
            else:
                second_capacity.append([designated_dep_num, all_dep_num])
        temp -= total_capacity_of_i_th_department
    return total_capacity, first_capacity, second_capacity

#学生の得点を決定(同じ得点の学生はほぼ発生しない)
def score_of_each_student(n):
    score_and_id = []
    score_solo = []
    for i in range(n):
        score_of_i_th_student = np.random.normal(70, 10)
        if score_of_i_th_student < 0:
            score_of_i_th_student = np.random.rand()
        elif score_of_i_th_student > 100:
            score_of_i_th_student = 100-np.random.rand()
        score_and_id.append([score_of_i_th_student, i])
        score_solo.append(score_of_i_th_student)
    return score_and_id, score_solo

#第一段階
def first_step_wish(n, k):
    wished = [0 for i in range(n)]
    for i in range(n):
        wished_dep = 0
        t = np.random.randint(0, 100)
        if t > 70: #行きにくい学科へ
            if i < n//3:
                wished_dep = np.random.randint(k//3, k)
            elif i < 2*(n//3):
                u = np.random.randint(1,3)
                if u == 1:
                    wished_dep = np.random.randint(0, k//3)
                else:
                    wished_dep = np.random.randint(2*(k//3), k)
            else:
                wished_dep = np.random.randint(0, 2*(k//3))
            wished[i] = [[wished_dep, 'A'], [wished_dep, 'A']]
        else: #行きやすい(指定科類枠がある)学科へ
            if i < n//3:
                wished_dep = np.random.randint(0, k//3)
            elif i < 2*(n//3):
                wished_dep = np.random.randint(k//3, 2*(k//3))
            else:
                wished_dep = np.random.randint(2*(k//3), k)
            wished[i] = [[wished_dep, 'S'], [wished_dep, 'A']]
    return wished

def second_step_wish(n, k):
    wished = []
    for i in range(n):
        hoge = []
        fuga = [j for j in range(k+1)]
        pohe = [j for j in range(k)]
        retention_flag = 0 #留年を最後の選択肢にする
        coin = np.random.rand()
        if coin > 0.9:
            retention_flag = 1 #行きたくない学科に行くよりは留年する
        if retention_flag == 1:
            for j in range(k+1):
                aaa = np.random.randint(0, len(fuga))
                if i < n//3:
                    if fuga[aaa] < k//3:
                        hoge.append([fuga[aaa], 'S'])
                        hoge.append([fuga[aaa], 'A'])
                    else:
                        hoge.append([fuga[aaa], 'A'])
                        hoge.append([fuga[aaa], 'A'])
                elif i < 2*(n//3):
                    if k//3 <= fuga[aaa] and fuga[aaa] < 2*(k//3):
                        hoge.append([fuga[aaa], 'S'])
                        hoge.append([fuga[aaa], 'A'])
                    else:
                        hoge.append([fuga[aaa], 'A'])
                        hoge.append([fuga[aaa], 'A'])
                else:
                    if 2*(k//3) < fuga[aaa] and fuga[aaa] < k:
                        hoge.append([fuga[aaa], 'S'])
                        hoge.append([fuga[aaa], 'A'])
                    else:
                        hoge.append([fuga[aaa], 'A'])
                        hoge.append([fuga[aaa], 'A'])
                fuga.remove(fuga[aaa])
        else:
            for j in range(k):
                aaa = np.random.randint(0, len(pohe))
                if i < n//3:
                    if pohe[aaa] < k//3:
                        hoge.append([pohe[aaa], 'S'])
                        hoge.append([pohe[aaa], 'A'])
                    else:
                        hoge.append([pohe[aaa], 'A'])
                        hoge.append([pohe[aaa], 'A'])
                elif i < 2*(n//3):
                    if k//3 <= pohe[aaa] and pohe[aaa] < 2*(k//3):
                        hoge.append([pohe[aaa], 'S'])
                        hoge.append([pohe[aaa], 'A'])
                    else:
                        hoge.append([pohe[aaa], 'A'])
                        hoge.append([pohe[aaa], 'A'])
                else:
                    if 2*(k//3) <= pohe[aaa] and pohe[aaa] < k:
                        hoge.append([pohe[aaa], 'S'])
                        hoge.append([pohe[aaa], 'A'])
                    else:
                        hoge.append([pohe[aaa], 'A'])
                        hoge.append([pohe[aaa], 'A'])
                pohe.remove(pohe[aaa])
            hoge.append([k, 'S'])
            hoge.append([k, 'A'])
        wished.append(hoge)
    return wished

#n = 300 #学生数(0~299で管理、100人ずつ0,1,2の3つの科類に分かれている)
#k = 6 #学科数(0~5で管理, 1/3ごとに、指定科類は0,1,2とする。それぞれ学生の希望をそちらに偏重させる)

def sinfuri(n, k, show_flag):
    score_id, score = score_of_each_student(n)
    #plt.hist(score, bins = 100)
    total_capacity, first_capacity, second_capacity = capacity_of_each_departments(n, k)
    confirmed = [[False, -1] for i in range(n)] #進学先のリスト
    #第一段階
    first_wish = first_step_wish(n, k)
    W, first_match_counter = gale_shapley(confirmed, first_wish, first_capacity, score_id, n, k, 2, show_flag)
    #第二段階
    second_wish = second_step_wish(n,k)
    V, second_match_counter = gale_shapley(W, second_wish, second_capacity, score_id, n, k, 2*k+2, show_flag)
    return first_match_counter, second_match_counter

#人数でどう変化するか
def sinfuri_student(dif_x, unit_num, dep_num):
    L = []
    for i in range(1, dif_x):
        L.append([unit_num*i, dep_num])
    M = []
    for i in range(len(L)):
        x,y = sinfuri(L[i][0], L[i][1], 0)
        M.append([x,y])
    plt.xlabel("students")
    plt.ylabel("first steps")
    for i in range(len(L)):
        plt.scatter(L[i][0], M[i][0], label = str(L[i][0])+","+str(L[i][1]))
    plt.show()
    plt.xlabel("students")
    plt.ylabel("second steps")
    for i in range(len(L)):
        plt.scatter(L[i][0], M[i][1], label = str(L[i][0])+","+str(L[i][1]))
    plt.show()

#学科数でどう変化するか
def sinfuri_department(dif_x, unit_num, population):
    L = []
    for i in range(1, dif_x):
        L.append([population, i*unit_num])
    M = []
    for i in range(len(L)):
        x,y = sinfuri(L[i][0], L[i][1], 0)
        M.append([x,y])
    plt.xlabel("departments")
    plt.ylabel("first steps")
    for i in range(len(L)):
        plt.scatter(L[i][1], M[i][0], label = str(L[i][0])+","+str(L[i][1]))
    plt.show()
    plt.xlabel("departments")
    plt.ylabel("second steps")
    for i in range(len(L)):
        plt.scatter(L[i][1], M[i][1], label = str(L[i][0])+","+str(L[i][1]))
    plt.show()

#sinfuri(10, 3, 1)
#sinfuri_student(20, 500, 50)
#sinfuri_department(50, 20, 1000)
