# test-mlfow

入力を [Hydra][linkhydra] で管理し、出力を [MLFlow][linkmlflow] で管理するサンプルスクリプト。

## 環境設定

```bash
pip install -r requirements.txt
```

## Hydra の設定

設定ファイルの置き場所

```python
HYDRA_CONFIG_PATH = os.path.join(os.curdir, 'conf')
HYDRA_CONFIG_NAME = 'config.yaml'
```

各ディレクトリ内でのデフォルトの設定ファイルを指定することができる。
`config.yaml` の設定例は下記の通り。

```yaml
defaults:
  - settings: default
  - data: default
  - model: default
```

## 実行

`version: 1.2` から、デフォルトでは working directory の位置が `outputs` 以下に変更しなくなった。
下記を正しく記録するためには、`outputs` 以下に移動する必要がある。

```python
mlflow.log_artifact('.hydra/config.yaml')			# まとめられた設定内容
mlflow.log_artifact('.hydra/hydra.yaml')			# Hydraの構成
mlflow.log_artifact('.hydra/overrides.yaml')		# コマンドラインから上書きした内容
```

そのためには、実行時に引数 `hydra.job.chdir=True` を加える必要がある。
実行例は下記の通り。

```bash
python main.py hydra.job.chdir=True
```

### 複数の設定で実行

設定項目をカンマで区切ると複数の設定を実行できる。

```bash
python main.py --multirun settings.run_name='test run 1','test run 2'
```

複数の設定項目に複数の設定を指定することも可能。
その場合は、全組み合わせが実行される。

```bash
$ python main.py --multirun settings.run_name='test run 1','test run 2' data.train.hoge=2,3

[2022-05-21 00:52:03,577][HYDRA] 	#0 : settings.run_name=test\ run\ 1 data.train.hoge=2
{'settings': {'experiment_name': 'test', 'run_name': 'test run 1'}, 'data': {'train': {'hoge': 2}, 'valid': {'hoge': 1}, 'test': {'hoge': 2}}, 'model': {'hyperparam': {'hoge': 1}}}
[2022-05-21 00:52:03,635][HYDRA] 	#1 : settings.run_name=test\ run\ 1 data.train.hoge=3
{'settings': {'experiment_name': 'test', 'run_name': 'test run 1'}, 'data': {'train': {'hoge': 3}, 'valid': {'hoge': 1}, 'test': {'hoge': 2}}, 'model': {'hyperparam': {'hoge': 1}}}
[2022-05-21 00:52:03,688][HYDRA] 	#2 : settings.run_name=test\ run\ 2 data.train.hoge=2
{'settings': {'experiment_name': 'test', 'run_name': 'test run 2'}, 'data': {'train': {'hoge': 2}, 'valid': {'hoge': 1}, 'test': {'hoge': 2}}, 'model': {'hyperparam': {'hoge': 1}}}
[2022-05-21 00:52:03,758][HYDRA] 	#3 : settings.run_name=test\ run\ 2 data.train.hoge=3
{'settings': {'experiment_name': 'test', 'run_name': 'test run 2'}, 'data': {'train': {'hoge': 3}, 'valid': {'hoge': 1}, 'test': {'hoge': 2}}, 'model': {'hyperparam': {'hoge': 1}}}
```

## 結果の確認

`mlruns` があるディレクトリで Web UI を開く。

```bash
mlflow ui
```

[linkhydra]:https://github.com/facebookresearch/hydra
[linkmlflow]:https://mlflow.org/
