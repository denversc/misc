#!/usr/bin/env python3

import argparse
import collections
import datetime
import io
import random
import statistics
import sys
import xlsxwriter


def main():
    (names_path, xlsx_path, start_date) = parse_args()
    print("Loading player names from file: {}".format(names_path))
    names = load_names_from_file(names_path)
    print("Generating teams")
    team_generator = FoosballTeamListGenerator(names, min_games_per_player=0)
    teams = team_generator.generate()
    print("Generating matches")
    match_generator = FoosballMatchListGenerator(teams)
    matches = match_generator.generate()
    print("Generating tournament")
    tournament_generator = FoosballTournamentGenerator(matches, start_date)
    tournament = tournament_generator.generate()
    text_printer = TournamentTextPrinter(sys.stdout)
    text_printer.run(tournament)
    print("Writing Tournament to Excel file: {}".format(xlsx_path))
    xlsx_printer = TournamentXlsxPrinter(xlsx_path)
    xlsx_printer.run(tournament)

def parse_args():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-n", "--names-file", default="names.txt")
    arg_parser.add_argument("-o", "--output-excel-file", default="FoosballTournament.xlsx")
    arg_parser.add_argument("-s", "--start-date", default=None)
    parsed_args = arg_parser.parse_args()

    # parse the start date, ensuring that it begins on a Monday, Wednesday, or Friday
    valid_weekdays = (0, 2, 4)
    start_date_str = parsed_args.start_date
    if start_date_str is None:
        start_date = datetime.datetime.today()
        while start_date.weekday() not in valid_weekdays:
            start_date = start_date + datetime.timedelta(days=1)
    else:
        start_date_format = "%Y-%m-%d"
        try:
            start_date = datetime.datetime.strptime(start_date_str, start_date_format)
        except ValueError as e:
            arg_parser.error("Invalid start date: {} (must be formatted {})"
                .format(start_date_str, start_date_format))
            raise AssertionError("should never get here")

        if start_date.weekday() not in valid_weekdays:
            arg_parser.error("Invalid start date: {} (must be a Monday, Wednesday, or Friday)"
                .format(start_date_str))
            raise AssertionError("should never get here")

        start_date = start_date.date()  # convert datetime object to date object

    return (parsed_args.names_file, parsed_args.output_excel_file, start_date)

class FoosballTournament:

    def __init__(self):
        self.match_lists = []

    def add_match_list(self, match_list):
        self.match_lists.append(match_list)

    def players(self):
        for match_list in self.match_lists:
            yield from match_list.players()

    def teams_including_player(self, player):
        for match_list in self.match_lists:
            yield from match_list.teams_including_player(player)

    def player_partners(self, player):
        for match_list in self.match_lists:
            yield from match_list.player_partners(player)

    def player_opponents(self, player):
        for match_list in self.match_lists:
            yield from match_list.player_opponents(player)

    def __iter__(self):
        return iter(self.match_lists)


class FoosballTournamentGenerator:

    MAX_GAMES_PER_DAY_PER_PLAYER = 1
    MAX_GAMES_PER_WEEK_PER_PLAYER = 2

    EXCLUDE_DATES = {
        datetime.date(2015, 2, 16): "Family Day"
    }

    def __init__(self, match_list, start_date):
        self.match_list = match_list
        self.start_date = start_date

    def generate(self):
        tournament = FoosballTournament()
        matches = list(self.match_list)
        players = frozenset(self.match_list.players())
        shuffle(matches)

        coordinator_counts = collections.defaultdict(lambda: 0)
        cur_date = self.start_date
        while len(matches) > 0:
            week_player_counts = collections.defaultdict(lambda: 0)

            while len(matches) > 0:
                day = FoosballMatchList(date=cur_date)
                day_player_counts = collections.defaultdict(lambda: 0)

                # generate matches for the day
                if cur_date in self.EXCLUDE_DATES:
                    day.date_message = self.EXCLUDE_DATES[cur_date]
                else:
                    while True and cur_date:
                        match = self._find_match_for_day(
                            matches, day_player_counts, week_player_counts)
                        if match is None:
                            break
                        self._set_match_coordinator(match, coordinator_counts)
                        day.add_match(match)
                tournament.add_match_list(day)

                # if any players didn't play today, move them to the end of the list so they get
                # preference in the next day
                self._move_unused_players_to_end(matches, day_player_counts)

                # advance to the next day
                new_week = False
                while True:
                    cur_date = cur_date + datetime.timedelta(days=1)
                    if cur_date.weekday() == 0:
                        new_week = True
                    if cur_date.weekday() in (0, 2, 4):
                        break

                # if starting a new week, reset the weekly counts
                if new_week:
                    break

        return tournament

    def _find_match_for_day(self, matches, day_player_counts, week_player_counts):
        i = len(matches)
        while i > 0:
            i -= 1
            match = matches[i]

            # make sure no players have already maxxed out their max games per day
            for player in match.players():
                if day_player_counts[player] >= self.MAX_GAMES_PER_DAY_PER_PLAYER:
                    skip_match_due_to_daily_max = True
                    break
            else:
                skip_match_due_to_daily_max = False
            if skip_match_due_to_daily_max:
                continue

            # make sure no players have already maxxed out their max games per week
            for player in match.players():
                if week_player_counts[player] >= self.MAX_GAMES_PER_WEEK_PER_PLAYER:
                    skip_match_due_to_weekly_max = True
                    break
            else:
                skip_match_due_to_weekly_max = False
            if skip_match_due_to_weekly_max:
                continue

            # found a match that meets the criteria; stop searching and return it
            for player in match.players():
                day_player_counts[player] += 1
                week_player_counts[player] += 1
            del matches[i]
            return match

    @staticmethod
    def _set_match_coordinator(match, coordinator_counts):
        coordinator = None
        for player in match.players():
            cur_count = coordinator_counts[player]
            if coordinator is None or cur_count < coordinator_count:
                coordinator = player
                coordinator_count = cur_count
        match.coordinator = coordinator
        coordinator_counts[coordinator] += 1

    @staticmethod
    def _move_unused_players_to_end(matches, player_counts):
        i = len(matches)
        while i > 0:
            i -= 1
            match = matches[i]

            for player in match.players():
                if player_counts[player] == 0:
                    break
            else:
                continue

            for player in match.players():
                player_counts[player] += 1

            del matches[i]
            matches.append(match)

class FoosballMatch:

    def __init__(self, team1, team2):
        self.team1 = team1
        self.team2 = team2
        self.coordinator = None

    def teams(self):
        yield self.team1
        yield self.team2

    def includes_player(self, player):
        for unused in self.teams_including_player(player):
            return True
        else:
            return False

    def teams_including_player(self, player):
        for team in self.teams():
            if team.includes_player(player):
                yield team

    def players(self):
        for team in self.teams():
            yield from team.players()


class FoosballMatchList:

    def __init__(self, date=None, date_message=None):
        self.matches = []
        self.date = date
        self.date_message = date_message

    def add_match(self, match):
        self.matches.append(match)

    def get_opponent_counts(self, player):
        counts = collections.defaultdict(lambda: 0)
        for match in self.matches:
            if match.includes_player(player):
                for team in match.teams():
                    if not team.includes_player(player):
                        for opponent in team.players():
                            counts[opponent] += 1
        return counts

    def includes_player(self, player):
        for match in self.matches:
            if match.includes_player(player):
                return True
        return False

    def teams_including_player(self, player):
        for match in self.matches:
            yield from match.teams_including_player(player)

    def players(self):
        for match in self.matches:
            yield from match.players()

    def player_partners(self, player):
        for team in self.teams_including_player(player):
            for partner in team.players():
                if partner != player:
                    yield partner

    def player_opponents(self, player):
        for match in self.matches:
            if match.includes_player(player):
                for team in match.teams():
                    if not team.includes_player(player):
                        yield from team.players()

    def __iter__(self):
        return iter(self.matches)


class FoosballMatchListGenerator:

    def __init__(self, team_list):
        self.team_list = team_list

    def generate(self):
        match_list = FoosballMatchList()

        teams = list(self.team_list)
        assert len(teams) % 2 == 0
        shuffle(teams)

        while len(teams) > 0:
            team1 = teams[0]
            team1_opponent_counts = {x: match_list.get_opponent_counts(x) for x in team1.players()}

            team2 = None
            for cur_team in teams:
                if cur_team.includes_any_player(team1.players()):
                    continue

                cur_team_opponent_counts = []
                for team1_player in team1.players():
                    for cur_team_player in cur_team.players():
                        cur_team_opponent_counts.append(
                            team1_opponent_counts[team1_player][cur_team_player])

                if team2 is None:
                    team2 = cur_team
                    team2_opponent_counts = cur_team_opponent_counts
                else:
                    cur_team_opponent_count_max = max(cur_team_opponent_counts)
                    team2_opponent_count_max = max(team2_opponent_counts)
                    if cur_team_opponent_count_max < team2_opponent_count_max:
                        replace_team2 = True
                    elif cur_team_opponent_count_max == team2_opponent_count_max:
                        cur_team_opponent_count_mean = statistics.mean(cur_team_opponent_counts)
                        team2_opponent_count_mean = statistics.mean(team2_opponent_counts)
                        if cur_team_opponent_count_mean < team2_opponent_count_mean:
                            replace_team2 = True
                        else:
                            replace_team2 = False
                    else:
                        replace_team2 = False

                    if replace_team2:
                        team2 = cur_team
                        team2_opponent_counts = cur_team_opponent_counts

            if team2 is not None:
                del teams[0]
                teams.remove(team2)
                match = FoosballMatch(team1, team2)
                match_list.add_match(match)

        return match_list


class FoosballTeam:

    def __init__(self, player1, player2):
        self.player1 = player1
        self.player2 = player2

    def includes_player(self, player):
        for cur_player in self.players():
            if cur_player == player:
                return True
        return False

    def includes_any_player(self, players):
        for candidate_player in players:
            for team_player in self.players():
                if candidate_player == team_player:
                    return True
        return False

    def players(self):
        yield self.player1
        yield self.player2


class FoosballTeamList:

    def __init__(self):
        self.teams = []

    def add_team(self, team):
        self.teams.append(team)

    def teams_including_player(self, player):
        for team in self.teams:
            if team.includes_player(player):
                yield team

    def count_teams_including_player(self, player):
        count = 0
        for team in self.teams_including_player(player):
            count += 1
        return count

    def teams_including_players(self, player1, player2):
        for team in self.teams:
            if team.includes_player(player1) and team.includes_player(player2):
                yield team

    def count_teams_including_players(self, player1, player2):
        count = 0
        for team in self.teams_including_players(player1, player2):
            count += 1
        return count

    def count_teams_per_player(self):
        counts = collections.defaultdict(lambda: 0)
        for team in self.teams:
            counts[team.player1] += 1
            counts[team.player2] += 1

        if len(counts) == 0:
            return 0

        num_games_per_player = next(iter(counts.values()))
        for count in counts.values():
             if count != num_games_per_player:
                 raise AssertionError("not all player have played the same number of games")

        return num_games_per_player

    def __iter__(self):
        return iter(self.teams)

    def __len__(self):
        return len(self.teams)


class FoosballTeamListGenerator:

    def __init__(self, names, min_games_per_player=None):
        self.names = tuple(names)
        if min_games_per_player is None:
            min_games_per_player = 0
        self.min_games_per_player = min_games_per_player

    def generate(self):
        teams = FoosballTeamList()

        # generate all partner combinations
        self.add_all_team_combinations(teams)
        num_teams_per_player_all_combinations = teams.count_teams_per_player()

        # generate more all partner combinations so that the minimum number is fulfilled
        while teams.count_teams_per_player() + num_teams_per_player_all_combinations < self.min_games_per_player:
            self.add_all_team_combinations(teams)

        # generate filler teams to either bring the number of teams to an even number or to get
        # the number of games per player up to the minimum
        while teams.count_teams_per_player() < self.min_games_per_player:
            self.add_filler_teams(teams)

        # generate filler teams so that the overall number is even
        while len(teams) % 2 != 0:
            self.add_filler_teams(teams)

        return teams

    def add_all_team_combinations(self, teams):
        for i in range(len(self.names)):
            player1 = self.names[i]
            for j in range(len(self.names) - i - 1):
                player2 = self.names[j + i + 1]
                team = FoosballTeam(player1, player2)
                teams.add_team(team)

    def add_filler_teams(self, teams):
        players = list(self.names)
        if len(players) % 2 != 0:
            players.extend(players)
        shuffle(players)

        while len(players) > 0:
            player1 = players[0]
            del players[0]

            player2 = None
            for player in (x for x in players if x != player1):
                if player2 is None:
                    player2 = player
                    partner_count = teams.count_teams_including_players(player1, player)
                else:
                    cur_partner_count = teams.count_teams_including_players(player1, player)
                    if cur_partner_count < partner_count:
                        player2 = player
                        partner_count = cur_partner_count

            players.remove(player2)
            team = FoosballTeam(player1, player2)
            teams.add_team(team)


class TournamentTextPrinter:

    def __init__(self, f):
        self.f = f

    def run(self, tournament):
        self.print_schedule(tournament)
        self.print_partners(tournament)
        self.print_opponents(tournament)

    def print_schedule(self, tournament):
        self.println()
        self.println("Tournament Schedule")
        week_num = None
        day_num = 0
        for match_list in tournament:
            day_num += 1
            if week_num is None:
                week_num = 1
            elif match_list.date.weekday() == 0:
                week_num += 1

            date_str = match_list.date.strftime("%a %b %d")
            self.println("Week {} Day {} {}".format(week_num, day_num, date_str))
            if match_list.date_message is not None:
                self.println(match_list.date_message)
            for (match_index, match) in enumerate(match_list):
                teams_str = " vs. ".join(" & ".join(team.players()) for team in match.teams())
                self.println("  Match {}: {}".format(match_index + 1, teams_str))

    def print_partners(self, tournament):
        self.println()
        self.println("Partner Counts")
        players = tuple(sorted(frozenset(tournament.players())))
        for player in players:
            counts = collections.defaultdict(lambda: 0)
            for partner in tournament.player_partners(player):
                counts[partner] += 1
            counts = [(counts[x], x) for x in players]
            counts.sort(reverse=True)

            self.println()
            self.println("{} partners".format(player))
            for (count, partner) in counts:
                if partner != player:
                    self.println("  {} {}".format(partner, count))

    def print_opponents(self, tournament):
        self.println()
        self.println("Opponent Counts")
        players = tuple(sorted(frozenset(tournament.players())))
        for player in players:
            counts = collections.defaultdict(lambda: 0)
            for opponent in tournament.player_opponents(player):
                counts[opponent] += 1
            counts = [(counts[x], x) for x in players]
            counts.sort(reverse=True)

            self.println()
            self.println("{} opponents".format(player))
            for (count, opponent) in counts:
                if opponent != player:
                    self.println("  {} {}".format(opponent, count))

    def println(self, line=None):
        if line is None:
            line = ""
        print(line, file=self.f)


class TournamentXlsxPrinter:

    def __init__(self, path):
        self.path = path

    def run(self, tournament):
        f = xlsxwriter.Workbook(self.path)
        formats = self.Formats(f)
        players_info = {x: self.PlayerInfo(x) for x in tournament.players()}

        self.write_schedule(f, formats, tournament, players_info)
        self.write_standings(f, formats, players_info)
        self.write_players(f, formats, players_info)

    def write_schedule(self, f, formats, tournament, players_info):
        class columns:
            date = 0
            player1 = 1
            player2 = 2
            points = 3

        sheet_name = "Schedule"
        sheet = f.add_worksheet(sheet_name)
        row_index = 0

        sheet.write_string(row_index, columns.date, "Date", formats.heading)
        sheet.write_string(row_index, columns.player1, "Player 1", formats.heading)
        sheet.write_string(row_index, columns.player2, "Player 2", formats.heading)
        sheet.write_string(row_index, columns.points, "Points", formats.heading)
        row_index += 1

        for match_list in tournament:

            # write the date header
            row_index += 1
            date_str = match_list.date.strftime("%a %b %d")
            if match_list.date_message is not None:
                date_str = "{} ({})".format(date_str, match_list.date_message)
            for col_index in range(4):
                sheet.write_blank(row_index, col_index, None, formats.shaded)
            sheet.write_string(row_index, columns.date, date_str, formats.shaded)
            row_index += 1

            # write the day's matches
            day_has_matches = False
            for match in match_list:
                day_has_matches = True
                team_points_cells = []

                teams = tuple(match.teams())
                for team in teams:
                    row_index += 1
                    for (col_index, player) in [
                        (columns.player1, team.player1),
                        (columns.player2, team.player2),
                    ]:
                        if player == match.coordinator:
                            player_str = "{} (MC)".format(player)
                            player_format = formats.bold
                        else:
                            player_str = player
                            player_format = None
                        sheet.write_string(row_index, col_index, player_str, player_format)
                    team_points_cells.append((row_index, columns.points))

                sheet.write_blank(row_index, columns.points, None, formats.number)

                # store information about the match for the players
                for (i, team) in enumerate(teams):
                    if i == 0:
                        my_points_rowcol = team_points_cells[0]
                        opponent_points_rowcol = team_points_cells[1]
                    elif i == 1:
                        my_points_rowcol = team_points_cells[1]
                        opponent_points_rowcol = team_points_cells[0]
                    else:
                        raise AssertionError("invalid i: {!r}".format(i))

                    my_points_cell = "{}!{}".format(sheet_name,
                        xlsxwriter.utility.xl_rowcol_to_cell(
                            my_points_rowcol[0], my_points_rowcol[1],
                            row_abs=True, col_abs=True
                        )
                    )
                    opponent_points_cell = "{}!{}".format(sheet_name,
                        xlsxwriter.utility.xl_rowcol_to_cell(
                            opponent_points_rowcol[0], opponent_points_rowcol[1],
                            row_abs=True, col_abs=True
                        )
                    )

                    match_info = self.PlayerInfo.MatchInfo(
                        match, match_list.date, my_points_cell, opponent_points_cell)
                    for player in team.players():
                        players_info[player].matches.append(match_info)

                row_index += 1

            if not day_has_matches:
                row_index += 1
                sheet.write_string(row_index, 0, "no matches today", formats.italic)
                row_index += 1

    def write_standings(self, f, formats, players_info):
        sheet = f.add_worksheet("Standings")
        row_index = 0

        class columns:
            name = 0
            wins = 1
            losses = 2
            win_percentage = 3
            matches_played = 4

        sheet.write_string(row_index, columns.name, "Name", formats.heading)
        sheet.write_string(row_index, columns.wins, "Wins", formats.heading)
        sheet.write_string(row_index, columns.losses, "Losses", formats.heading)
        sheet.write_string(row_index, columns.win_percentage, "Win %", formats.heading)
        sheet.write_string(row_index, columns.matches_played, "Matches Played", formats.heading)
        row_index += 1

        for name in sorted(players_info):
            player_info = players_info[name]
            row_index += 1

            wins_formula = "+".join(x.my_points_cell for x in player_info.matches)
            losses_formula = "+".join(x.opponent_points_cell for x in player_info.matches)
            matches_played_formula = "+".join(
                "IF(ISBLANK({}), 0, 1)".format(x.my_points_cell) for x in player_info.matches)

            sheet.write_string(row_index, columns.name, name)
            sheet.write_formula(row_index, columns.wins, wins_formula, formats.number)
            wins_cell = xlsxwriter.utility.xl_rowcol_to_cell(row_index, columns.wins)
            sheet.write_formula(row_index, columns.losses, losses_formula, formats.number)
            losses_cell = xlsxwriter.utility.xl_rowcol_to_cell(row_index, columns.losses)
            sheet.write_formula(
                row_index, columns.matches_played, matches_played_formula, formats.number)

            win_percentage_formula = "{wins}/({wins}+{losses})".format(
                wins=wins_cell, losses=losses_cell)
            sheet.write_formula(
                row_index, columns.win_percentage, win_percentage_formula,
                formats.percent_0_decimals)

    def write_players(self, f, formats, players_info):
        player_names = tuple(players_info)
        for name in sorted(players_info):
            info = players_info[name]
            self.write_player(f, formats, name, info, player_names)

    def write_player(self, f, formats, name, info, player_names):
        sheet = f.add_worksheet(name)
        row_index = 0
        sheet.write_string(row_index, 0, name, formats.bold)
        row_index += 1
        row_index = self.write_player_schedule(sheet, formats, info, row_index)
        row_index = self.write_player_partners_and_opponents(
            sheet, formats, info, player_names, row_index)

    def write_player_schedule(self, sheet, formats, player, row_index):
        class columns:
            match_number = 0
            date = 1
            wins = 2
            losses = 3
            match_coordinator = 4
            partner = 5
            opponent1 = 6
            opponent2 = 7

        # Write schedule heading
        row_index += 1
        sheet.write_string(row_index, 0, "Schedule", formats.shaded)
        for col_index in range(1, 7):
            sheet.write_blank(row_index, col_index, None, formats.shaded)
        row_index += 1

        # Write schedule
        row_index += 1
        sheet.write_string(row_index, columns.match_number, "#", formats.heading)
        sheet.write_string(row_index, columns.date, "Date", formats.heading)
        sheet.write_string(row_index, columns.wins, "Wins", formats.heading)
        sheet.write_string(row_index, columns.losses, "Losses", formats.heading)
        sheet.write_string(row_index, columns.match_coordinator, "MC", formats.heading)
        sheet.write_string(row_index, columns.partner, "Partner", formats.heading)
        sheet.write_string(row_index, columns.opponent1, "Opponent 1", formats.heading)
        sheet.write_string(row_index, columns.opponent2, "Opponent 2", formats.heading)

        first_match_row = None
        last_match_row = None
        for (match_index, match_info) in enumerate(player.matches):
            row_index += 1
            if first_match_row is None:
                first_match_row = row_index
            last_match_row = row_index

            match_date_str = match_info.date.strftime("%a %b %d")
            winloss_template = '=IF(ISBLANK({0}),"",{0})'
            win_formula = winloss_template.format(match_info.my_points_cell)
            loss_formula = winloss_template.format(match_info.opponent_points_cell)

            if match_info.match.team1.includes_player(player.name):
                my_team = match_info.match.team1
                other_team = match_info.match.team2
            else:
                my_team = match_info.match.team2
                other_team = match_info.match.team1

            match_coordinator = "X" if match_info.match.coordinator == player.name else ""
            partner = my_team.player1 if my_team.player1 != player.name else my_team.player2
            opponent1 = other_team.player1
            opponent2 = other_team.player2

            sheet.write_string(row_index, columns.match_number, "{}".format(match_index + 1))
            sheet.write_string(row_index, columns.date, match_date_str)
            sheet.write_formula(row_index, columns.wins, win_formula)
            sheet.write_formula(row_index, columns.losses, loss_formula)
            sheet.write_string(
                row_index, columns.match_coordinator, match_coordinator, formats.center)
            sheet.write_string(row_index, columns.partner, partner)
            sheet.write_string(row_index, columns.opponent1, opponent1)
            sheet.write_string(row_index, columns.opponent2, opponent2)
        row_index += 1

        # Write schedule totals
        total_wins_formula = "=SUM({}:{})".format(
            xlsxwriter.utility.xl_rowcol_to_cell(
                first_match_row, columns.wins, row_abs=True, col_abs=True),
            xlsxwriter.utility.xl_rowcol_to_cell(
                last_match_row, columns.wins, row_abs=True, col_abs=True),
        )
        total_losses_formula = "=SUM({}:{})".format(
            xlsxwriter.utility.xl_rowcol_to_cell(
                first_match_row, columns.losses, row_abs=True, col_abs=True),
            xlsxwriter.utility.xl_rowcol_to_cell(
                last_match_row, columns.losses, row_abs=True, col_abs=True),
        )

        row_index += 1
        sheet.write_string(row_index, 0, "TOTALS:", formats.bold)
        sheet.write_formula(row_index, columns.wins, total_wins_formula)
        sheet.write_formula(row_index, columns.losses, total_losses_formula)

        # Write schedule percentages
        percent_template = "={0}/({0}+{1})"
        percent_wins_formula = percent_template.format(
            xlsxwriter.utility.xl_rowcol_to_cell(
                row_index, columns.wins, row_abs=True, col_abs=True),
            xlsxwriter.utility.xl_rowcol_to_cell(
                row_index, columns.losses, row_abs=True, col_abs=True),
        )
        percent_losses_formula = percent_template.format(
            xlsxwriter.utility.xl_rowcol_to_cell(
                row_index, columns.losses, row_abs=True, col_abs=True),
            xlsxwriter.utility.xl_rowcol_to_cell(
                row_index, columns.wins, row_abs=True, col_abs=True),
        )

        row_index += 1
        sheet.write_formula(
            row_index, columns.wins, percent_wins_formula, formats.percent_0_decimals)
        sheet.write_formula(
            row_index, columns.losses, percent_losses_formula, formats.percent_0_decimals)
        row_index += 1

        return row_index

    def write_player_partners_and_opponents(self, sheet, formats, player, player_names, row_index):
        # Calculate partners and opponents
        partner_counts = {x:0 for x in player_names}
        opponent_counts = {x:0 for x in player_names}
        for match_info in player.matches:
            match = match_info.match
            for team in match.teams():
                if team.includes_player(player.name):
                    for cur_player_name in team.players():
                        if cur_player_name != player.name:
                            partner_counts[cur_player_name] += 1
                else:
                    for cur_player_name in team.players():
                        if cur_player_name != player.name:
                            opponent_counts[cur_player_name] += 1

        partner_counts = [(partner_counts[x], x) for x in partner_counts]
        partner_counts.sort(key=lambda x: (-x[0], x[1]))
        opponent_counts = [(opponent_counts[x], x) for x in opponent_counts]
        opponent_counts.sort(key=lambda x: (-x[0], x[1]))

        # Write partners
        row_index += 1
        sheet.write_string(row_index, 0, "Partners", formats.shaded)
        for col_index in range(1, 7):
            sheet.write_blank(row_index, col_index, None, formats.shaded)
        row_index += 1

        for (count, partner) in partner_counts:
            if partner == player.name:
                continue
            row_index += 1
            sheet.write_string(row_index, 0, partner)
            sheet.write_string(row_index, 1, "{}".format(count))
        row_index += 1

        # Write opponents
        row_index += 1
        sheet.write_string(row_index, 0, "Opponents", formats.shaded)
        for col_index in range(1, 7):
            sheet.write_blank(row_index, col_index, None, formats.shaded)
        row_index += 1

        for (count, opponent) in opponent_counts:
            if opponent == player.name:
                continue
            row_index += 1
            sheet.write_string(row_index, 0, opponent)
            sheet.write_string(row_index, 1, "{}".format(count))
        row_index += 1

    class PlayerInfo:

        def __init__(self, name):
            self.name = name
            self.matches = []

        def __str__(self):
            return "{}".format(self.name)

        class MatchInfo:

            def __init__(self, match, date, my_points_cell, opponent_points_cell):
                self.match = match
                self.date = date
                self.my_points_cell = my_points_cell
                self.opponent_points_cell = opponent_points_cell

    class Formats:

        # Microsoft Excel built-in number formats
        NUM_FORMAT_NUMBER = 1  # e.g. 0
        NUM_FORMAT_PERCENTAGE_NO_DECIMALS = 9  # e.g. 5%
        NUM_FORMAT_PERCENTAGE_TWO_DECIMALS = 10  # e.g. 5.25%

        def __init__(self, f):
            self.heading = f.add_format()
            self.heading.set_align("center")
            self.heading.set_bold()

            self.shaded = f.add_format()
            self.shaded.set_bg_color("#D3D3D3")

            self.italic = f.add_format()
            self.italic.set_italic()

            self.bold = f.add_format()
            self.bold.set_bold()

            self.number = f.add_format()
            self.number.set_num_format(self.NUM_FORMAT_NUMBER)

            self.percent_0_decimals = f.add_format()
            self.percent_0_decimals.set_num_format(self.NUM_FORMAT_PERCENTAGE_NO_DECIMALS)

            self.percent_2_decimals = f.add_format()
            self.percent_2_decimals.set_num_format(self.NUM_FORMAT_PERCENTAGE_TWO_DECIMALS)

            self.center = f.add_format()
            self.center.set_align("center")

def shuffle(seq):
    for i in range(len(seq) - 1):
        j = random.randrange(i + 1, len(seq))
        temp = seq[i]
        seq[i] = seq[j]
        seq[j] = temp

def load_names_from_file(path):
    with io.open(path, "rt", encoding="utf8") as f:
        for line in f:
            name = line.strip()
            if len(name) > 0:
                yield name


if __name__ == "__main__":
    main()
