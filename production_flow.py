from prefect import flow, task
from typing import Dict, Any
import yaml
from dotenv import load_dotenv
from production.production_flow import prepare_future_prices_to_database,get_production_model,predict_future_prices
import os

CONFIG_FILE_PATH = "cryptopredictor_config.yml"

@task()
def read_config(file_path: str) -> Dict[str, Any]:
    """Reads the config file and returns the configuration as a dictionary."""
    with open(file_path, "r", encoding="utf-8") as file:
        conf = yaml.safe_load(file)
    return conf
@flow()
def production_main():
    config = read_config(CONFIG_FILE_PATH)

    model_parameters = config.get("model_parameters", {})

    interval = model_parameters.get("interval", {"type": "h6"})
    num_values = model_parameters.get("num_values", 25)
    sequence_length = model_parameters.get("sequence_len", 5)

    load_dotenv(".env")

    postgres_user = os.environ.get("POSTGRES_USER")
    postgres_password = os.environ.get("POSTGRES_PASSWORD")
    postgres_db = os.environ.get("POSTGRES_DB")
    postgres_port = os.environ.get("POSTGRES_PORT")
    postgres_host = os.environ.get("POSTGRES_HOST")

    prepare_future_prices_to_database(num_values=num_values,
                                      interval=interval['type'],
                                      db_user=postgres_user,
                                      db_password=postgres_password,
                                      db_host=postgres_host,
                                      db_port=postgres_port,
                                      db_name=postgres_db)

    model = get_production_model()

    predict_future_prices(
                    model=model,
                    seq_length=sequence_length,
                    db_user=postgres_user,
                    db_password=postgres_password,
                    db_host=postgres_host,
                    db_port=postgres_port,
                    db_name=postgres_db)


if __name__ == "__main__":
    production_main()