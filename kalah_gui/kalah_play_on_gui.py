import tkinter
from tkinter import messagebox
import random

EMPTY_BG_COLOR = "lightgray"
P0_COLOR = "deep sky blue"
P1_COLOR = "spring green"

def grid_to_house(x,y): #x, y -> n
    if y == 0:
        return 13-x
    else:
        if y == 2:
            return x-1
        else:
            if x == 0:
                return 13
            else:
                return 6

def house_to_grid(n): #n -> x, y
    if n == 13:
        return 0, 1
    elif n == 6:
        return 7, 1
    elif 0 <= n <= 5:
        return n+1, 2
    else:
        return 13-n, 0

class Kalah_Board():
    def __init__(self):
        L = [4 for i in range(14)]
        L[6] = 0
        L[13] = 0
        self.board = L

    def already_settled(self):
        for i in range(2):
            for j in range(6):
                self.board[7*i+6] += self.board[7*i+j]
                self.board[7*i+j] = 0

    def move_stones(self, num, player):
        moveable = self.list_houses_of_next_possible_move(player)
        if len(moveable) == 0: #if one cannot move stones
            opponent = 0
            if player == 0:
                opponent = 1
            self.already_settled()
            return 0 #finish the game
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
                        if self.board[6] > 24 or self.board[13] > 24:
                            self.already_settled()
                            return 0
                        else:
                            return 1 #continue player's turn
                    elif 7*player <= next_house <= 7*player+5 and self.board[next_house] == 0 and self.board[12-next_house] != 0:
                        self.board[7*player+6] += (1+self.board[12-next_house])
                        self.board[12-next_house] = 0
                        temp -= 1
                        if self.board[6] > 24 or self.board[13] > 24:
                            self.already_settled()
                            return 0
                        else:
                            return 2 #ryoudori
                    else:
                        self.board[next_house] += 1
                        temp -= 1
                        if self.board[6] > 24 or self.board[13] > 24:
                            self.already_settled()
                            return 0
                        else:
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
    def __init__(self, app, start_player = 0, turn = 0):
        super().__init__()
        self.current_player = start_player
        self.turn = turn #count turns(useless)
        self.winner = None
        self.app = app
        self.to_be_locked = 0
        self.play_mode = 0    #0: You vs CPU, 1: CPU vs You, 2: CPU vs CPU
        app.title("Kalah")
        app.geometry("800x300+400+100")
        app.resizable(0, 0)
        self.create_widgets()
        self.set_events()

    def is_finished(self):
        return self.winner is not None

    def list_houses_of_next_possible_move(self, player):
        return super().list_houses_of_next_possible_move(self.current_player)

    def get_next_player(self):
        if self.current_player == 0:
            return 1
        else:
            return 0

    def move_stones(self, num, player):
        cur = super().move_stones(num, player)
        if cur == 0:
            return self.finish_game()
        elif cur == 1:
            self.turn += 1
        else:
            self.current_player = self.get_next_player()
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

    def create_widgets(self):
        self.labels = [[None]*8 for i in range(3)]
        self.player_label = None
        self.message_window = None
        self.restart_button_0 = None
        self.restart_button_1 = None
        self.restart_button_2 = None
        for i in range(3):
            for j in range(8):
                if (j != 0 and j != 7) and i != 1:
                    if i == 0:
                        label = tkinter.Label(
                            self.app,
                            text = "4",
                            width = 8,
                            height = 4,
                            bg = P1_COLOR,
                            relief = tkinter.RAISED,
                        )
                    else:
                        label = tkinter.Label(
                            self.app,
                            text = "4",
                            width = 8,
                            height = 4,
                            bg = P0_COLOR,
                            relief = tkinter.RAISED
                        )
                elif (j == 0 or j == 7) and i == 1:
                    if j == 0:
                        label = tkinter.Label(
                            self.app,
                            text = "0",
                            width = 8,
                            height = 4,
                            bg = P1_COLOR,
                            relief = tkinter.FLAT
                        )
                    else:
                        label = tkinter.Label(
                            self.app,
                            text = "0",
                            width = 8,
                            height = 4,
                            bg = P0_COLOR,
                            relief = tkinter.FLAT
                        )
                else:
                    label = tkinter.Label(
                        self.app,
                        width = 8,
                        height = 4,
                        bg = EMPTY_BG_COLOR,
                        relief = tkinter.FLAT
                    )
                label.grid(column = j, row = i)
                self.labels[i][j] = label

        label1 = tkinter.Label(
            self.app,
            width = 15,
            height = 2,
            bg = P0_COLOR if self.current_player == 0 else P1_COLOR,
            relief = tkinter.FLAT,
            text = "Player:"+str(self.current_player)
        )
        label1.place(
            x=640,
            y=20,
            anchor=tkinter.NW
        )
        self.player_label = label1

        label2 = tkinter.Label(
            self.app,
            width = 50,
            height = 2,
            bg = EMPTY_BG_COLOR,
            relief = tkinter.FLAT,
            text = "This is your turn. Choose a house."
        )
        label2.place(
            x=80,
            y=250,
            anchor=tkinter.NW
        )
        self.message_window = label2

        button1 = tkinter.Button(
            self.app,
            width = 16,
            height = 2,
            text = "Restart: You vs CPU"
        )
        button1.place(
            x = 640,
            y = 150,
            anchor = tkinter.NW
        )
        self.restart_button_0 = button1

        button2 = tkinter.Button(
            self.app,
            width = 16,
            height = 2,
            text = "Restart: CPU vs You"
        )
        button2.place(
            x = 640,
            y = 185,
            anchor = tkinter.NW
        )
        self.restart_button_1 = button2
        
        button3 = tkinter.Button(
            self.app,
            width = 16,
            height = 2,
            text = "Restart: CPU vs CPU"
        )
        button3.place(
            x = 640,
            y = 220,
            anchor = tkinter.NW
        )
        self.restart_button_2 = button3

    def set_events(self):
        for i in range(3):
            for j in range(8):
                if (j != 0 and j != 7) and i != 1:
                    label = self.labels[i][j]
                    label.bind("<ButtonPress-1>", self.take_action)
                else:
                    None
        self.restart_button_0.bind("<ButtonPress-1>", self.reset_action)
        self.restart_button_1.bind("<ButtonPress-1>", self.reset_action)
        self.restart_button_2.bind("<ButtonPress-1>", self.reset_action)

    def refresh_board_color(self):
        for i in range(1,7):
            self.labels[0][i].config(bg = P1_COLOR)
            self.labels[2][i].config(bg = P0_COLOR)
        self.labels[1][0].config(bg = P1_COLOR)
        self.labels[1][7].config(bg = P0_COLOR)
    
    def update_board(self):
        self.refresh_board_color()
        for y in range(3):
            for x in range(8):
                if ((x != 0 and x != 7) and y != 1) or ((x == 0 or x == 7) and y == 1):
                    label = self.labels[y][x]
                    label.config(text = str(self.board[grid_to_house(x, y)]))
        label = self.player_label
        self.show_winner()
        label.config(
            text = "Player:"+str(self.current_player), 
            bg = P0_COLOR if self.current_player == 0 else P1_COLOR
        )
        app.after(1000, self.change_player)

    def take_action(self, event): #when a button is pressed
        if self.to_be_locked:
            self.message_window.config(text = "This is not your turn.")
            return
        label = event.widget
        if label.cget("text") == "0":
            self.message_window.config(text = "This house does not have any stone. Choose another house.")
            return
        else:
            self.message_window.config(text = "")
            x_axis = 0
            y_axis = 0
            for y in range(3):
                for x in range(8):
                    if self.labels[y][x] == label:
                        y_axis = y
                        x_axis = x
            if self.current_player == 0:
                if y_axis == 0:
                    self.message_window.config(text = "This is opponent's house. Choose your house.")
                    return
                else:
                    t = grid_to_house(x_axis, y_axis)
                    stone_num = self.board[t]
                    if self.labels[y_axis][x_axis].cget("bg") != "gold":
                        self.refresh_board_color()
                        self.labels[y_axis][x_axis].config(bg = "gold")
                        for i in range(1, stone_num+1):
                            x, y = house_to_grid((t+i)%14)
                            if self.labels[y][x].cget("bg") != "gold" and self.labels[y][x].cget("bg") != "orange":
                                self.labels[y][x].config(bg = "orange")
                            elif self.labels[y][x].cget("bg") == "orange":
                                self.labels[y][x].config(bg = "orange red")
                        self.message_window.config(text = "Press again if you want to move stones from the house.")
                    else:
                        house = grid_to_house(x_axis, y_axis)
                        self.to_be_locked = 1
                        self.move_stones(house, self.current_player)
                        self.update_board()
    
    def reset_action(self, event): #when reset button is pressed
        button = event.widget
        buttons_list = [self.restart_button_0, self.restart_button_1, self.restart_button_2]
        button_num = 0
        self.board = [4 for i in range(14)]
        self.board[6] = 0
        self.board[13] = 0
        for i in range(3):
            if button == buttons_list[i]:
                self.play_mode = i
        self.message_window.config(text = "Reset")
        if self.play_mode == 1:
            self.to_be_locked = 1
            self.current_player = 1
        else:
            self.current_player = 0
        self.winner = None
        self.update_board()
    
    def change_player(self):
        if self.play_mode != 2:
            if self.current_player == 1:
                self.CPU(1)
            else:
                self.YOU()
        else:
            if self.current_player == 1:
                self.CPU(1)
            else:
                self.CPU(0)
    
    def CPU(self, cpu_side):
        opponent = 0
        if cpu_side == 0:
            opponent = 1
        if self.current_player == opponent:
            return
        self.message_window.config(text = "")
        possible_choices = self.list_houses_of_next_possible_move(cpu_side)
        if possible_choices != []:
            cur = random.randint(0, len(possible_choices)-1)
            if cpu_side == 1:
                self.labels[0][6-possible_choices[cur]].config(bg = "gold")
            else:
                self.labels[2][possible_choices[cur]+1].config(bg = "gold")
            self.move_stones(possible_choices[cur], cpu_side)
        else:
            self.move_stones(-1, cpu_side)
        app.after(1000, self.update_board)
    
    def YOU(self):
        self.to_be_locked = 0
        if self.current_player == 1:
            return
        self.message_window.config(text = "This is your turn. Choose a house.")
        possible_choices = self.list_houses_of_next_possible_move(0)
        if possible_choices == []:
            self.move_stones(-1, 0)
            self.update_board()

    def show_winner(self):
        if playout.is_finished():
            if playout.winner == -1:
                self.message_window.config(text = "DRAW")
            else:
                self.message_window.config(text = "The winner is player" + str(playout.winner)+".")
    



if __name__ == "__main__":
    app = tkinter.Tk()
    playout = Playout_Kalah(app)
    app.mainloop()
