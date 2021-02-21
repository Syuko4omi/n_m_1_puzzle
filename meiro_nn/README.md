# 迷路を解きます

問題設定->
https://qiita.com/ishizakiiii/items/5eff79b59bce74fdca0d#dqn  

meiro.pyは、xを位置、yを上下左右の移動のQ値として、y = Wx+bの形式のニューラルネットワークを持っている。  
meiro_conv.pyは、y = W'(Wx+b)+b'の形式のニューラルネットワークを持っている。（隠れ層が一つある）
