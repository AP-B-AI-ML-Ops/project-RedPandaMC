-- Drop schemas if they exist
DROP SCHEMA IF EXISTS "training" CASCADE;
DROP SCHEMA IF EXISTS "validation" CASCADE;
DROP SCHEMA IF EXISTS "testing" CASCADE;
DROP SCHEMA IF EXISTS "recent" CASCADE;
DROP SCHEMA IF EXISTS "prediction" CASCADE;

-- Create schemas
CREATE SCHEMA IF NOT EXISTS "training";
CREATE SCHEMA IF NOT EXISTS "validation";
CREATE SCHEMA IF NOT EXISTS "testing";
CREATE SCHEMA IF NOT EXISTS "recent";
CREATE SCHEMA IF NOT EXISTS "prediction";

-- Create tables in respective schemas
CREATE TABLE IF NOT EXISTS "training"."training_data" (
    "PriceUSD" REAL,
    "Date" TIMESTAMP
);

CREATE TABLE IF NOT EXISTS "validation"."validation_data" (
    "PriceUSD" REAL,
    "Date" TIMESTAMP
);

CREATE TABLE IF NOT EXISTS "testing"."testing_data" (
    "PriceUSD" REAL,
    "Date" TIMESTAMP
);

CREATE TABLE IF NOT EXISTS "recent"."recent_data" (
    "PriceUSD" REAL,
    "Date" TIMESTAMP
);

CREATE TABLE IF NOT EXISTS "prediction"."predicted_data" (
    "PriceUSDPredicted" REAL,
    "FutureDate" TIMESTAMP
);
