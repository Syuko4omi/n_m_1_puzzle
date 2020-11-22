import math
import random
import heapq
import copy

#0 represents _

print("choose n and m")
print("n:")
n = int(input())
print("m:")
m = int(input())

def print_board(state_li):
    for i in range(n*m):
        if state_li[i] == 0:
            print('_', end = '')
        else:
            print(str(state_li[i]), end = '')
        if i%m == m-1:
            print()

def calc_id(state_li):
    state = copy.deepcopy(state_li)
    cur = 0
    temp = n*m-1
    id = 0
    while id < n*m:
        if temp != 0:
            cur += state[id]*math.factorial(temp)
        temp -= 1
        for j in range(id+1, n*m):
            if state[j] > state[id]:
                state[j] -= 1
        id += 1
    return cur

def calc_manhattan(state_li):
    cost = 0
    for i in range(len(state_li)):
        if state_li[i] != 0:
            temp = state_li[i]
            cost += int(abs(math.floor((temp-1)/m)-i//m)+abs((temp-1)%m-i%m))
        else:
            cost += abs(i//m-(m-1))+abs(i%m-(m-1))
    return cost

def pivot(state_li, i, j):
    state = copy.deepcopy(state_li)
    cur_1 = state[i]
    cur_2 = state[j]
    state[i] = cur_2
    state[j] = cur_1
    return state

def generate_new_state(state_li):
    L = []
    id_zero = 0
    for i in range(n*m):
        if state_li[i] == 0:
            id_zero = i
            break
    temp_y = id_zero//m
    temp_x = id_zero%m
    if temp_y == 0:
        if temp_x == 0:
            if m > 1:
                L.append(pivot(state_li, 0, 1))
            if n > 1:
                L.append(pivot(state_li, 0, m))
        elif temp_x == m-1:
            if m > 1:
                L.append(pivot(state_li, m-2, m-1))
            if n > 1:
                L.append(pivot(state_li, 2*m-1, m-1))
        else:
            if m > 2:
                L.append(pivot(state_li, id_zero, id_zero+1))
                L.append(pivot(state_li, id_zero, id_zero-1))
            if n > 1:
                L.append(pivot(state_li, id_zero, id_zero+m))
    elif temp_y == n-1:
        if temp_x == 0:
            if m > 1:
                L.append(pivot(state_li, id_zero, id_zero+1))
            if n > 1:
                L.append(pivot(state_li, id_zero, id_zero-m))
        elif temp_x == m-1:
            if m > 1:
                L.append(pivot(state_li, id_zero, id_zero-1))
            if n > 1:
                L.append(pivot(state_li, id_zero, id_zero-m))
        else:
            if m > 2:
                L.append(pivot(state_li, id_zero, id_zero+1))
                L.append(pivot(state_li, id_zero, id_zero-1))
            if n > 1:
                L.append(pivot(state_li, id_zero, id_zero-m))
    else:
        if temp_x == 0:
            if m > 1:
                L.append(pivot(state_li, id_zero, id_zero+1))
            if n > 2:
                L.append(pivot(state_li, id_zero, id_zero-m))
                L.append(pivot(state_li, id_zero, id_zero+m))
        elif temp_x == m-1:
            if m > 1:
                L.append(pivot(state_li, id_zero, id_zero-1))
            if n > 2:
                L.append(pivot(state_li, id_zero, id_zero-m))
                L.append(pivot(state_li, id_zero, id_zero+m))
        else:
            if m > 2:
                L.append(pivot(state_li, id_zero, id_zero-1))
                L.append(pivot(state_li, id_zero, id_zero+1))
            if n > 2:
                L.append(pivot(state_li, id_zero, id_zero-m))
                L.append(pivot(state_li, id_zero, id_zero+m))

    return L

goal_state = [i for i in range(1,n*m)]
goal_state.append(0)
depth_table = [[float('inf'), float('inf'), None] for i in range(math.factorial(n*m))] #[parent,depth]
initial_state = random.sample(goal_state, len(goal_state)) #make new state
cur_id = calc_id(initial_state)
depth_table[cur_id][0] = 0
depth_table[cur_id][1] = 0
depth_table[cur_id][2] = initial_state
Q = [[calc_manhattan(initial_state),initial_state]]
heapq.heapify(Q)
flag = True
print('I will solve this puzzle!')
print_board(initial_state)

while(True):
    if len(Q) != 0:
        cur_state = heapq.heappop(Q)
        cur_id = calc_id(cur_state[1])
        depth = depth_table[cur_id][1]
        if calc_manhattan(cur_state[1]) == 0:
            break
        else:
            L = generate_new_state(cur_state[1])
            S = []
            for i in range(len(L)):
                if depth_table[calc_id(L[i])][1] == float('inf'):
                    S.append([depth+1+calc_manhattan(L[i]), L[i]])
                    depth_table[calc_id(L[i])][0] = cur_id
                    depth_table[calc_id(L[i])][1] = depth+1
                    depth_table[calc_id(L[i])][2] = L[i]
            for i in range(len(S)):
                heapq.heappush(Q, S[i])
    else:
        flag = False
        break

if flag:
    ans_list = []
    while cur_id != calc_id(initial_state):
        ans_list.append(cur_id)
        cur_id = depth_table[cur_id][0]
    print('I solved this puzzle in',len(ans_list),'steps! Sollution follows:')
    for i in range(len(ans_list)-1, -1, -1):
        print_board(depth_table[ans_list[i]][2])
        print('___________')
else:
    print('I cannot solve this puzzle....')
