from typing import List, Optional
from datetime import datetime, timedelta
import pandas as pd
from loguru import logger
from pandas.tseries.holiday import USFederalHolidayCalendar


def week_of_year(dates):
    return [
        (
            (date - timedelta(days=date.weekday()))
            - (
                date.replace(month=1, day=1)
                - timedelta(days=date.replace(month=1, day=1).weekday())
            )
        ).days
        // 7
        + 1
        for date in dates
    ]


class DateTableTransformStrategy:
    """
    Transformation strategy for creating a date table from a date series.

    Attributes:
        df (pd.DataFrame): The input DataFrame.
        date_col (str): The column name for the date data in the DataFrame.
        included_features (List[str]): The list of date features to include in the date table.
    """

    FEATURE_GENERATORS = {
        "Year": lambda dates: dates.year,
        "Month": lambda dates: dates.month,
        "MonthName": lambda dates: dates.strftime("%B"),
        "Day": lambda dates: dates.day,
        "Quarter": lambda dates: dates.quarter,
        "QuarterName": lambda dates: "Q" + dates.quarter.astype(str),
        "DayOfWeek": lambda dates: dates.dayofweek,
        "DayName": lambda dates: dates.strftime("%A"),
        "DayOfYear": lambda dates: dates.dayofyear,
        "WeekOfYear": lambda dates: week_of_year(dates),
        "IsWeekend": lambda dates: dates.weekday >= 5,
        "IsMonthStart": lambda dates: dates.is_month_start,
        "IsMonthEnd": lambda dates: dates.is_month_end,
        "IsQuarterStart": lambda dates: dates.is_quarter_start,
        "IsQuarterEnd": lambda dates: dates.is_quarter_end,
        "IsYearStart": lambda dates: dates.is_year_start,
        "IsYearEnd": lambda dates: dates.is_year_end,
        "WeekOfQuarter": lambda dates: (dates.isocalendar().week - 1) % 13 + 1,
        "DayOfQuarter": lambda dates: (dates - dates.to_period("Q").to_timestamp()).days
        + 1,
        "MonthOfQuarter": lambda dates: (dates.month - 1) % 3 + 1,
        "WeekOfMonth": lambda dates: (dates.day - 1) // 7 + 1,
        "SortableMonthYear": lambda dates: dates.strftime("%Y%m"),
    }

    def __init__(
        self,
        dfs: List[pd.DataFrame],
        date_cols: List[str],
        included_features: Optional[List[str]] = None,
    ):
        """
        Initializes the DateTableTransformStrategy class.

        Args:
            dfs (List[pd.DataFrame]): The list of input DataFrames.
            date_cols (List[str]): The column names for the date data in the DataFrames.
            included_features (Optional[List[str]]): The list of date features to include in the date table. If None, all features are included.
        """
        logger.info("Initializing DateTableTransformStrategy...")
        logger.info("Date columns: %s", date_cols)
        self.dfs = dfs
        self.date_cols = date_cols
        self.included_features = (
            included_features
            if included_features is not None
            else self.FEATURE_GENERATORS.keys()
        )

    def transform(self) -> pd.DataFrame:
        """
        Transforms a list of date series into a date table.

        Returns:
            pd.DataFrame: The transformed DataFrame.

        Raises:
            Exception: If there's any error during the transformation process.
        """
        logger.info("Finding min and max dates...")
        min_date = pd.Timestamp.max
        max_date = pd.Timestamp.min
        for df in self.dfs:
            date_series = df[self.date_cols].apply(pd.to_datetime)
            min_date = min(min_date, date_series.min().min())
            max_date = max(max_date, date_series.max().max())
        logger.info("Min date: %s", min_date)
        logger.info("Max date: %s", max_date)
        dates = pd.date_range(min_date, max_date)

        date_table = pd.DataFrame({"Date": dates})

        for feature in self.included_features:
            if feature in self.FEATURE_GENERATORS:
                generator = self.FEATURE_GENERATORS[feature]
                date_table[feature] = generator(dates)
            else:
                logger.warning(f"Unknown feature: {feature}")

        logger.info("Creating holiday table...")
        logger.info(date_table.head(10))

        cal = USFederalHolidayCalendar()
        holidays = cal.holidays(start=min_date, end=max_date, return_name=True)
        holidays = holidays.reset_index().rename(
            columns={"index": "Date", 0: "HolidayName"}
        )
        date_table = pd.merge(date_table, holidays, on="Date", how="left")

        return date_table


def create_default_date_dataframe():
    current_date = datetime.now().date()
    end_date = datetime(2034, 12, 31).date()

    dates = pd.date_range(start=current_date, end=end_date, freq="D")
    df = pd.DataFrame({"Date": dates})

    return df
