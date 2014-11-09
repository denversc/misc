import argparse
import collections
import contextlib
import io
import itertools
import os
import pickle
import random
import statistics
import sys
import xlsxwriter

def main():
    parsed_args = parse_args()
    players_path = parsed_args.players_file
    min_num_matches_per_player = parsed_args.min_num_matches_per_player
    max_weeks = parsed_args.max_weeks
    max_matches_per_day = parsed_args.max_matches_per_day
    tournament_path = parsed_args.tournament_file
    xlsx_path = parsed_args.xlsx_file

    if tournament_path is None:
        load_tournament = False
        save_tournament = False
    elif os.path.exists(tournament_path):
        load_tournament = True
        save_tournament = False
    else:
        load_tournament = False
        save_tournament = True

    if load_tournament:
        print("Loading tournament from file: {}".format(tournament_path))
        with io.open(tournament_path, "rb") as f:
            tournament = pickle.load(f)
        print("Loading tournament from file successful")
    else:
        players = tuple(load_players(players_path))
        print("Loaded {} players".format(len(players)))

        while True:
            matches = generate_matches(players, min_num_matches_per_player)
            tournament = generate_tournament(matches, max_matches_per_day)
            if max_weeks is not None:
                num_weeks = tournament.num_weeks()
                if num_weeks > max_weeks:
                    continue
            break
        print("Tournament generated successfully")

    if save_tournament:
        print("Saving tournament to file: {}".format(tournament_path))
        with io.open(tournament_path, "wb") as f:
            pickle.dump(tournament, f, protocol=pickle.HIGHEST_PROTOCOL)

    tournament_printers = [TextTournamentPrinter(tournament, sys.stdout)]
    if xlsx_path is not None:
        tournament_printers.append(ExcelTournamentPrinter(tournament, xlsx_path))

    for printer in tournament_printers:
        printer.run()


def generate_matches(players, min_num_matches_per_player):
    print("Generating matches")
    match_generator = MatchGenerator(
        players, min_num_matches_per_player=min_num_matches_per_player)
    matches = match_generator.run()
    print("Generated {} matches".format(len(matches)))
    return matches


def generate_tournament(matches, max_matches_per_day):
    print("Generating Tournament")
    tournament_generator = TournamentGenerator(matches, max_matches_per_day)
    tournament = tournament_generator.run()
    return tournament


def parse_args():
    arg_parser = argparse.ArgumentParser();
    arg_parser.add_argument("players_file")
    arg_parser.add_argument("--min-num-matches-per-player", "-m", type=int)
    arg_parser.add_argument("--max-weeks", "-w", type=int)
    arg_parser.add_argument("--max-matches-per-day", "-d", type=int)
    arg_parser.add_argument("--tournament-file", "-f")
    arg_parser.add_argument("--xlsx-file", "-x")
    parsed_args = arg_parser.parse_args()
    return parsed_args


class TournamentGenerator:

    def __init__(self, matches, max_matches_per_day=None):
        self.matches = matches
        self.max_matches_per_day = max_matches_per_day

    def run(self):
        days = FoosballItemList(self.generate_days())
        return Tournament(days)

    def generate_days(self):
        players = tuple(set(self.matches.players()))
        matches = FoosballItemList(self.matches)

        while len(matches) > 0:
            day_matches = self.generate_day(matches, players)
            day_matches = FoosballItemList(day_matches)
            yield day_matches

    def generate_day(self, matches, players):
        unused_players = list(players)
        num_matches = 0
        while True:
            match = self.pick_match(matches, unused_players)
            if match is None:
                break
            yield match
            matches.remove(match)
            for player in match.players():
                unused_players.remove(player)

            num_matches += 1
            if (self.max_matches_per_day is not None
                    and num_matches >= self.max_matches_per_day):
                break

    @classmethod
    def pick_match(cls, matches, players):
        min_players = cls.players_with_fewest_appearances(matches, players)

        r = min(len(min_players), 4)
        while r > 0:
            for cur_players in itertools.combinations(min_players, r):
                for match in matches:
                    matching_matches = []
                    if match.contains_players(cur_players):
                        if all(x in players for x in match.players()):
                            matching_matches.append(match)
                    if len(matching_matches) > 0:
                        return random.choice(matching_matches)
            r -= 1

        matching_matches = []
        for match in matches:
             if all(x in players for x in match.players()):
                 matching_matches.append(match)
        if len(matching_matches) > 0:
            return random.choice(matching_matches)

        return None


    @staticmethod
    def players_with_fewest_appearances(matches, players):
        min_players = []
        min_num_appearances = None
        for cur_player in players:
            num_appearances = matches.num_player_appearances(cur_player)
            if (min_num_appearances is None
                    or num_appearances < min_num_appearances):
                min_num_appearances = num_appearances
                min_players = [cur_player]
            elif num_appearances == min_num_appearances:
                min_players.append(cur_player)
        return min_players


class MatchGenerator:

    def __init__(self, players, min_num_matches_per_player=None):
        self.players = tuple(players)
        self.min_num_matches_per_player = min_num_matches_per_player

    def run(self):
        matches = FoosballItemList()
        cache = collections.defaultdict(lambda: collections.defaultdict(lambda: 0))
        while True:
            match = self.generate_match(matches, cache)
            matches.append(match)
            num_matches_per_player = self.num_matches_per_player(matches)
            if num_matches_per_player is not None:
                if self.min_num_matches_per_player is None:
                    break
                elif num_matches_per_player >= self.min_num_matches_per_player:
                    break
        return matches

    def generate_match(self, matches, cache):
        min_player_sets = None
        min_weight = None

        players_randomized = list(self.players)
        random.shuffle(players_randomized)
        for cur_players in itertools.combinations(players_randomized, 4):
            weight = 0
            for player1 in cur_players:
                for player2 in cur_players:
                    weight += cache[player1][player2]

            if min_weight is None or weight < min_weight:
                min_player_sets = [cur_players]
                min_weight = weight
            elif weight == min_weight:
                min_player_sets.append(cur_players)

        min_players = random.choice(min_player_sets)

        for player1 in min_players:
            for player2 in min_players:
                cache[player1][player2] += 1

        coordinator = random.choice(min_players)
        return Match(
            min_players[0], min_players[1], min_players[2], min_players[3],
            coordinator)

    def num_matches_per_player(self, matches):
        count = None
        for player in self.players:
            cur_count = matches.num_player_appearances(player)
            if count is None:
                count = cur_count
            elif count != cur_count:
                return None
        return count


class Match:

    def __init__(self, player1, player2, player3, player4, coordinator):
        self.player1 = player1
        self.player2 = player2
        self.player3 = player3
        self.player4 = player4
        self.coordinator = coordinator

    def players(self):
        yield self.player1
        yield self.player2
        yield self.player3
        yield self.player4

    def contains_player(self, player):
        return (
            player == self.player1 or
            player == self.player2 or
            player == self.player3 or
            player == self.player4
        )

    def contains_players(self, players):
        for player in players:
            if not self.contains_player(player):
                return False
        return True

    def num_player_appearances(self, player):
        count = 0
        for cur_player in self.players():
            if cur_player == player:
                count += 1
        return count


class FoosballItemList(list):

    def players(self):
        for match in self:
            yield from match.players()

    def num_player_appearances(self, player):
        return sum(x.num_player_appearances(player) for x in self)

    def contains_player(self, player):
        for match in self:
            if match.contains_player(player):
                return True
        return False

    def num_player_co_appearances(self, player1, player2):
        count = 0
        for match in self:
            match_contains_player1 = match.contains_player(player1)
            match_contains_player2 = match.contains_player(player2)
            if match_contains_player1 and match_contains_player2:
                count += 1
        return count


class Tournament:

    def __init__(self, days):
        self.days = days

    def num_days(self):
        return len(self.days)

    def num_weeks(self):
        count = 0
        day_num = 0
        for unused_day in self.days:
            if day_num % 3 == 0:
                count += 1
                day_num = 0
            day_num += 1
        return count

    def num_matches(self):
        count = 0
        for day in self.days:
            for unused_match in day:
                count += 1
        return count

    def matches_per_day_stats(self):
        match_per_day_counts = []
        for day in self.days:
            match_per_day_counts.append(len(day))
        return (
            min(match_per_day_counts),
            max(match_per_day_counts),
            statistics.mean(match_per_day_counts),
        )

    def matches_per_player_stats(self):
        players = set(self.players())
        players = {x:0 for x in players}
        for player in self.players():
            players[player] += 1
        match_per_player_counts = tuple(players.values())
        return (
            min(match_per_player_counts),
            max(match_per_player_counts),
            statistics.mean(match_per_player_counts),
        )

    def weeks(self):
        week = []
        for day in self.days:
            week.append(day)
            if len(week) == 3:
                yield week
                week = []
        if len(week) > 0:
            yield week

    def players(self):
        for day in self.days:
            for match in day:
                yield from match.players()

    def num_player_appearances(self, player):
        count = 0
        for day in self.days:
            for match in day:
                count += match.num_player_appearances(player)
        return count

    def num_player_co_appearances(self, player1, player2):
        count = 0
        for day in self.days:
            count += day.num_player_co_appearances(player1, player2)
        return count


class TextTournamentPrinter:

    def __init__(self, tournament, f):
        self.tournament = tournament
        self.f = f
        self.indent_count = 0

    def run(self):
        self.print_schedule()
        self.print_player_info()
        self.print_statistics()

    def print_schedule(self):
        week_num = 1
        for week in self.tournament.weeks():
            self.println()
            self.println("Week {}".format(week_num))
            with self.indented():
                self.print_schedule_for_week(week_num, week)
            week_num += 1

    def print_schedule_for_week(self, week_num, week):
        day_num = 1
        for day in week:
            self.println()
            self.println("Day {}".format(day_num))
            with self.indented():
                self.print_schedule_for_day(week_num, day_num, day)
            day_num += 1

    def print_schedule_for_day(self, week_num, day_num, day):
        match_num = 1
        for match in day:
            self.println()
            self.println("Match {}".format(match_num))
            with self.indented():
                self.println(match.player1)
                self.println(match.player2)
                self.println(match.player3)
                self.println(match.player4)
            match_num += 1

    def print_player_info(self):
        players = tuple(sorted(list(set(self.tournament.players()))))
        for player in players:
            num_appearances = self.tournament.num_player_appearances(player)
            co_appearance_counts = [
                (self.tournament.num_player_co_appearances(player, x), x)
                for x in players]
            co_appearance_counts.sort(key=lambda x: x[0], reverse=True)
            self.println()
            self.println("{} (Total Matches: {})".format(
                player, num_appearances))
            with self.indented():
                for (count, other_player) in co_appearance_counts:
                    if player == other_player:
                        continue
                    self.println("{} {}".format(count, other_player))

    def print_statistics(self):
        num_weeks = self.tournament.num_weeks()
        num_days = self.tournament.num_days()
        num_matches = self.tournament.num_matches()
        match_stats = self.tournament.matches_per_day_stats()
        (min_matches_per_day, max_matches_per_day, avg_matches_per_day) = match_stats
        player_stats = self.tournament.matches_per_player_stats()
        (min_matches_per_player, max_matches_per_player, avg_matches_per_player) = player_stats

        self.println()
        self.println("Num Weeks: {}".format(num_weeks))
        self.println("Num Days: {}".format(num_days))
        self.println("Num Matches: {}".format(num_matches))
        self.println()
        self.println("Min Matches Per Day: {}".format(min_matches_per_day))
        self.println("Max Matches Per Day: {}".format(max_matches_per_day))
        self.println("Avg Matches Per Day: {}".format(avg_matches_per_day))
        self.println()
        self.println("Min Matches Per Player: {}".format(min_matches_per_player))
        self.println("Max Matches Per Player: {}".format(max_matches_per_player))
        self.println("Avg Matches Per Player: {}".format(avg_matches_per_player))

    def println(self, line=""):
        self._print_indent()
        self.f.write(line)
        self.f.write("\n")

    def increase_indent(self):
        self.indent_count += 1

    def decrease_indent(self):
        self.indent_count -= 1

    @contextlib.contextmanager
    def indented(self):
        self.increase_indent()
        try:
            yield
        finally:
            self.decrease_indent()

    def _print_indent(self):
        indent_str = "   " * self.indent_count
        self.f.write(indent_str)


class ExcelTournamentPrinter:

    COL_SCHEDULE_WEEK = 0
    COL_SCHEDULE_DAY = 1
    COL_SCHEDULE_MATCH_NUM = 2
    COL_SCHEDULE_PLAYERS = 3
    COL_SCHEDULE_POINTS = 4
    COL_SCHEDULE_COORDINATOR = COL_SCHEDULE_MATCH_NUM

    COL_STANDINGS_PLAYER = 0
    COL_STANDINGS_POINTS = 1
    COL_STANDINGS_WINS = 3
    COL_STANDINGS_LOSSES = 4
    COL_STANDINGS_GAMES = 5
    COL_STANDINGS_WIN_PERCENTAGE = 7
    COL_STANDINGS_LOSS_PERCENTAGE = 8
    COL_STANDINGS_MATCHES = 9

    SHEET_NAME_SCHEDULE = "Schedule"
    SHEET_NAME_STANDINGS = "Standings"

    # Microsoft Excel built-in number formats
    NUM_FORMAT_NUMBER = 1  # e.g. 0
    NUM_FORMAT_PERCENTAGE_NO_DECIMALS = 9  # e.g. 5%
    NUM_FORMAT_PERCENTAGE_TWO_DECIMALS = 10  # e.g. 5.25%

    def __init__(self, tournament, path):
        self.tournament = tournament
        self.path = path

    def run(self):
        print("Creating Excel tournament schedule: {}".format(self.path))
        workbook = xlsxwriter.Workbook(self.path)
        player_info = {x:[] for x in self.tournament.players()}
        try:
            self.write_schedule(workbook, player_info)
            self.write_standings(workbook, player_info)
            self.write_players(workbook, player_info)
        finally:
            workbook.close()

    def write_schedule(self, f, player_info):
        sheet = f.add_worksheet(self.SHEET_NAME_SCHEDULE)
        row_number = 0

        format_heading = self.format_hcenter(f)
        format_heading.set_bold()
        sheet.write_string(row_number, self.COL_SCHEDULE_WEEK, "Week", format_heading)
        sheet.write_string(row_number, self.COL_SCHEDULE_DAY, "Day", format_heading)
        sheet.write_string(row_number, self.COL_SCHEDULE_MATCH_NUM, "Match", format_heading)
        sheet.write_string(row_number, self.COL_SCHEDULE_PLAYERS, "Players", format_heading)
        sheet.write_string(row_number, self.COL_SCHEDULE_POINTS, "Points", format_heading)
        row_number += 2

        format_hcenter = self.format_hcenter(f)
        format_number = f.add_format()
        format_number.set_num_format(self.NUM_FORMAT_NUMBER)
        week_num = 0
        for week in self.tournament.weeks():
            week_num += 1
            sheet.write_string(row_number, self.COL_SCHEDULE_WEEK,
                "Week {}".format(week_num))
            row_number += 1

            day_num = 0
            for day in week:
                day_num += 1
                sheet.write_string(
                    row_number, self.COL_SCHEDULE_DAY, "Day {}".format(day_num))
                row_number += 1

                match_num = 0
                for match in day:
                    match_num += 1
                    row_number += 1
                    sheet.write_string(
                        row_number, self.COL_SCHEDULE_MATCH_NUM,
                        "Match {}".format(match_num))
                    row_number += 1

                    coords = {}
                    for player in sorted(match.players()):
                        sheet.write_string(
                            row_number, self.COL_SCHEDULE_PLAYERS, player)
                        if player == match.coordinator:
                            sheet.write_string(
                                row_number, self.COL_SCHEDULE_COORDINATOR,
                                "X", format_hcenter)
                        sheet.write_blank(row_number, self.COL_SCHEDULE_POINTS,
                            None, format_number)
                        coords[player] = (row_number, self.COL_SCHEDULE_POINTS)
                        row_number += 1

                    for player in match.players():
                        player_info[player].append(self.MatchInfo(
                            match, week_num, day_num, match_num, coords))

    def write_standings(self, f, player_info):
        sheet = f.add_worksheet(self.SHEET_NAME_STANDINGS)
        row_number = 0

        format_heading = self.format_hcenter(f)
        format_heading.set_bold()

        sheet.write_string(
            row_number, self.COL_STANDINGS_PLAYER, "Player", format_heading)
        sheet.write_string(
            row_number, self.COL_STANDINGS_POINTS, "Points", format_heading)
        sheet.write_string(
            row_number, self.COL_STANDINGS_WINS, "Wins", format_heading)
        sheet.write_string(
            row_number, self.COL_STANDINGS_LOSSES, "Losses", format_heading)
        sheet.write_string(
            row_number, self.COL_STANDINGS_GAMES, "Games", format_heading)
        sheet.write_string(
            row_number, self.COL_STANDINGS_WIN_PERCENTAGE, "Win %", format_heading)
        sheet.write_string(
            row_number, self.COL_STANDINGS_LOSS_PERCENTAGE, "Loss %", format_heading)
        sheet.write_string(
            row_number, self.COL_STANDINGS_MATCHES, "Matches Played", format_heading)
        row_number += 2

        format_percentage = f.add_format()
        format_percentage.set_num_format(self.NUM_FORMAT_PERCENTAGE_NO_DECIMALS)
        format_number = f.add_format()
        format_number.set_num_format(self.NUM_FORMAT_NUMBER)

        players = sorted(set(self.tournament.players()))
        for player in players:
            points_formula = "={}".format(
                xlsxwriter.utility.xl_rowcol_to_cell(
                    row_number, self.COL_STANDINGS_WINS))
            wins_formula = "=" + "+".join(
                "IF(ISBLANK({sheet}!{cell}), 0, {sheet}!{cell})".format(
                    sheet=self.SHEET_NAME_SCHEDULE,
                    cell=xlsxwriter.utility.xl_rowcol_to_cell(
                        x.coords[player][0],
                        x.coords[player][1],
                        row_abs=True,
                        col_abs=True,
                    ))
                for x in player_info[player]
            )
            losses_formula = "=" + "+".join(
                "IF(ISBLANK({sheet}!{cell}), 0, 3-{sheet}!{cell})".format(
                    sheet=self.SHEET_NAME_SCHEDULE,
                    cell=xlsxwriter.utility.xl_rowcol_to_cell(
                        x.coords[player][0],
                        x.coords[player][1],
                        row_abs=True,
                        col_abs=True,
                    ))
                for x in player_info[player]
            )
            games_formula = "={}+{}".format(
                xlsxwriter.utility.xl_rowcol_to_cell(
                    row_number, self.COL_STANDINGS_WINS),
                xlsxwriter.utility.xl_rowcol_to_cell(
                    row_number, self.COL_STANDINGS_LOSSES),
            )
            win_percentage_formula = "=IF({}=0, 0, {}/{})".format(
                xlsxwriter.utility.xl_rowcol_to_cell(
                    row_number, self.COL_STANDINGS_GAMES),
                xlsxwriter.utility.xl_rowcol_to_cell(
                    row_number, self.COL_STANDINGS_WINS),
                xlsxwriter.utility.xl_rowcol_to_cell(
                    row_number, self.COL_STANDINGS_GAMES),
            )
            loss_percentage_formula = "=IF({}=0, 0, {}/{})".format(
                xlsxwriter.utility.xl_rowcol_to_cell(
                    row_number, self.COL_STANDINGS_GAMES),
                xlsxwriter.utility.xl_rowcol_to_cell(
                    row_number, self.COL_STANDINGS_LOSSES),
                xlsxwriter.utility.xl_rowcol_to_cell(
                    row_number, self.COL_STANDINGS_GAMES),
            )
            matches_played_formula = "=" + "+".join(
                "IF(ISBLANK({sheet}!{cell}), 0, 1)".format(
                    sheet=self.SHEET_NAME_SCHEDULE,
                    cell=xlsxwriter.utility.xl_rowcol_to_cell(
                        x.coords[player][0],
                        x.coords[player][1],
                        row_abs=True,
                        col_abs=True,
                    ))
                for x in player_info[player]
            )

            sheet.write_string(
                row_number, self.COL_STANDINGS_PLAYER, player)
            sheet.write_formula(
                row_number, self.COL_STANDINGS_POINTS,
                points_formula, format_number)
            sheet.write_formula(
                row_number, self.COL_STANDINGS_WINS,
                wins_formula, format_number)
            sheet.write_formula(
                row_number, self.COL_STANDINGS_LOSSES,
                losses_formula, format_number)
            sheet.write_formula(
                row_number, self.COL_STANDINGS_GAMES,
                games_formula, format_number)
            sheet.write_formula(
                row_number, self.COL_STANDINGS_WIN_PERCENTAGE,
                win_percentage_formula, format_percentage)
            sheet.write_formula(row_number, self.COL_STANDINGS_LOSS_PERCENTAGE,
                loss_percentage_formula, format_percentage)
            sheet.write_formula(
                row_number, self.COL_STANDINGS_MATCHES,
                matches_played_formula, format_number)

            row_number += 1

    def write_players(self, f, player_info):
        for player in sorted(set(self.tournament.players())):
            cur_player_info = player_info[player]
            self.write_player(f, player, cur_player_info)

    def write_player(self, f, player, player_info):
        format_bold = f.add_format()
        format_bold.set_bold()
        format_number = f.add_format()
        format_number.set_num_format(self.NUM_FORMAT_NUMBER)

        sheet = f.add_worksheet(player)
        row_number = 0
        sheet.write_string(row_number, 0, player, format_bold)
        row_number += 2

        sheet.write_string(row_number, 0, "Schedule", format_bold)
        col_number = 0
        row_number += 2
        sheet.write_string(row_number, col_number, "#", format_bold)
        col_number += 1
        sheet.write_string(row_number, col_number, "Week", format_bold)
        col_number += 1
        sheet.write_string(row_number, col_number, "Day", format_bold)
        col_number += 1
        sheet.write_string(row_number, col_number, "Match", format_bold)
        col_number += 1
        sheet.write_string(row_number, col_number, "Wins", format_bold)
        col_number += 1
        sheet.write_string(row_number, col_number, "Losses", format_bold)
        col_number += 1
        sheet.write_string(row_number, col_number, "Player 1", format_bold)
        col_number += 1
        sheet.write_string(row_number, col_number, "Player 2", format_bold)
        col_number += 1
        sheet.write_string(row_number, col_number, "Player 3", format_bold)

        row_number += 1

        match_index = 0
        for match_info in player_info:
            match_index += 1
            col_number = 0

            sheet.write_string(row_number, col_number,
                "{}".format(match_index))
            col_number += 1
            sheet.write_string(row_number, col_number,
                "Week {}".format(match_info.week_num))
            col_number += 1
            sheet.write_string(row_number, col_number,
                "Day {}".format(match_info.day_num))
            col_number += 1
            sheet.write_string(row_number, col_number,
                "Match {}".format(match_info.match_num))
            col_number += 1

            coords = match_info.coords[player]
            cell = "{}!{}".format(
                    self.SHEET_NAME_SCHEDULE,
                    xlsxwriter.utility.xl_rowcol_to_cell(
                        coords[0],
                        coords[1],
                        row_abs=True,
                        col_abs=True,
                    )
            )
            win_formula = "=IF(ISBLANK({cell}), \"\", {cell})".format(
                cell=cell)
            loss_formula = "=IF(ISBLANK({cell}), \"\", 3-{cell})".format(
                cell=cell)
            sheet.write_formula(
                row_number, col_number, win_formula, format_number)
            col_number += 1
            sheet.write_formula(
                row_number, col_number, loss_formula, format_number)
            col_number += 1

            for other_player in sorted(match_info.match.players()):
                if other_player == player:
                    continue
                sheet.write_string(row_number, col_number, other_player)
                col_number += 1

            row_number += 1

        row_number += 1
        sheet.write_string(
            row_number, 0, "Number of Matches with Other Players", format_bold)
        row_number += 2

        players = tuple(set(self.tournament.players()))
        counts = [
            (self.tournament.num_player_co_appearances(player, x), x)
            for x in players
        ]
        counts.sort(key=lambda x: x[1])
        counts.sort(key=lambda x: x[0], reverse=True)
        for (count, other_player) in counts:
            if other_player == player:
                continue
            sheet.write_string(row_number, 0, other_player)
            sheet.write_number(row_number, 1, count)
            row_number += 1

    @staticmethod
    def format_hcenter(workbook):
        format = workbook.add_format()
        format.set_align("center")
        return format

    class MatchInfo:

        def __init__(self, match, week_num, day_num, match_num, coords):
            self.match = match
            self.week_num = week_num
            self.day_num = day_num
            self.match_num = match_num
            self.coords = coords


def load_players(path):
    print("Loading player list from file: {}".format(path))
    with io.open(path, "rt", encoding="utf8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                yield line


if __name__ == "__main__":
    main()
