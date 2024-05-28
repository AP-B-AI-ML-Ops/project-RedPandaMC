import pandas as pd

import pytest
from data.api_data_to_df_flow import api_data_to_df, convert_data_to_json, convert_json_to_df
from data.clean_data_flow import clean_data

# Sample JSON data for testing
valid_json_data_string = """
{
    "data": [
        {
            "time": 1621484785890,
            "date": "2022-05-20",
            "priceUsd": "0.8",
            "circulatingSupply": "1000000"
        }
    ]
}
"""

invalid_json_data_string = """
{
    "data": [
        {
            "time": 1621484785890,
            "date": "2022-05-20",
            "priceUsd": "0.8",
            "circulatingSupply": "1000000"
        }
    ]
"""  # Missing closing brace

empty_json_data_string = """
{
    "data": []
}
"""


@pytest.mark.parametrize(
    "json_data_string,expected_output",
    [
        (
            valid_json_data_string,
            [
                {
                    "time": 1621484785890,
                    "date": "2022-05-20",
                    "priceUsd": "0.8",
                    "circulatingSupply": "1000000",
                }
            ],
        ),
        (invalid_json_data_string, None),
        (empty_json_data_string, []),
    ],
)
def test_convert_data_to_json(json_data_string, expected_output):
    result = convert_data_to_json.fn(json_data_string)
    assert result == expected_output


def test_convert_json_to_df():
    json_data = [
        {
            "time": 1621484785890,
            "date": "2022-05-20",
            "priceUsd": "0.8",
            "circulatingSupply": "1000000",
        }
    ]
    expected_df = pd.DataFrame(json_data)
    expected_df["time"] = pd.to_datetime(expected_df["time"], unit="ms")
    expected_df["date"] = pd.to_datetime(expected_df["date"])
    expected_df["priceUsd"] = pd.to_numeric(expected_df["priceUsd"])
    expected_df["circulatingSupply"] = pd.to_numeric(expected_df["circulatingSupply"])
    expected_df["circulatingSupply"] = expected_df["circulatingSupply"].astype(int)

    result_df = convert_json_to_df.fn(json_data)
    pd.testing.assert_frame_equal(result_df, expected_df)


def test_clean_data():
    # Create a sample DataFrame for testing
    sample_data = {
        "time": [1621484785890, 1621484785891],
        "date": ["2022-05-20", "2022-05-21"],
        "priceUsd": ["0.8", "0.9"],
        "circulatingSupply": ["1000000", "2000000"],
    }
    df = pd.DataFrame(sample_data)

    # Expected DataFrame after cleaning
    expected_data = {"Time": [1621484785890, 1621484785891], "PriceUSD": ["0.8", "0.9"]}
    expected_df = pd.DataFrame(expected_data)

    # Run the clean_data function
    result_df = clean_data(df)

    # Check if the resulting DataFrame matches the expected DataFrame
    pd.testing.assert_frame_equal(result_df, expected_df)


if __name__ == "__main__":
    pytest.main()
