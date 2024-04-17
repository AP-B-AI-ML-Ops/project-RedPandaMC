# Cryptocurrency Price Forecasting Project💰

## Overview
This project aims to utilize the [CoinCap API](https://docs.coincap.io/) to forecast the prices of cryptocurrencies, such as Bitcoin. The process involves normalizing the data using Prefect flows and tasks, automating the workflow with Prefect's scheduling feature, and experimenting with MLflow to identify the optimal model for forecasting.

## Components
<ul>
  <li>💹 <strong>CoinCap API Integration:</strong> Utilize CoinCap API to retrieve cryptocurrency price data.</li>
  <li>📊 <strong>Data Normalization:</strong> Implement Prefect flows and tasks to normalize the obtained data.</li>
  <li>🔄 <strong>Workflow Automation:</strong> Utilize Prefect's scheduling feature to automate the entire process.</li>
  <li>🧪 <strong>Model Experimentation:</strong> Employ MLflow to experiment with different forecasting models and identify the best-performing one.</li>
</ul>

## How will it work? 🤔
### How will I retrieve my data?

The api which I aim to utilize offers a REST API with a specific GET request that allows me to get a the open, close, high, low and volume of a given coin on a given exchange that is supplied by [coincap.io](https://coincap.io/). I intend to execute a GET request to obtain data on the Bitcoin/Euro exchange rate spanning from seven days prior to the project's initiation until the present moment. This data will be segmented into intervals of five minutes, resulting in approximately 2016 data points, which will serve as the basis for training a model. Subsequently, I will partition the dataset into a test set comprising 24 data points and a training set consisting of 1992 data points. It's worth noting that the specific timeframe for the test data may be adjusted, but as currently planned, it will encompass the last two hours prior to project initialization.

[API Docs](https://docs.coincap.io/#51da64d7-b83b-4fac-824f-3f06b6c8d944)

### Which model will i use?

For this project, I intend to explore the use of Neural Networks, particularly focusing on an LSTM (Long Short-Term Memory) model, which falls under the category of Recurrent Neural Network (RNN) models. Why? I believe this project is the perfect opportunity to get a deeper understanding of LSTM's.

### How do i envision the model retrain pipeline?

When the model is getting too off track of the current market and the quality of the results are declining. I intend to run the same process as the first retrain to replace the old model.

### Monitoring

I think monitoring the actual real data vs the forecast data is probably the best way to monitor the models quality.  

## The task and flows

<div style="display: flex; justify-content: space-around;">

  <div style="flex-grow: 1;">
    <h4>Initialization</h4>
    <ul>
      <li>Load data
        <ul>
          <li>Make an API call for data prior 7 days</li>
        </ul>
      </li>
      <li>Preprocess data
        <ul>
          <li>Remove certain aspects of the data that are not important</li>
        </ul>
      </li>
      <li>Split data in train and test</li>
      <li>Hyperparameter tune model</li>
      <li>Train model</li>
      <li>Select best model via mlflow</li>
      <li>Promote best model to production</li>
    </ul>
  </div>

  <div style="flex-grow: 1;">
    <h4>Production</h4>
    <ul>
      <li>Load production model</li>
      <li>Scheduled flow of getting data from coincap every 5 minutes</li>
      <li>Put this data in database</li>
      <li>Use gotten data to forecast next 5 minutes</li>
      <li>Put this forecast in database</li>
    </ul>
  </div>

  <div style="flex-grow: 1;">
    <h4>Retrain</h4>
    <ul>
      <li>Flush database</li>
      <li>Load data
        <ul>
          <li>Make an API call</li>
        </ul>
      </li>
      <li>Preprocess data
        <ul>
          <li>Remove certain aspects of the data that are not important</li>
        </ul>
      </li>
      <li>Split data in train and test</li>
      <li>Hyperparameter tune & train model</li>
      <li>Select best model via mlflow</li>
      <li>Promote best model to production</li>
    </ul>
  </div>

</div>

<details>
  <summary>p.s.</summary>
  The actual flows & tasks may differ but this a good jumping off point.
</details>
