#!/usr/bin/env python3

import argparse
import collections
import io
import random
import statistics
import sys
import xlsxwriter


def main():
    (names_path, xlsx_path) = parse_args()
    print("Loading player names from file: {}".format(names_path))
    names = load_names_from_file(names_path)
    print("Generating teams")
    team_generator = FoosballTeamListGenerator(names, min_games_per_player=0)
    teams = team_generator.generate()
    print("Generating matches")
    match_generator = FoosballMatchListGenerator(teams)
    matches = match_generator.generate()
    print("Generating tournament")
    tournament_generator = FoosballTournamentGenerator(matches)
    tournament = tournament_generator.generate()
    print("Writing Tournament to Excel file: {}".format(xlsx_path))
    xlsx_printer = TournamentXlsxPrinter(xlsx_path)
    xlsx_printer.run(tournament)
    text_printer = TournamentTextPrinter(sys.stdout)
    text_printer.run(tournament)

def parse_args():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-n", "--names-file", default="names.txt")
    arg_parser.add_argument("-o", "--output-excel-file", default="FoosballTournament.xlsx")
    parsed_args = arg_parser.parse_args()
    return (parsed_args.names_file, parsed_args.output_excel_file)

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

    def __init__(self, match_list):
        self.match_list = match_list

    def generate(self):
        tournament = FoosballTournament()
        matches = list(self.match_list)
        players = frozenset(self.match_list.players())
        shuffle(matches)

        while len(matches) > 0:
            cur_match_list = FoosballMatchList()

            match_index = len(matches)
            while match_index > 0:
                match_index -= 1
                match = matches[match_index]

                for player in match.players():
                    if cur_match_list.includes_player(player):
                        match_can_be_added_to_cur_match_list = False
                        break
                else:
                    match_can_be_added_to_cur_match_list = True

                if match_can_be_added_to_cur_match_list:
                    cur_match_list.add_match(match)
                    del matches[match_index]

            tournament.add_match_list(cur_match_list)

            # move matches with unused players to the end of the list so they will be used by
            # priority next time
            unused_players = set(players - set(cur_match_list.players()))
            for i in range(len(matches)):
                match = matches[i]
                for unused_player in unused_players:
                    if match.includes_player(unused_player):
                        move_match = True
                        break
                else:
                    move_match = False

                if move_match:
                    del matches[i]
                    matches.append(match)
                    for player in match.players():
                        if player in unused_players:
                            unused_players.remove(player)

        return tournament


class FoosballMatch:

    def __init__(self, team1, team2):
        self.team1 = team1
        self.team2 = team2

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

    def __init__(self):
        self.matches = []

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
        for (day_index, match_list) in enumerate(tournament):
            self.println("Day {}".format(day_index + 1))
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
        workbook = xlsxwriter.Workbook(self.path)
        xls_info = self.XlsxInfo()
        self.write_schedule(tournament, workbook, xls_info)
        self.write_standings(tournament, workbook, xls_info)
        self.write_players(tournament, workbook, xls_info)
        workbook.close()

    def write_schedule(self, tournament, workbook, xls_info):
        worksheet = workbook.add_worksheet("Schedule")
        row = 0

        worksheet.write(row, 0, "Day")
        worksheet.write(row, 1, "Match")
        worksheet.write(row, 2, "Winner X")
        worksheet.write(row, 3, "Player 1")
        worksheet.write(row, 4, "Player 2")
        row += 1

        for (day_index, day) in enumerate(tournament):
            day_label = "Day {}".format(day_index + 1)
            worksheet.write(row, 0, day_label)
            row += 1

            for (match_index, match) in enumerate(day):
                match_label = "Match {}".format(match_index + 1)
                worksheet.write(row, 1, match_label)
                row += 1

                team_cells = []
                for (team_index, team) in enumerate(match.teams()):
                    if team_index > 0:
                        worksheet.write(row, 3, "vs.")
                        row += 1
                    col = 3
                    for player in team.players():
                        worksheet.write(row, col, player)
                        col += 1
                    row += 1

                    team_cells.append((team, row))

                xls_info.schedule_cells.append((match, day_label, match_label, team_cells))

        xls_info.schedule_last_row = row

    def write_standings(self, tournament, workbook, xls_info):
        worksheet = workbook.add_worksheet("Standings")

        row = 0
        for player in sorted(frozenset(tournament.players())):
            worksheet.write(row, 0, player)
            worksheet.write(row, 1,
                "="
                "COUNTIFS(Schedule!C1:C{last_row}, \"X\", Schedule!D1:D{last_row}, \"{name}\")"
                "+"
                "COUNTIFS(Schedule!C1:C{last_row}, \"X\", Schedule!E1:E{last_row}, \"{name}\")"
                .format(
                    last_row=xls_info.schedule_last_row,
                    name=player,
                ))
            row += 1

    def write_players(self, tournament, workbook, xls_info):
        for player in sorted(frozenset(tournament.players())):
            worksheet = workbook.add_worksheet(player)
            row = 0


            # write games
            worksheet.write(row, 0, "Scheduled Games".format(player))
            row += 2
            worksheet.write(row, 0, "Game")
            worksheet.write(row, 1, "Day")
            worksheet.write(row, 2, "Match")
            worksheet.write(row, 3, "WinLoss")
            worksheet.write(row, 4, "Partner")
            worksheet.write(row, 5, "Opponent 1")
            worksheet.write(row, 6, "Opponent 2")
            row += 1
            game_number = 1
            for (match, day_label, match_label, team_cells) in xls_info.schedule_cells:
                if not match.includes_player(player):
                    continue
                worksheet.write(row, 0, "Game #{}".format(game_number))
                game_number += 1
                worksheet.write(row, 1, day_label)
                worksheet.write(row, 2, match_label)

                win_row = None
                loss_row = None
                for (team, temp_row) in team_cells:
                    if team.includes_player(player):
                        win_row = temp_row
                    else:
                        loss_row = temp_row

                worksheet.write(row, 3,
                    "=IF(Schedule!C{}=\"X\", \"Win\", "
                        "IF(Schedule!C{}=\"X\", \"Loss\", \"\")"
                    ")"
                    .format(win_row, loss_row)
                )

                col = 4

                for team in match.teams_including_player(player):
                    for partner in team.players():
                        if partner != player:
                            worksheet.write(row, col, partner)
                            col += 1

                for team in match.teams():
                    if not team.includes_player(player):
                        for opponent in team.players():
                            worksheet.write(row, col, opponent)
                            col += 1

                row += 1
            row += 1

            # write partners
            partner_counts = collections.defaultdict(lambda: 0)
            for partner in tournament.player_partners(player):
                partner_counts[partner] += 1
            partner_counts = [(v, k) for (k, v) in partner_counts.items()]
            partner_counts.sort(reverse=True)

            worksheet.write(row, 0, "{} Partners".format(player))
            row += 2
            for (partner_count, partner) in partner_counts:
                worksheet.write(row, 0, partner)
                worksheet.write(row, 1, partner_count)
                row += 1
            row += 1

            # write opponents
            opponent_counts = collections.defaultdict(lambda: 0)
            for opponent in tournament.player_opponents(player):
                opponent_counts[opponent] += 1
            opponent_counts = [(v, k) for (k, v) in opponent_counts.items()]
            opponent_counts.sort(reverse=True)

            worksheet.write(row, 0, "{} Opponents".format(player))
            row += 2
            for (opponent_count, opponent) in opponent_counts:
                worksheet.write(row, 0, opponent)
                worksheet.write(row, 1, opponent_count)
                row += 1
            row += 1

    class XlsxInfo:
        def __init__(self):
            self.schedule_last_row = None
            self.schedule_cells = []


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
