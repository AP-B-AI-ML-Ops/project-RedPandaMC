from mlflow.tracking import MlflowClient
import mlflow

def prepare_future_prices_to_database():
    pass

def get_production_model():
    client = MlflowClient()
    model_name = "CryptoPredictor"
    alias = "Production"
    
    model_version = client.get_model_version_by_alias(name=model_name, alias=alias)
    
    model_uri = f"models:/{model_name}/{model_version.version}"
    model = mlflow.pyfunc.load_model(model_uri)
    
    return model

def predict_future_prices(model):
    pass

def write_future_prices_to_database():
    pass