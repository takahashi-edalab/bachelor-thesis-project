# thesis-project
R6 学士特定課題プロジェクト チャネル配線問題.   
`src/algos.py`に含まれる`proposed_algorithm`関数を改良してLeft Edgeに勝とう！


## Preliminary
- [pyenv](https://github.com/pyenv/pyenv)
- [poetry](https://github.com/python-poetry/poetry)

### Python Instal
```
pyenv install 3.10.11
```


## Build Environment
1. clone project repository
```
git clone git@github.com:takahashi-edalab/bachelor-thesis-project.git
```
2. In the directory, create virtual python environment
```
cd bachelor-thesis-project
pyenv local 3.10.11
```

3. install necessary libraries to virtual environment
```
poetry config virtualenvs.in-project true && poetry install
```


## How to run
Run comparison script with scenario 1 and single gap
```
poetry run python -m src.main --seed 0 --n_nets 100  -c 1
```

You can see the following log
```
Input
  - #nets        : 100
  - Density      : 91
Lower Bound
  - #gaps used   : 1
==============================
Left Edge: 98.0
Proposal: 98.0
```


Run comparison script with scenario 2 and multiple gaps whose width = 10
```
poetry run python -m src.main --seed 0 --n_nets 100  -c 2 -w 10
```

You can see the following log
```
Input
  - #nets        : 100
  - Density      : 121
Lower Bound
  - #gaps used   : 13
==============================
Left Edge:  13
Proposal:  13
```

There are two kinds of net width probabilities exist as follows:

| scenario   | w=1  | w=2  | w=3  | w=4  | 
| --- | ---- | ---- | ---- | ---- | 
| 1   | 0.80 | 0.10 | 0.08 | 0.02 | 
| 2   | 0.50 | 0.30 | 0.15 | 0.05 | 




