#!/bin/bash

start_services() {
    prefect init --recipe local && \

    prefect worker start -t process -p main_pool &
    WORKER_PID=$!

    prefect --no-prompt deploy main_flow.py:main_flow -p main_pool

    prefect server start &
    SERVER_PID=$!

    mlflow ui --backend-store-uri sqlite:///mlflow_db &
    MLFLOW_PID=$!

    optuna-dashboard sqlite:///optuna_lstm.db &
    OPTUNA_PID=$!

    echo "All services started"

    wait $SERVER_PID $WORKER_PID $MLFLOW_PID $OPTUNA_PID
}

trap 'echo "Stopping services..."; pkill -P $$; exit 1' SIGINT

start_services