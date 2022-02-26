# -*- coding: utf-8 -*-

# This file is part of wger Workout Manager.
#
# wger Workout Manager is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# wger Workout Manager is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License

# Standard Library
import csv
import datetime
import decimal
import io
import json
import logging
from collections import OrderedDict

# Django
from django.core.cache import cache

# wger
from wger.manager.models import (
    WorkoutLog,
    WorkoutSession,
)
from wger.utils.cache import cache_mapper
from wger.utils.helpers import DecimalJsonEncoder
from wger.weight.models import WeightEntry


logger = logging.getLogger(__name__)


def parse_weight_csv(request, cleaned_data):

    try:
        dialect = csv.Sniffer().sniff(cleaned_data['csv_input'])
    except csv.Error:
        dialect = 'excel'

    # csv.reader expects a file-like object, so use StringIO
    parsed_csv = csv.reader(io.StringIO(cleaned_data['csv_input']), dialect)
    distinct_weight_entries = []
    entry_dates = set()
    weight_list = []
    error_list = []
    MAX_ROW_COUNT = 1000
    row_count = 0

    # Process the CSV items first
    for row in parsed_csv:
        try:
            parsed_date = datetime.datetime.strptime(row[0], cleaned_data['date_format'])
            parsed_weight = decimal.Decimal(row[1].replace(',', '.'))
            duplicate_date_in_db = WeightEntry.objects.filter(date=parsed_date,
                                                              user=request.user).exists()
            # within the list there are no duplicate dates
            unique_among_csv = parsed_date not in entry_dates

            # there is no existing weight entry in the database for that date
            unique_in_db = not duplicate_date_in_db

            if unique_among_csv and unique_in_db and parsed_weight:
                distinct_weight_entries.append((parsed_date, parsed_weight))
                entry_dates.add(parsed_date)
            else:
                error_list.append(row)

        except (ValueError, IndexError, decimal.InvalidOperation):
            error_list.append(row)
        row_count += 1
        if row_count > MAX_ROW_COUNT:
            break

    # Create the valid weight entries
    for date, weight in distinct_weight_entries:
        weight_list.append(WeightEntry(date=date, weight=weight, user=request.user))

    return (weight_list, error_list)


def group_log_entries(user, year, month, day=None):
    """
    Processes and regroups a list of log entries so they can be more easily
    used in the different calendar pages

    :param user: the user to filter the logs for
    :param year: year
    :param month: month
    :param day: optional, day

    :return: a dictionary with grouped logs by date and exercise
    """
    if day:
        log_hash = hash((user.pk, year, month, day))
    else:
        log_hash = hash((user.pk, year, month))

    # There can be workout sessions without any associated log entries, so it is
    # not enough so simply iterate through the logs
    if day:
        filter_date = datetime.date(year, month, day)
        logs = WorkoutLog.objects.filter(user=user, date=filter_date)
        sessions = WorkoutSession.objects.filter(user=user, date=filter_date)

    else:
        logs = WorkoutLog.objects.filter(user=user, date__year=year, date__month=month)

        sessions = WorkoutSession.objects.filter(user=user, date__year=year, date__month=month)

    logs = logs.order_by('date', 'id')
    out = cache.get(cache_mapper.get_workout_log_list(log_hash))
    # out = OrderedDict()

    if not out:
        out = OrderedDict()

        # Logs
        for entry in logs:
            if not out.get(entry.date):
                out[entry.date] = {
                    'date': entry.date,
                    'workout': entry.workout,
                    'session': entry.get_workout_session(),
                    'logs': OrderedDict()
                }

            if not out[entry.date]['logs'].get(entry.exercise):
                out[entry.date]['logs'][entry.exercise] = []

            out[entry.date]['logs'][entry.exercise].append(entry)

        # Sessions
        for entry in sessions:
            if not out.get(entry.date):
                out[entry.date] = {
                    'date': entry.date,
                    'workout': entry.workout,
                    'session': entry,
                    'logs': {}
                }

        cache.set(cache_mapper.get_workout_log_list(log_hash), out)
    return out


def approximate_rm(logs):
    """
    Approximate 1 rm from the last 0 rir unit
    """

    # https://aesirsports.de/autoregulation-training-rpe-rir/
    trans_map = {
        '0': {
            1: 1.00,
            2: 0.95,
            3: 0.90,
            4: 0.85,
            5: 0.80,
            6: 0.77,
            7: 0.74,
            8: 0.71,
            9: 0.69,
            10: 0.66,
            11: 0.64,
            12: 0.62
        },
        '0.5': {
            1: 0.98,
            2: 0.93,
            3: 0.88,
            4: 0.83,
            5: 0.79,
            6: 0.76,
            7: 0.73,
            8: 0.70,
            9: 0.67,
            10: 0.65,
            11: 0.63
        },
        '1': {
            1: 0.95,
            2: 0.90,
            3: 0.85,
            4: 0.80,
            5: 0.77,
            6: 0.74,
            7: 0.71,
            8: 0.69,
            9: 0.66,
            10: 0.64,
            11: 0.62
        },
        '1.5': {
            1: 0.93,
            2: 0.88,
            3: 0.83,
            4: 0.79,
            5: 0.76,
            6: 0.73,
            7: 0.70,
            8: 0.67,
            9: 0.65,
            10: 0.63
        },
        '2': {
            1: 0.90,
            2: 0.85,
            3: 0.80,
            4: 0.77,
            5: 0.74,
            6: 0.71,
            7: 0.69,
            8: 0.66,
            9: 0.64,
            10: 0.62
        },
        '2.5': {
            1: 0.85,
            2: 0.80,
            3: 0.77,
            4: 0.74,
            5: 0.71,
            6: 0.69,
            7: 0.66,
            8: 0.64,
            9: 0.62
        },
        '3': {
            1: 0.80,
            2: 0.77,
            3: 0.74,
            4: 0.71,
            5: 0.69,
            6: 0.66,
            7: 0.64,
            8: 0.62
        }
    }

    valid_logs = OrderedDict()
    for entry in logs:
        if entry.repetition_unit.name == 'Repetitions' and entry.weight_unit.name == 'kg' and (
            (entry.rir == '0' and entry.reps <= 12) or (entry.rir == '0.5' and entry.reps <= 11) or
            (entry.rir == '1' and entry.reps <= 11) or (entry.rir == '1.5' and entry.reps <= 10) or
            (entry.rir == '2' and entry.reps <= 10) or (entry.rir == '2.5' and entry.reps <= 9) or
            (entry.rir == '3' and entry.reps <= 8)
        ):
            if not valid_logs.get(entry.date):
                valid_logs[entry.date] = entry
            elif valid_logs[entry.date].rir > entry.rir or (
                valid_logs[entry.date].reps > entry.reps and valid_logs[entry.date].rir == entry.rir
            ):
                valid_logs[entry.date] = entry

    if len(valid_logs) <= 0:
        return None

    last_valid_log = valid_logs[next(reversed(valid_logs))]
    percent_max = trans_map[last_valid_log.rir][last_valid_log.reps]
    one_rm = last_valid_log.weight / decimal.Decimal(percent_max)
    return round(one_rm, 0)


def process_log_entries(logs):
    """
    Processes and regroups a list of log entries so they can be rendered
    and passed to the D3 library to render a chart
    """

    entry_log = OrderedDict()
    entry_list = {}
    chart_data = []
    max_weight = {}

    # Group by date
    for entry in logs:

        if not entry_log.get(entry.date):
            entry_log[entry.date] = []
        entry_log[entry.date].append(entry)

        # Find the maximum weight per date per repetition.
        # If on a day there are several entries with the same number of
        # repetitions, but different weights, only the entry with the
        # higher weight is shown in the chart
        if not max_weight.get(entry.date):
            max_weight[entry.date] = {entry.reps: entry.weight}

        if not max_weight[entry.date].get(entry.reps):
            max_weight[entry.date][entry.reps] = entry.weight

        if entry.weight > max_weight[entry.date][entry.reps]:
            max_weight[entry.date][entry.reps] = entry.weight

    for entry in logs:
        if not entry_list.get(entry.reps):
            entry_list[entry.reps] = {'list': [], 'seen': []}

        # Only add if weight is the maximum for the day
        if entry.weight != max_weight[entry.date][entry.reps]:
            continue
        if (entry.date, entry.reps, entry.weight) in entry_list[entry.reps]['seen']:
            continue

        entry_list[entry.reps]['seen'].append((entry.date, entry.reps, entry.weight))
        entry_list[entry.reps]['list'].append(
            {
                'date': entry.date,
                'weight': entry.weight,
                'reps': entry.reps
            }
        )
    for rep in entry_list:
        chart_data.append(entry_list[rep]['list'])

    return entry_log, json.dumps(chart_data, cls=DecimalJsonEncoder)


def get_last_entries(user, amount=5):
    """
    Get the last weight entries as well as the difference to the last

    This can be used e.g. to present a list where the last entries and
    their changes are presented.
    """

    last_entries = WeightEntry.objects.filter(user=user).order_by('-date')[:5]
    last_entries_details = []

    for index, entry in enumerate(last_entries):
        curr_entry = entry
        prev_entry_index = index + 1

        if prev_entry_index < len(last_entries):
            prev_entry = last_entries[prev_entry_index]
        else:
            prev_entry = None

        if prev_entry and curr_entry:
            weight_diff = curr_entry.weight - prev_entry.weight
            day_diff = (curr_entry.date - prev_entry.date).days
        else:
            weight_diff = day_diff = None
        last_entries_details.append((curr_entry, weight_diff, day_diff))

    return last_entries_details
