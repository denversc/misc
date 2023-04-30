from __future__ import annotations

import argparse
from collections.abc import Sequence
import dataclasses
import datetime
import io
import statistics
import sys
from typing import Callable, Iterable
import unittest
from unittest import mock


def main():
  argument_parser = MyArgumentParser()
  parsed_args = argument_parser.parse()

  if parsed_args.run_unit_tests:
    return unittest.main(argv=[sys.argv[0]])

  calculator = InterestPenaltyCalculator(
      amount=parsed_args.amount,
      start_date=parsed_args.start_date,
      end_date=parsed_args.end_date,
      chart_writer_factory=TableWriter if parsed_args.show_chart else None,
  )

  calculator.run()


class InterestPenaltyCalculator:

  def __init__(
      self,
      amount: float,
      start_date: datetime.date,
      end_date: datetime.date,
      chart_writer_factory: Callable[[Iterable[str]], TableWriter] | None,
  ) -> None:
    self.amount = amount
    self.start_date = start_date
    self.end_date = end_date
    self.chart_writer_factory = chart_writer_factory

  def run(self):
    if self.chart_writer_factory is None:
      chart_writer = None
    else:
      chart_writer = self.chart_writer_factory([
          "Date",
          "Opening Balance",
          "Interest Rate",
          "Interest",
          "New Balance",
      ])

    current_date = self.start_date
    balance = self.amount
    accrued_interest = 0.0
    num_days = 0
    interest_rates_per_year: list[float] = []
    while current_date <= self.end_date:
      num_days += 1
      current_interest_rate_per_year = interest_rate_for_date(current_date)
      current_interest_rate_per_day = current_interest_rate_per_year / 365
      interest_rates_per_year.append(current_interest_rate_per_year)
      current_interest = balance * current_interest_rate_per_day
      old_balance = balance
      balance += current_interest
      accrued_interest += current_interest
      if chart_writer is not None:
        chart_writer.add_row([
            "{0.year:04}-{0.month:02}-{0.day:02}".format(current_date),
            f"${old_balance:.6f}",
            f"{current_interest_rate_per_year:.2f} ({current_interest_rate_per_day:.12f} per day)",
            f"${current_interest:.9f}",
            f"${balance:.6f}",
        ])

      current_date += datetime.timedelta(days=1)

    if chart_writer is not None:
      chart_writer.print(self.print)
      self.print()

    self.print(f"Start Date: {self.start_date}")
    self.print(f"End Date: {self.end_date} ({num_days} days)")
    self.print(f"Average Interest Rate: {statistics.mean(interest_rates_per_year):.6f}")
    self.print(f"Principal Amount: ${self.amount:.2f}")
    self.print(f"Accrued Interest: ${accrued_interest:.2f}")
    self.print(f"Principal + Interest: ${balance:.2f}")
  
  def print(self, text: str | None = None) -> None:
    if text is None:
      print("")
    else:
      print(text)


class TableWriter:

  def __init__(self, columns: Iterable[str]) -> None:
    self.columns = tuple(columns)
    self.rows = []

  def add_row(self, row: Iterable[str]) -> None:
    row = tuple(row)
    if len(row) != len(self.columns):
      raise ValueError(f"invalid row length: f{len(row)} (expected f{len(self.columns)})")
    self.rows.append(row)

  def print(self, print_func: Callable[[str | None], None]) -> None:

    column_widths = self.calculate_column_widths()

    def print_joined_iterable(chunks: Iterable[str]) -> None:
      print_func("".join(chunks))
    print_joined_iterable(self.line_chunks(self.columns, column_widths))
    print_joined_iterable(self.divider(column_widths))
    for row in self.rows:
      print_joined_iterable(self.line_chunks(row, column_widths))

  def calculate_column_widths(self) -> Sequence[int]:
    widths = [len(column_title) for column_title in self.columns]
    for row in self.rows:
      for (i, cell) in enumerate(row):
        current_width = len(cell)
        if current_width > widths[i]:
          widths[i] = current_width
    return tuple(widths)
  
  @staticmethod
  def line_chunks(values: Sequence[str], widths: Sequence[int]) -> Iterable[str]:
    for column_index in range(len(widths)):
      value = values[column_index]
      width = widths[column_index]

      if column_index > 0:
        yield " | "

      yield value

      yield " " * (width - len(value))

  @staticmethod
  def divider(widths: Sequence[int]) -> Iterable[str]:
    for column_index in range(len(widths)):
      width = widths[column_index]

      if column_index > 0:
        yield "-|-"
      yield "-" * width



class MyArgumentParser:

  def __init__(self):
    self.parser = argparse.ArgumentParser()

    def date_parse(s: str) -> datetime.date:
      return datetime.date.fromisoformat(s)

    def formatted_date(d: datetime.date) -> str:
      return f"{d.year:04}-{d.month:02}-{d.day:02}"

    self.default_start = datetime.date(2022, 1, 1)
    self.default_end = self._today()
    self.default_amount = 100.0

    self.parser.add_argument(
        "--test",
        action="store_true",
        default=False,
        help=f"""Run a suite of unit tests on this application, then exits."""
    )
    self.parser.add_argument(
        "--chart",
        action="store_true",
        default=False,
        help=f"""Show a chart of each individual calculation in the total compound interest."""
    )
    self.parser.add_argument(
        "--start",
        type=date_parse,
        help=f"""The date at which interest begins accumulating (e.g. 2023-12-31);
          If not specified, {formatted_date(self.default_start)} is used arbitrarily."""
    )
    self.parser.add_argument(
        "--end",
        type=date_parse,
        help=f"""The date at which interest ends accumulating (e.g. 2023-12-31);
          If not specified, today's date, {formatted_date(self.default_end)}, is used."""
    )
    self.parser.add_argument(
        "--amount",
        type=float,
        help=f"""The dollar amount whose interest to calculate;
          if not specified, {self.default_amount:.2f} is used arbitrarily."""
    )

  def parse(self, args: Sequence[str] | None = None) -> ParsedArgs:
    parsed_arguments = self.parser.parse_args(args=args)

    if parsed_arguments.start is not None:
      start_date = parsed_arguments.start
    else:
      start_date = self.default_start

    if parsed_arguments.end is not None:
      end_date = parsed_arguments.end
    else:
      end_date = self.default_end

    if parsed_arguments.amount is not None:
      amount = parsed_arguments.amount
    else:
      amount = self.default_amount

    return self.ParsedArgs(
        run_unit_tests=parsed_arguments.test,
        amount=amount,
        start_date=start_date,
        end_date=end_date,
        show_chart=parsed_arguments.chart,
    )

  def _today(self) -> datetime.date:
    return datetime.date.today()

  @dataclasses.dataclass(frozen=True)
  class ParsedArgs:
    run_unit_tests: bool
    amount: float
    start_date: datetime.date
    end_date: datetime.date
    show_chart: bool

  class ParseError(Exception):
    pass


@dataclasses.dataclass(frozen=True)
class InterestRateTableRow:
  start_date: datetime.date
  interest_rate: float | None

def interest_rate_table() -> tuple[InterestRateTableRow, ...]:
  return(
    InterestRateTableRow(datetime.date(2020, 4, 1), 0.06),
    InterestRateTableRow(datetime.date(2020, 7, 1), 0.05),
    InterestRateTableRow(datetime.date(2020, 10, 1), 0.05),
    InterestRateTableRow(datetime.date(2021, 1, 1), 0.05),
    InterestRateTableRow(datetime.date(2021, 4, 1), 0.05),
    InterestRateTableRow(datetime.date(2021, 7, 1), 0.05),
    InterestRateTableRow(datetime.date(2021, 10, 1), 0.05),
    InterestRateTableRow(datetime.date(2022, 1, 1), 0.05),
    InterestRateTableRow(datetime.date(2022, 4, 1), 0.05),
    InterestRateTableRow(datetime.date(2022, 7, 1), 0.06),
    InterestRateTableRow(datetime.date(2022, 10, 1), 0.07),
    InterestRateTableRow(datetime.date(2023, 1, 1), 0.08),
    InterestRateTableRow(datetime.date(2023, 4, 1), 0.09),
    InterestRateTableRow(datetime.date(2023, 7, 1), None),
  )


def interest_rate_for_date(d: datetime.date) -> float:
  table = interest_rate_table()

  for i in range(len(table)):
    if d < table[i].start_date:
      i -= 1
      break

  if i < 0:
    raise ValueError(f"date is too far in the past: {d}; "
        f"the earliest date supported is {table[0].start_date}")
  elif i == len(table) - 1:
    raise ValueError(f"date is too far in the future: {d}; "
        f"the latest date supported is {table[-1].start_date}")

  return table[i].interest_rate


class MyArgumentParserTest(unittest.TestCase):

  def test_defaults(self):
    with mock.patch.object(MyArgumentParser, "_today", spec_set=True, autospec=True,
        return_value=datetime.date(2023, 12, 23)):
      parser = MyArgumentParser()
      result = parser.parse([])

    self.assertFalse(result.run_unit_tests)
    self.assertEqual(result.start_date, datetime.date(2022, 1, 1))
    self.assertEqual(result.end_date, datetime.date(2023, 12, 23))
    self.assertEqual(result.amount, 100)
    self.assertFalse(result.show_chart)

  def test_test(self):
    parser = MyArgumentParser()
    result = parser.parse(["--test"])
    self.assertTrue(result.run_unit_tests)

  def test_amount(self):
    parser = MyArgumentParser()
    result = parser.parse(["--amount", "1.23"])
    self.assertEqual(result.amount, 1.23)

  def test_start(self):
    parser = MyArgumentParser()
    result = parser.parse(["--start", "1981-11-21"])
    self.assertEqual(result.start_date, datetime.date(1981, 11, 21))

  def test_end(self):
    parser = MyArgumentParser()
    result = parser.parse(["--end", "2021-11-23"])
    self.assertEqual(result.end_date, datetime.date(2021, 11, 23))

  def test_chart(self):
    parser = MyArgumentParser()
    result = parser.parse(["--chart"])
    self.assertTrue(result.show_chart)


class InterestRateTableTest(unittest.TestCase):

  def test_ends_with_interest_rate_none(self):
    table = interest_rate_table()
    self.assertIsNone(table[-1].interest_rate)

  def test_only_the_last_element_has_interest_rate_none(self):
    table = interest_rate_table()[:-1]
    for i in range(len(table)):
      with self.subTest(i=i):
        self.assertIsNotNone(table[i].interest_rate)

  def test_elements_are_sorted(self):
    table = interest_rate_table()
    actual_start_dates = [row.start_date for row in table]
    expected_start_dates = sorted(actual_start_dates)
    self.assertEqual(actual_start_dates, expected_start_dates)


class InterestRateByDateTest(unittest.TestCase):

  def test_raise_value_error_if_date_is_too_far_in_the_past(self):
    with self.assertRaisesRegex(ValueError, "(?i)in the past"):
      interest_rate_for_date(datetime.date(1, 1, 1))
    with self.assertRaisesRegex(ValueError, "(?i)in the past"):
      interest_rate_for_date(datetime.date(2020, 3, 31))

  def test_raise_value_error_if_date_is_too_far_in_the_future(self):
    with self.assertRaisesRegex(ValueError, "(?i)in the future"):
      interest_rate_for_date(datetime.date(9999, 12, 31))
    with self.assertRaisesRegex(ValueError, "(?i)in the future"):
      interest_rate_for_date(datetime.date(2023, 7, 1))

  def test_values(self):
    cases = [
        (datetime.date(2020, 4, 1), 0.06),
        (datetime.date(2020, 4, 2), 0.06),
        (datetime.date(2020, 5, 2), 0.06),
        (datetime.date(2020, 6, 2), 0.06),
        (datetime.date(2020, 6, 30), 0.06),
        (datetime.date(2023, 1, 1), 0.08),
        (datetime.date(2023, 2, 1), 0.08),
        (datetime.date(2023, 4, 6), 0.09),
        (datetime.date(2023, 6, 30), 0.09),
        (datetime.date(2023, 6, 30), 0.09),
    ]
    for (d, expected_interest_rate) in cases:
      with self.subTest(date=d):
        self.assertEqual(interest_rate_for_date(d), expected_interest_rate)


if __name__ == "__main__":
  main()
