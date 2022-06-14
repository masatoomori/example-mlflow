import os
import tempfile

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import ElasticNet
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import hydra
from omegaconf import DictConfig
import mlflow


HYDRA_CONFIG_PATH = os.path.join(os.pardir, os.pardir, 'conf')
HYDRA_CONFIG_NAME = 'config.yaml'

DATA_PATH = os.path.join(os.pardir, os.pardir, 'data')


def eval_metrics(actual, pred):
    rmse = np.sqrt(mean_squared_error(actual, pred))
    mae = mean_absolute_error(actual, pred)
    r2 = r2_score(actual, pred)
    return rmse, mae, r2


def log_hydra_config():
	mlflow.log_artifact('.hydra/config.yaml', 'config')			# まとめられた設定内容
	mlflow.log_artifact('.hydra/hydra.yaml', 'config')			# Hydraの構成
	mlflow.log_artifact('.hydra/overrides.yaml', 'config')		# コマンドラインから上書きした内容


def log_file(df, file_name, dir_name):
	with tempfile.TemporaryDirectory() as tmp_dir:
		tmp_file = os.path.join(tmp_dir, file_name)
		df.to_pickle(tmp_file)
		mlflow.log_artifact(tmp_file, dir_name)


@hydra.main(version_base=None, config_path=HYDRA_CONFIG_PATH, config_name=HYDRA_CONFIG_NAME)
def main(cfg: DictConfig) -> None:
	original_cwd = hydra.utils.get_original_cwd()		# スクリプト実行場所

	assert original_cwd != os.getcwd(), 'run this script with `hydra.job.chdir=True`'

	mlflow.set_tracking_uri('file://' + original_cwd + '/mlruns')
	experiment_name = cfg.experiment_name
	mlflow.set_experiment(experiment_name)

	print(original_cwd)
	print(cfg)

	df = pd.read_csv(os.path.join(original_cwd, DATA_PATH, cfg.data.path, cfg.data.file))
	df_train, df_test = train_test_split(df, test_size=cfg.model.test_size)
	X_train = df_train.drop('quality', axis=1)
	y_train = df_train['quality']
	X_test = df_test.drop('quality', axis=1)
	y_test = df_test['quality']

	with mlflow.start_run():
		mlflow.log_param('experiment_name', experiment_name)

		model = ElasticNet(alpha=cfg.model.alpha, l1_ratio=cfg.model.l1_ratio, random_state=cfg.model.random_state)
		model.fit(X_train, y_train)
		y_pred = model.predict(X_test)
		(rmse, mae, r2) = eval_metrics(y_test, y_pred)

		df_train['pred'] = model.predict(X_train)
		df_test['pred'] = model.predict(X_test)

		# Log model
		mlflow.log_metric("rmse", rmse)
		mlflow.log_metric("r2", r2)
		mlflow.log_metric("mae", mae)
		mlflow.sklearn.log_model(model, "model")
		log_hydra_config()
		log_file(df_train, cfg.data.name + '_train.pkl', 'result')
		log_file(df_test, cfg.data.name + '_test.pkl', 'result')


if __name__ == '__main__':
	main()
