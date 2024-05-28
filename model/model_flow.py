"""
Everything model related happens in this doc
"""

from typing import Tuple
import pandas as pd
import optuna
import numpy as np
import mlflow.keras
import mlflow
from sqlalchemy import create_engine
from prefect import task, flow
from optuna.samplers import TPESampler
from optuna.pruners import WilcoxonPruner
from mlflow.tracking import MlflowClient
from mlflow.models.signature import infer_signature
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, Input
import datetime

OPTUNA_URI = "sqlite:///optuna_lstm.db"
MLFLOW_URI = "sqlite:///mlflow.db"

@task(
    name="Get Data From Database",
    description="Fetch data from a database table and return it as a pandas DataFrame.",
)
def get_data_from_database(
    schema: str,
    table_name: str,
    db_user: str,
    db_password: str,
    db_host: str,
    db_port: int,
    db_name: str,
) -> pd.DataFrame:
    """
    Fetch data from a database table and return it as a pandas DataFrame.

    Parameters:
    schema (str): The schema name.
    table_name (str): The table name.
    db_user (str): The database user.
    db_password (str): The database password.
    db_host (str): The database host.
    db_port (int): The database port.
    db_name (str): The database name.

    Returns:
    pd.DataFrame: The data from the specified table.
    """
    db_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    engine = create_engine(db_url)
    query = f"SELECT * FROM {schema}.{table_name}"
    df = pd.read_sql_query(query, con=engine)

    return df


def create_sequences(
    data: np.ndarray, seq_length: int
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Create sequences from data for time series forecasting.

    Args:
        data (np.ndarray): Input data array.
        seq_length (int): Length of each sequence.

    Returns:
        Tuple[np.ndarray, np.ndarray]: Tuple containing the
        sequences (xs) and corresponding targets (ys).
    """
    xs, ys = [], []
    for i in range(len(data) - seq_length):
        x = data[i : (i + seq_length)]
        y = data[i + seq_length]
        xs.append(x)
        ys.append(y)
    return np.array(xs), np.array(ys)


@flow(
    name="Train, HPO and Log Model",
    description="Train a model with hyperparameter optimization and log the model using MLflow.",
)
def train_model(
    train_set: pd.DataFrame,
    validation_set: pd.DataFrame,
    test_set: pd.DataFrame,
    train_date_range: dict[str, str],
    val_date_range: dict[str, str],
    test_date_range: dict[str, str],
    seq_length: int = 12,
) -> None:
    """
    Train a model with hyperparameter optimization and log the model using MLflow.

    Args:
        train_set (pd.DataFrame): Training dataset.
        validation_set (pd.DataFrame): Validation dataset.
        test_set (pd.DataFrame): Test dataset.
        train_date_range (Tuple[str, str]): Date range for the training set.
        val_date_range (Tuple[str, str]): Date range for the validation set.
        test_date_range (Tuple[str, str]): Date range for the test set.
        seq_length (int, optional): Length of each sequence. Defaults to 12.
    """
    train = train_set["PriceUSD"].values
    validation = validation_set["PriceUSD"].values
    test = test_set["PriceUSD"].values

    x_trn, y_trn = create_sequences(train, seq_length)
    x_val, y_val = create_sequences(validation, seq_length)
    x_tst, y_tst = create_sequences(test, seq_length)

    n_features = 1  # Number of features, e.g., 1 for univariate time series

    def objective(trial: optuna.trial.Trial) -> Tuple[float, float, float]:
        """
        Objective function for Optuna hyperparameter optimization.

        Args:
            trial (optuna.trial.Trial): A trial object that suggests hyperparameters.

        Returns:
            Tuple[float, float]: Loss and accuracy on the validation set.
        """
        n_units_1 = trial.suggest_int("n_units_1", 50, 250)
        n_units_2 = trial.suggest_int("n_units_2", 50, 250)
        dropout_rate_1 = trial.suggest_float("dropout_rate_1", 0.1, 0.5)
        dropout_rate_2 = trial.suggest_float("dropout_rate_2", 0.1, 0.5)
        learning_rate = trial.suggest_float("learning_rate", 1e-6, 1e-1, log=True)
        batch_size = trial.suggest_int("batch_size", 16, 256, step=8)

        model = Sequential(
            [
                Input(shape=(seq_length, n_features)),
                LSTM(n_units_1, return_sequences=True),
                Dropout(dropout_rate_1),
                LSTM(n_units_2),
                Dropout(dropout_rate_2),
                Dense(64, activation="relu"),
                Dense(1, activation="sigmoid"),
            ]
        )

        opt = Adam(learning_rate=learning_rate)
        model.compile(
            optimizer=opt, loss="mean_squared_error", metrics=["mae"]
        )

        # Train the model
        model.fit(
            x_trn,
            y_trn,
            epochs=7,
            batch_size=batch_size,
            validation_split=0.25,
            verbose=0
        )

        l, m = model.evaluate(x_val, y_val)
        return l, m

    mlflow.set_tracking_uri(MLFLOW_URI)

    sampler = TPESampler(seed=42)
    pruner = WilcoxonPruner(p_threshold=0.25)

    study = optuna.create_study(
        directions=["minimize","minimize"],
        storage=OPTUNA_URI,
        load_if_exists=True,
        sampler=sampler,
        pruner=pruner,
    )

    study.optimize(objective, n_trials=125)
    best_trial = study.best_trials[-1]
    best_params = best_trial.params

    final_model = Sequential(
        [
            Input(shape=(seq_length, n_features)),
            LSTM(
                best_params["n_units_1"],
                return_sequences=True
            ),
            Dropout(best_params["dropout_rate_1"]),
            LSTM(best_params["n_units_2"]),
            Dropout(best_params["dropout_rate_2"]),
            Dense(64, activation="relu"),
            Dense(1, activation="sigmoid"),
        ]
    )

    optimizer = Adam(learning_rate=best_params["learning_rate"])
    final_model.compile(
        optimizer=optimizer, loss="mean_squared_error", metrics=["mae"]
    )

    final_model.fit(
        x_trn,
        y_trn,
        epochs=15,
        batch_size=best_params["batch_size"],
        validation_data=(x_tst, y_tst),
        verbose = 0
    )

    loss, mae = final_model.evaluate(x_tst, y_tst)

    experiment_name = f"CryptoModelTracking-{datetime.datetime.now().strftime('%H:%M:%S %d:%m:%Y')}"

    client = MlflowClient(tracking_uri=MLFLOW_URI)
    if experiment_name not in [exp.name for exp in client.search_experiments()]:
        mlflow.create_experiment(experiment_name)
    mlflow.set_experiment(experiment_name)

    with mlflow.start_run() as run:
        try:
            mlflow.set_tag("developer", "red panda 🕊️")

            mlflow.keras.log_model(
                final_model, "model", signature=infer_signature(x_trn, y_trn)
            )

            mlflow.log_params(best_params)
            mlflow.log_params({
                "training_set_date_range": train_date_range,
                "validation_set_date_range": val_date_range,
                "test_date_range": test_date_range
            })
            mlflow.log_params({
                "LOSS": loss,
                "MAE": mae
            })

            model_uri = f"runs:/{run.info.run_id}/model"
            mlflow.register_model(model_uri, "CryptoModel")
            latest_model_version = client.get_latest_versions("CryptoModel", stages=['None'])
            latest_version_number = latest_model_version[0].version if latest_model_version else None
            client.set_registered_model_alias("CryptoModel", "Production", latest_version_number)

        except Exception as e:
            mlflow.log_param("error", str(e))
            raise

@flow(name="Main Flow - Model Training")
def model_flow(
    sequence_length,
    train_range,
    valid_range,
    testing_range,
    pstgrs_user: str,
    pstgrs_password: str,
    pstgrs_host: str,
    pstgrs_port: int,
    pstgrs_name: str,
):
    """Main Flow - Model Training"""
    trn_set = get_data_from_database(
        schema="mlops",
        table_name="trainingdata",
        db_user=pstgrs_user,
        db_password=pstgrs_password,
        db_name=pstgrs_name,
        db_host=pstgrs_host,
        db_port=pstgrs_port,
    )

    val_set = get_data_from_database(
        schema="mlops",
        table_name="validationdata",
        db_user=pstgrs_user,
        db_password=pstgrs_password,
        db_name=pstgrs_name,
        db_host=pstgrs_host,
        db_port=pstgrs_port,
    )

    tst_set = get_data_from_database(
        schema="mlops",
        table_name="testingdata",
        db_user=pstgrs_user,
        db_password=pstgrs_password,
        db_name=pstgrs_name,
        db_host=pstgrs_host,
        db_port=pstgrs_port,
    )

    train_model(
        train_set=trn_set,
        validation_set=val_set,
        test_set=tst_set,
        train_date_range=train_range,
        val_date_range=valid_range,
        test_date_range=testing_range,
        seq_length=sequence_length,
    )
