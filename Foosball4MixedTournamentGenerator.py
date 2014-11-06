import argparse
import collections
import io
import itertools
import random
import statistics

def main():
    (players_path, min_num_matches_per_player, max_weeks) = parse_args()
    players = tuple(load_players(players_path))
    print("Loaded {} players".format(len(players)))

    while True:
        matches = generate_matches(players, min_num_matches_per_player)
        tournament = generate_tournament(matches)
        if max_weeks is not None:
            num_weeks = len(tournament) / 3
            if num_weeks > max_weeks:
                continue
        break

    print_tournament(tournament, matches, players)


def generate_matches(players, min_num_matches_per_player):
    print("Generating matches")
    match_generator = MatchGenerator(
        players, min_num_matches_per_player=min_num_matches_per_player)
    matches = match_generator.run()
    print("Generated {} matches".format(len(matches)))
    return matches


def generate_tournament(matches):
    print("Generating Tournament")
    tournament_generator = TournamentGenerator(matches)
    tournament = tournament_generator.run()
    tournament = tuple(tournament)
    return tournament


def print_tournament(tournament, matches, players):
    for player in sorted(players):
        print("")
        print("{} ({} appearances)".format(
            player, matches.num_player_appearances(player)))

        co_appearance_counts = [
            (matches.num_player_co_appearances(player, x), x)
            for x in sorted(players)
        ]
        co_appearance_counts.sort(reverse=True, key=lambda x: x[0])

        for (count, other_player) in co_appearance_counts:
            if player == other_player:
                continue
            print("   {} {}".format(count, other_player))

    print("")
    print("Tournament Schedule")

    week_num = 0
    day_num = 4
    for day in tournament:
        if day_num == 4:
            day_num = 1
            week_num += 1
            print("")
            print("Week {}".format(week_num))

        print("")
        print("   Day {}".format(day_num))

        for (match_num, match) in enumerate(day):
            print("")
            print("      Match {}".format(match_num + 1))
            for player in match.players():
                print("         {}".format(player))

        day_num += 1

    print("")
    print("Num Weeks: {}".format(week_num))
    print("Num Days: {}".format(len(tournament)))
    print("Num Matches: {}".format(sum(len(x) for x in tournament)))
    print("Max Matches Per Day: {}".format(max(len(x) for x in tournament)))
    print("Min Matches Per Day: {}".format(min(len(x) for x in tournament)))
    print("Avg Matches Per Day: {}".format(statistics.mean(len(x) for x in tournament)))

    matches_per_player = [matches.num_player_appearances(x) for x in players]
    print("Max Matches Per Player: {}".format(max(matches_per_player)))
    print("Min Matches Per Player: {}".format(min(matches_per_player)))
    print("Avg Matches Per Player: {}".format(statistics.mean(matches_per_player)))


def parse_args():
    arg_parser = argparse.ArgumentParser();
    arg_parser.add_argument("players_file")
    arg_parser.add_argument("--min-num-matches-per-player", "-m", type=int)
    arg_parser.add_argument("--max-weeks", "-w", type=int)
    parsed_args = arg_parser.parse_args()
    return (
        parsed_args.players_file,
        parsed_args.min_num_matches_per_player,
        parsed_args.max_weeks,
    )


class TournamentGenerator:

    def __init__(self, matches):
        self.matches = matches

    def run(self):
        players = tuple(set(self.matches.players()))
        matches = FoosballItemList(self.matches)

        while len(matches) > 0:
            day_matches = self.generate_day(matches, players)
            day_matches = tuple(day_matches)
            yield day_matches

    @classmethod
    def generate_day(cls, matches, players):
        unused_players = list(players)
        while len(matches) > 0 and len(unused_players) >= 4:
            match = cls.pick_match(matches, unused_players)
            if match is None:
                break
            yield match
            matches.remove(match)
            for player in match.players():
                unused_players.remove(player)

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

        for cur_players in itertools.combinations(self.players, 4):
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

        return Match(
            min_players[0], min_players[1], min_players[2], min_players[3])

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

    def __init__(self, player1, player2, player3, player4):
        self.player1 = player1
        self.player2 = player2
        self.player3 = player3
        self.player4 = player4

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


def load_players(path):
    print("Loading player list from file: {}".format(path))
    with io.open(path, "rt", encoding="utf8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                yield line


if __name__ == "__main__":
    main()
