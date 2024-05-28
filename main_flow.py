"""
In this file you'll find all the entry points
for the different deployments for this project
"""

import os
from datetime import datetime, timedelta
from typing import Any, Dict

import yaml
from dotenv import load_dotenv
from prefect import flow, task

from data.api_data_to_df_flow import api_data_to_df
from data.clean_data_flow import clean_data
from data.download_data_from_coincap_flow import get_crypto_data_flow
from data.prepare_db_flow import prepare_database
from data.upload_data_to_db_flow import upload_data_to_database
from model.model_flow import model_flow

CONFIG_FILE_PATH = "cryptopredictor_config.yml"


@task()
def read_config(file_path: str) -> Dict[str, Any]:
    """Reads the config file and returns the configuration as a dictionary."""
    with open(file_path, "r", encoding="utf-8") as file:
        conf = yaml.safe_load(file)
    return conf


@flow(name="Main Flow - Data Gathering Flow")
def data_gathering_flow(
    trn_range: Dict[str, str],
    val_range: Dict[str, str],
    tst_range: Dict[str, str],
    intrval: str,
    crypto_c: str,
    user: str,
    pasw: str,
    db: str,
    port: str,
    host: str,
) -> None:
    """Main data gathering flow that orchestrates the
    collection of training, validation, and testing data."""

    @flow(name="Sub Flow - Training Data")
    def training_data_gathering_flow(
        start_d: str,
        end_d: str,
        intrvl: str,
        coin: str,
        usr: str,
        pwd: str,
        db: str,
        prt: str,
        hst: str,
    ) -> None:
        """Sub flow to gather and upload training data."""
        _, api_data_str = get_crypto_data_flow(
            interval=intrvl, crypto_coin=coin, start_date=start_d, end_date=end_d
        )
        trn_coin_df = api_data_to_df(api_data_str)
        cln_trn_coin_df = clean_data(trn_coin_df)
        upload_data_to_database(
            df=cln_trn_coin_df,
            schema="mlops",
            table_name="trainingdata",
            db_user=usr,
            db_password=pwd,
            db_name=db,
            db_port=prt,
            db_host=hst,
        )

    @flow(name="Sub Flow - Validation Data")
    def validation_data_gathering_flow(
        start_d: str,
        end_d: str,
        intrvl: str,
        coin: str,
        usr: str,
        pwd: str,
        db: str,
        prt: str,
        hst: str,
    ) -> None:
        """Sub flow to gather and upload validation data."""
        _, api_data_str = get_crypto_data_flow(
            interval=intrvl, crypto_coin=coin, start_date=start_d, end_date=end_d
        )
        trn_coin_df = api_data_to_df(api_data_str)
        cln_trn_coin_df = clean_data(trn_coin_df)
        upload_data_to_database(
            df=cln_trn_coin_df,
            schema="mlops",
            table_name="validationdata",
            db_user=usr,
            db_password=pwd,
            db_name=db,
            db_port=prt,
            db_host=hst,
        )

    @flow(name="Sub Flow - Test Data")
    def test_data_gathering_flow(
        start_d: str,
        end_d: str,
        intrvl: str,
        coin: str,
        usr: str,
        pwd: str,
        db: str,
        prt: str,
        hst: str,
    ) -> None:
        """Sub flow to gather and upload test data."""
        _, api_data_str = get_crypto_data_flow(
            interval=intrvl, crypto_coin=coin, start_date=start_d, end_date=end_d
        )
        trn_coin_df = api_data_to_df(api_data_str)
        cln_trn_coin_df = clean_data(trn_coin_df)
        upload_data_to_database(
            df=cln_trn_coin_df,
            schema="mlops",
            table_name="testingdata",
            db_user=usr,
            db_password=pwd,
            db_name=db,
            db_port=prt,
            db_host=hst,
        )

    @flow(name="Sub Flow - Recent Data")
    def recent_data_gathering_flow(
        start_d: str,
        end_d: str,
        intrvl: str,
        coin: str,
        usr: str,
        pwd: str,
        db: str,
        prt: str,
        hst: str,
    ) -> None:
        """Sub flow to gather and upload recent data."""
        _, api_data_str = get_crypto_data_flow(
            interval=intrvl, crypto_coin=coin, start_date=start_d, end_date=end_d
        )
        trn_coin_df = api_data_to_df(api_data_str)
        cln_trn_coin_df = clean_data(trn_coin_df)
        upload_data_to_database(
            df=cln_trn_coin_df,
            schema="mlops",
            table_name="recentdata",
            db_user=usr,
            db_password=pwd,
            db_name=db,
            db_port=prt,
            db_host=hst,
        )

    prepare_database(
        sql_file_path="sql_scripts/create_schemas.sql",
        db_host=host,
        db_user=user,
        db_password=pasw,
        db_port=port,
        db_name=db,
    )

    recent_date_start = (datetime.now() - timedelta(days=7)).strftime("%d/%m/%Y")
    recent_date_end = datetime.now().strftime("%d/%m/%Y")

    training_data_gathering_flow(
        start_d=trn_range["start_date"],
        end_d=trn_range["end_date"],
        intrvl=intrval,
        coin=crypto_c,
        usr=user,
        pwd=pasw,
        db=db,
        prt=port,
        hst=host,
    )

    validation_data_gathering_flow(
        start_d=val_range["start_date"],
        end_d=val_range["end_date"],
        intrvl=intrval,
        coin=crypto_c,
        usr=user,
        pwd=pasw,
        db=db,
        prt=port,
        hst=host,
    )

    test_data_gathering_flow(
        start_d=tst_range["start_date"],
        end_d=tst_range["end_date"],
        intrvl=intrval,
        coin=crypto_c,
        usr=user,
        pwd=pasw,
        db=db,
        prt=port,
        hst=host,
    )

    recent_data_gathering_flow(
        start_d=recent_date_start,
        end_d=recent_date_end,
        intrvl=intrval,
        coin=crypto_c,
        usr=user,
        pwd=pasw,
        db=db,
        prt=port,
        hst=host,
    )


@flow()
def main_flow() -> None:
    """Main flow entry point."""
    config = read_config(CONFIG_FILE_PATH)

    model_parameters = config.get("model_parameters", {})

    training_range = model_parameters.get("training_range", {})
    validation_range = model_parameters.get("validation_range", {})
    test_range = model_parameters.get("test_range", {})
    interval = model_parameters.get("interval", {"type": "h6"})
    num_values = model_parameters.get("num_values", 25)
    threshold = model_parameters.get("threshold", 0.25)
    crypto_coin = model_parameters.get("crypto_coin", "bitcoin")
    sequence_length = model_parameters.get("sequence_len", 5)

    load_dotenv(".env")

    postgres_user = os.environ.get("POSTGRES_USER")
    postgres_password = os.environ.get("POSTGRES_PASSWORD")
    postgres_db = os.environ.get("POSTGRES_DB")
    postgres_port = os.environ.get("POSTGRES_PORT")
    postgres_host = os.environ.get("POSTGRES_HOST")

    data_gathering_flow(
        trn_range=training_range,
        val_range=validation_range,
        tst_range=test_range,
        intrval=interval["type"],
        crypto_c=crypto_coin,
        user=postgres_user,
        pasw=postgres_password,
        db=postgres_db,
        port=postgres_port,
        host=postgres_host,
    )

    model_flow(
        sequence_length,
        training_range,
        validation_range,
        test_range,
        postgres_user,
        postgres_password,
        postgres_host,
        postgres_port,
        postgres_db,
    )


if __name__ == "__main__":
    main_flow()
