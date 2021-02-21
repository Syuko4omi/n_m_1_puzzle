# 進振りのシミュレーション  

## 流れ
学生はまず、正規分布に従う「平均点」を各自持っているものとする。この平均点を基にして進振りが行われる。進振りは第一段階、第二段階に分かれているものとし、第一段階では学生は志望先を一つ決め、そこで受入留保アルゴリズムによって一部の学生が内定を獲得する。残った学生は第二段階に進み、今度はK+1種類の選択肢を並べて再び受入留保アルゴリズムを行う。本来は第三段階もあるが割愛した。

学生は三つの科類（一類、二類、三類）に均等に分かれているものとする。進学先の学科も三種類に分かれており、それぞれ一類、二類、三類の指定科類枠を持っている。学生は第一段階においては優先的に（70パーセントの確率で）自分の所属する科類の指定科類枠に出願するが、第二段階ではそれぞれの学科に均等の確率で出願するものとする。また、他の科類よりもどこにも行かない選択肢を高い優先順位にする学生もいるようにした（この学生は10パーセントの確率で発生する）。

安定なマッチングを求める手続きは次の通りである。

## 手続き★
ある学生Xが学科Aを志望した時、その時点で定員に達していなければ、仮の席が与えられる。もし定員に達していた場合、現在仮の席を与えられている学生の中で最も点数の低い学生Yと点数を比較し、Xの点数がYよりも高ければ、Yから仮の席をXに渡す。そうでなければYに席を与えたままにする。（以降の学生に対しても同じことを繰り返す。）

席を与えられなかったXまたはYに対し、学科Aの次に志望する学科に対し、上の手続き★を仮の席が与えられるまで行う。これを繰り返し、最終的に全ての学生の進路が決定した時点で終了する。