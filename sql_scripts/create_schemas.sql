DROP SCHEMA IF EXISTS training CASCADE;
DROP SCHEMA IF EXISTS validation CASCADE;
DROP SCHEMA IF EXISTS testing CASCADE;
DROP SCHEMA IF EXISTS recent CASCADE;

CREATE SCHEMA training;

CREATE TABLE training.training_data (
    "PriceUSD" FLOAT,
    "CirculatingSupply" INTEGER,
    "Date" TIMESTAMP
);

CREATE SCHEMA validation;

CREATE TABLE validation.validation_data (
    "PriceUSD" FLOAT,
    "CirculatingSupply" INTEGER,
    "Date" TIMESTAMP
);

CREATE SCHEMA testing;

CREATE TABLE testing.testing_data (
    "PriceUSD" FLOAT,
    "CirculatingSupply" INTEGER,
    "Date" TIMESTAMP
);

CREATE SCHEMA recent;

CREATE TABLE recent.recent_data (
    "PriceUSD" FLOAT,
    "CirculatingSupply" INTEGER,
    "Date" TIMESTAMP
);