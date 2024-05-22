from keras.layers import LSTM, Dense, Dropout
from keras.models import Sequential
from keras.optimizers import Adam
from mlflow.models.signature import infer_signature
from mlflow.tracking import MlflowClient
from optuna.pruners import WilcoxonPruner
from optuna.samplers import TPESampler
from sqlalchemy import create_engine
import mlflow
import mlflow.keras
import numpy as np
import optuna
import pandas as pd

SQLITE_URL = "sqlite:///optuna_lstm.db"


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


def create_sequences(data, seq_length):
    xs, ys = [], []
    for i in range(len(data) - seq_length):
        x = data[i : (i + seq_length)]
        y = data[i + seq_length]
        xs.append(x)
        ys.append(y)
    return np.array(xs), np.array(ys)


def train_model(train_set, validation_set, test_set, seq_length: int = 12):

    train = train_set["PriceUSD"].values
    validation = validation_set["PriceUSD"].values
    test = test_set["PriceUSD"].values

    x_trn, y_trn = create_sequences(train, seq_length)
    x_val, y_val = create_sequences(validation, seq_length)
    x_tst, y_tst = create_sequences(test, seq_length)

    def objective(trial):
        n_units_1 = trial.suggest_int("n_units_1", 50, 200)
        n_units_2 = trial.suggest_int("n_units_2", 50, 200)
        dropout_rate_1 = trial.suggest_float("dropout_rate_1", 0.2, 0.5)
        dropout_rate_2 = trial.suggest_float("dropout_rate_2", 0.2, 0.5)
        learning_rate = trial.suggest_loguniform("learning_rate", 1e-5, 1e-2)
        batch_size = trial.suggest_int("batch_size", 16, 128)

        model = Sequential(
            [
                LSTM(
                    n_units_1,
                    return_sequences=True,
                    input_shape=(x_trn.shape[1], x_trn.shape[2]),
                ),
                Dropout(dropout_rate_1),
                LSTM(n_units_2),
                Dropout(dropout_rate_2),
                Dense(64, activation="relu"),
                Dense(1, activation="sigmoid"),
            ]
        )

        optimizer = Adam(learning_rate=learning_rate)
        model.compile(
            optimizer=optimizer, loss="binary_crossentropy", metrics=["accuracy"]
        )

        model.fit(
            x_trn,
            y_trn,
            epochs=5,
            batch_size=batch_size,
            validation_split=0.2,
            verbose=0,
        )

        loss, accuracy = model.evaluate(x_val, y_val, verbose=0)

        return loss, accuracy

    sampler = TPESampler(seed=42, n_startup_trials=25)
    pruner = WilcoxonPruner(p_threshold=0.12, n_startup_steps=25)
    study = optuna.create_study(
        directions=["minimize", "maximize"],
        storage=SQLITE_URL,
        load_if_exists=True,
        sampler=sampler,
        pruner=pruner,
    )
    study.optimize(objective, n_trials=250)
    best_params = study.best_params

    final_model = Sequential(
        [
            LSTM(
                best_params["n_units_1"],
                return_sequences=True,
                input_shape=(x_trn.shape[1], x_trn.shape[2]),
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
        optimizer=optimizer, loss="binary_crossentropy", metrics=["accuracy"]
    )

    final_model.fit(
        x_trn,
        y_trn,
        epochs=15,
        batch_size=best_params["batch_size"],
        validation_data=(x_tst, y_tst),
    )

    with mlflow.start_run() as run:
        mlflow.keras.log_model(
            final_model, "model", signature=infer_signature(x_trn, y_trn)
        )
        mlflow.log_params(best_params)
        model_uri = f"runs:/{run.info.run_id}/model"
        client = MlflowClient()
        client.create_registered_model("CryptoPredictor")
        model_version = client.create_model_version(
            name="CryptoPredictor", source=model_uri, run_id=run.info.run_id
        )
        client.set_registered_model_alias(
            name="CryptoPredictor", alias="Production", version=model_version.version
        )
