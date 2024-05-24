"""
In this file you'll find all the entrypoints 
for the different deployments for this project
"""
import yaml

CONFIG_FILE_PATH = 'cryptopredictor_config.yml'

def read_config(file_path):
    """Reads the config file"""
    with open(file_path, 'r',encoding='utf-8') as file:
        conf = yaml.safe_load(file)
    return conf

config = read_config(CONFIG_FILE_PATH)

model_parameters = config.get('model_parameters', {})
training_range = model_parameters.get('training_range', {})
validation_range = model_parameters.get('validation_range', {})
test_range = model_parameters.get('test_range', {})
interval = model_parameters.get('interval', {})
num_values = model_parameters.get('num_values')
threshold = model_parameters.get('threshold')
crypto_coin = model_parameters.get('crypto_coin')
