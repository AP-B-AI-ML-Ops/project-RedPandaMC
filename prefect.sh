#!/bin/bash

prefect init --recipe local && \

prefect worker start -t process -p main_pool &

prefect --no-prompt deploy main_flow.py:main_flow -p main_pool -n Setup && \

prefect server start

mlflow ui --backend-store-uri sqlite:///mlflow_db &

optuna-dashboard sqlite:///optuna_lstm.db &

echo "All services started"

wait