DROP SCHEMA IF EXISTS training CASCADE;
DROP SCHEMA IF EXISTS validation CASCADE;
DROP SCHEMA IF EXISTS testing CASCADE;
DROP SCHEMA IF EXISTS recent CASCADE;
DROP SCHEMA IF EXISTS prediction CASCADE;

CREATE SCHEMA training;

CREATE TABLE training.training_data (
    "PriceUSD" FLOAT,
    "Date" TIMESTAMP
);

CREATE SCHEMA validation;

CREATE TABLE validation.validation_data (
    "PriceUSD" FLOAT,
    "Date" TIMESTAMP
);

CREATE SCHEMA testing;

CREATE TABLE testing.testing_data (
    "PriceUSD" FLOAT,
    "Date" TIMESTAMP
);

CREATE SCHEMA recent;

CREATE TABLE recent.recent_data (
    "PriceUSD" FLOAT,
    "Date" TIMESTAMP,
);

CREATE SCHEMA prediction;

CREATE TABLE prediction.predicted_data (
    "PriceUSDPredicted" FLOAT,
    "FutureDate" TIMESTAMP
);