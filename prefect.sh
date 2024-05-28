#!/bin/bash

touch mlflow.db && \

touch optuna_lstm.db && \

prefect init --recipe local && \

prefect worker start -t process -p main_pool &

prefect --no-prompt deploy main_flow.py:main_flow -p main_pool -n Setup && \

prefect --no-prompt deploy production_flow.py:production_main -p main_pool -n Production && \

prefect server start &

mlflow ui --backend-store-uri sqlite:///mlflow.db &

optuna-dashboard sqlite:///optuna_lstm.db &

echo "All services started"

wait