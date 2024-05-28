-- Drop schemas if they exist
DROP SCHEMA IF EXISTS "mlops" CASCADE;
CREATE SCHEMA "mlops";

CREATE TABLE mlops.trainingdata (
    "PriceUSD" FLOAT,
    "Time" TIMESTAMP
);

CREATE TABLE mlops.validationdata (
    "PriceUSD" FLOAT,
    "Time" TIMESTAMP
);

CREATE TABLE mlops.testingdata (
    "PriceUSD" FLOAT,
    "Time" TIMESTAMP
);

CREATE TABLE mlops.recentdata (
    "PriceUSD" FLOAT,
    "Time" TIMESTAMP
);

CREATE TABLE mlops.predicteddata (
    "PriceUSD" FLOAT,
    "Time" TIMESTAMP
);