import pandas as pd
from datetime import datetime
from m365client.date_table import DateTableTransformStrategy, create_default_date_dataframe


def test_transform_should_create_date_table_with_expected_columns():
    # Create a test DataFrame
    dates = pd.date_range(start='2022-01-01', end='2022-01-10', freq='D')
    df = pd.DataFrame({'Date': dates})

    # Create a DateTableTransformStrategy object
    strategy = DateTableTransformStrategy([df], ['Date'])

    # Call the transform method
    result = strategy.transform()

    # Check that the result has the expected columns
    expected_columns = ['Date', 'Year', 'Month', 'MonthName', 'Day', 'Quarter', 'QuarterName', 'DayOfWeek', 'DayName', 'DayOfYear', 'WeekOfYear', 'IsWeekend', 'IsMonthStart', 'IsMonthEnd', 'IsQuarterStart', 'IsQuarterEnd', 'IsYearStart', 'IsYearEnd', 'WeekOfQuarter', 'DayOfQuarter', 'MonthOfQuarter', 'WeekOfMonth', 'SortableMonthYear', 'HolidayName']
    assert list(result.columns) == expected_columns


def test_transform_should_create_date_table_with_expected_rows():
    # Create a test DataFrame
    dates = pd.date_range(start='2022-01-01', end='2022-01-10', freq='D')
    df = pd.DataFrame({'Date': dates})

    # Create a DateTableTransformStrategy object
    strategy = DateTableTransformStrategy([df], ['Date'])

    # Call the transform method
    result = strategy.transform()

    # Check that the result has the expected number of rows
    assert len(result) == 10

def test_should_create_date_table_max_and_min_in_list_of_dfs():
    # Given multiple DataFrames with different date ranges create a date table with the earliest date
    dates1 = pd.date_range(start='2022-01-02', end='2022-01-10', freq='D')
    dates2 = pd.date_range(start='2022-01-01', end='2022-01-15', freq='D')
    dates3 = pd.date_range(start='2022-01-08', end='2022-01-18', freq='D')

    df1 = pd.DataFrame({'Date': dates1})
    df2 = pd.DataFrame({'Date': dates2})
    df3 = pd.DataFrame({'Date': dates3})

    # Create a DateTableTransformStrategy object
    strategy = DateTableTransformStrategy([df1, df2, df3], ['Date', 'Date', 'Date'])

    # Call the transform method
    result = strategy.transform()

    # Check that the first and last dates are as expected
    assert result['Date'].min() == pd.Timestamp('2022-01-01')
    assert result['Date'].max() == pd.Timestamp('2022-01-18')

def test_create_default_date_dataframe_should_create_dataframe_with_expected_columns():
    # Call the create_default_date_dataframe function
    result = create_default_date_dataframe()

    # Check that the result has the expected columns
    expected_columns = ['Date']
    assert list(result.columns) == expected_columns


def test_create_default_date_dataframe_should_create_dataframe_with_expected_rows():
    # Call the create_default_date_dataframe function
    result = create_default_date_dataframe()

    # Check that the result has the expected number of rows
    expected_rows = (datetime(2034, 12, 31).date() - datetime.now().date()).days + 1
    assert len(result) == expected_rows