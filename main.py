import os
import random

import pandas as pd
import hydra
from omegaconf import DictConfig
import mlflow


HYDRA_CONFIG_PATH = os.path.join(os.curdir, 'conf')
HYDRA_CONFIG_NAME = 'config.yaml'


@hydra.main(version_base='1.1', config_path=HYDRA_CONFIG_PATH, config_name=HYDRA_CONFIG_NAME)
def main(cfg: DictConfig) -> None:
	mlflow.set_tracking_uri('file://' + hydra.utils.get_original_cwd() + '/mlruns')
	experiment_name = cfg.settings.experiment_name
	mlflow.set_experiment(experiment_name)

	run_name = cfg.settings.run_name

	print(cfg)
	print(hydra.utils.get_original_cwd())

	with mlflow.start_run(run_name=run_name):
		mlflow.log_param('experiment_name', experiment_name)
		mlflow.log_param('run_name', run_name)

		# Log model
		mlflow.log_artifact('.hydra/config.yaml')			# まとめられた設定内容
		mlflow.log_artifact('.hydra/hydra.yaml')			# Hydraの構成
		mlflow.log_artifact('.hydra/overrides.yaml')		# コマンドラインから上書きした内容


if __name__ == '__main__':
	main()
