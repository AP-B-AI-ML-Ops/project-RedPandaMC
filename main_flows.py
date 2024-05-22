import yaml

config_file_path = 'cryptopredictor_config.yml'

def read_config(file_path):
    with open(file_path, 'r') as file:
        config = yaml.safe_load(file)
    return config

config = read_config(config_file_path)

model_parameters = config.get('model_parameters', {})
training_range = model_parameters.get('training_range', {})
validation_range = model_parameters.get('validation_range', {})
test_range = model_parameters.get('test_range', {})
interval = model_parameters.get('interval', {})
num_values = model_parameters.get('num_values')
threshold = model_parameters.get('threshold')
crypto_coin = model_parameters.get('crypto_coin')

print("Model Parameters:")
print(f"Training Range: {training_range}")
print(f"Validation Range: {validation_range}")
print(f"Test Range: {test_range}")
print(f"Interval: {interval}")
print(f"Number of Values: {num_values}")
print(f"Threshold: {threshold}")
print(f"Crypto Coin: {crypto_coin}")