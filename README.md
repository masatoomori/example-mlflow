# test-mlfow

入力を [Hydra][linkhydra] で管理し、出力を [MLFlow][linkmlflow] で管理するサンプルスクリプト。

## 環境設定

```bash
pip install -r requirements.txt
```

## Hydra の設定

設定ファイルの置き場所

```bash
├── README.md
├── conf                  # 設定ファイルの置き場所
│   ├── config.yaml
│   ├── data/
│   ├── model/
│   └── settings/
├── data
│   └── raw
├── requirements.txt
├── src
│   └── models
└── venv
```

各ディレクトリ内でのデフォルトの設定ファイルを指定することができる。
`config.yaml` の設定例は下記の通り。

```yaml
defaults:
  - settings: default
  - data: default
  - model: default
```

### .py での利用例

```python
import os

import hydra
from omegaconf import DictConfig
import mlflow

HYDRA_CONFIG_PATH = path/to/conf
HYDRA_CONFIG_NAME = 'config.yaml'


@hydra.main(version_base=None, config_path=HYDRA_CONFIG_PATH, config_name=HYDRA_CONFIG_NAME)
def main(cfg: DictConfig) -> None:
    original_cwd = hydra.utils.get_original_cwd()

    assert original_cwd != os.getcwd(), 'run this script with `hydra.job.chdir=True`'

    mlflow.set_tracking_uri('file://' + original_cwd + '/mlruns')
    print(cfg)
```

### Jupyter Notebook での利用例

```python
import os

from hydra import initialize, compose
from omegaconf import DictConfig

HYDRA_CONFIG_PATH = path/to/conf
HYDRA_CONFIG_NAME = 'config.yaml'

with initialize(version_base=None, config_path=HYDRA_CONFIG_PATH):
    cfg = compose(config_name=HYDRA_CONFIG_NAME)
    print(cfg)
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
python train.py --multirun model.alpha=0.2,0.4 hydra.job.chdir=True
```

複数の設定項目に複数の設定を指定することも可能。
その場合は、全組み合わせが実行される。

```bash
$ python train.py --multirun model.alpha=0.2,0.4 model.l1_ratio=0.1,0.3  hydra.job.chdir=True

[2022-06-14 15:44:28,338][HYDRA] Launching 4 jobs locally
[2022-06-14 15:44:28,338][HYDRA] 	#0 : model.alpha=0.2 model.l1_ratio=0.1
{'settings': {'experiment_name': 'test'}, 'data': {'name': 'wine-quality', 'path': 'raw', 'file': 'wine-quality.csv'}, 'model': {'test_size': 0.2, 'alpha': 0.2, 'l1_ratio': 0.1, 'random_state': 22}}
[2022-06-14 15:44:29,255][HYDRA] 	#1 : model.alpha=0.2 model.l1_ratio=0.3
{'settings': {'experiment_name': 'test'}, 'data': {'name': 'wine-quality', 'path': 'raw', 'file': 'wine-quality.csv'}, 'model': {'test_size': 0.2, 'alpha': 0.2, 'l1_ratio': 0.3, 'random_state': 22}}
[2022-06-14 15:44:29,923][HYDRA] 	#2 : model.alpha=0.4 model.l1_ratio=0.1
{'settings': {'experiment_name': 'test'}, 'data': {'name': 'wine-quality', 'path': 'raw', 'file': 'wine-quality.csv'}, 'model': {'test_size': 0.2, 'alpha': 0.4, 'l1_ratio': 0.1, 'random_state': 22}}
[2022-06-14 15:44:30,600][HYDRA] 	#3 : model.alpha=0.4 model.l1_ratio=0.3
{'settings': {'experiment_name': 'test'}, 'data': {'name': 'wine-quality', 'path': 'raw', 'file': 'wine-quality.csv'}, 'model': {'test_size': 0.2, 'alpha': 0.4, 'l1_ratio': 0.3, 'random_state': 22}}
```

## 結果の確認

`mlruns` があるディレクトリで Web UI を開く。

```bash
mlflow ui
```

[linkhydra]:https://github.com/facebookresearch/hydra
[linkmlflow]:https://mlflow.org/
