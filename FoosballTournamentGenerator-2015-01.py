import argparse
import io
import itertools
import random
import sys
import hashlib

def main():
    args = parse_arguments()
    tournament_generator = TournamentGenerator(args.names, args.random_number_generator)
    try:
        tournament = tournament_generator.run()
    except tournament_generator.Error as e:
        print("ERROR: {}".format(e), file=sys.stderr)
        sys.exit(1)


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("names_file")
    parser.add_argument("--random-seed")
    parsed_args = parser.parse_args()

    names_file_path = parsed_args.names_file
    try:
        with io.open(names_file_path, "rt", encoding="utf8") as f:
            names = []
            for line in f:
                line = line.strip()
                if line and line[0] != "#":
                    names.append(line)
    except (IOError, UnicodeDecodeError) as e:
        print("ERROR: unable to read names from file: {} ({})"
              .format(names_file_path, e), file=sys.stderr)
        sys.exit(2)

    random_seed = parsed_args.random_seed
    if random_seed is None:
        random_number_generator = random.Random()
    else:
        try:
            random_seed = int(random_seed)
        except ValueError:
            random_seed_bytes = random_seed.encode("utf8", errors="ignore")
            random_seed_bytes_sha1 = hashlib.sha1(random_seed_bytes).digest()
            random_seed = int.from_bytes(random_seed_bytes_sha1, byteorder="big")
        random_number_generator = random.Random(random_seed)

    return ParsedArguments(names, random_number_generator)


class TournamentGenerator:

    def __init__(self, names, random_number_generator):
        self.names = tuple(names)
        self.random_number_generator = random_number_generator

    def run(self):
        teams = tuple(self.generate_teams())
        print("Generated {} teams".format(len(teams)))
        matches = tuple(self.generate_matches(teams))
        print("Generated {} matches".format(len(matches)))

        opponent_counts = {x: {y: 0 for y in self.names} for x in self.names}
        for match in matches:
            for (player, other_team) in ((match[0][0], match[1]), (match[0][1], match[1]), (match[1][0], match[0]), (match[1][1], match[0])):
                for opponent in other_team:
                    opponent_counts[player][opponent] += 1

        for player1 in sorted(self.names):
            opponents = list((opponent_counts[player1][x], x) for x in self.names)
            opponents.sort(reverse=True)

            print("")
            print("Opponents of {}".format(player1))
            for (opponent_count, opponent) in opponents:
                print("  {} {}".format(opponent_count, opponent))


    def generate_teams(self):
        names = tuple(self.generate_randomized_ordering(self.names))
        teams = list(itertools.combinations(names, 2))
        yield from teams
        if len(teams) % 2 == 0:
            print("generate_teams() len(teams) % 2 == 0")
            return

        print("generate_teams() len(teams) % 2 != 0 -- generating more teams")
        names = tuple(self.generate_randomized_ordering(names))
        if len(names) % 2 != 0:
            print("generate_teams() len(names) % 2 != 0 -- doubling the names")
            names *= 2
        else:
            print("generate_teams() len(names) % 2 == 0")

        num_pairs = len(names) // 2
        for i in range(num_pairs):
            player1 = names[i * 2]
            player2 = names[(i * 2) + 1]
            yield (player1, player2)

    def generate_matches(self, teams):
        teams = list(teams)
        assert len(teams) % 2 == 0
        opponent_counts = {x: {y: 0 for y in self.names} for x in self.names}
        while teams:
            yield self._generate_match(teams, opponent_counts)

    def _generate_match(self, teams, opponent_counts):
        team1_index = self.random_number_generator.randrange(len(teams))
        team1 = teams[team1_index]
        del teams[team1_index]
        del team1_index
        team1_player1 = team1[0]
        team1_player2 = team1[1]

        team2_indices = self.generate_randomized_ordering(range(len(teams)))
        for team2_index in team2_indices:
            team2 = teams[team2_index]
            if team1_player1 in team2 or team1_player2 in team2:
                continue

            team2_player1 = team2[0]
            team2_player2 = team2[1]
            count1 = opponent_counts[team1_player1][team2_player1] + opponent_counts[team1_player1][team2_player2]
            count2 = opponent_counts[team1_player2][team2_player1] + opponent_counts[team1_player2][team2_player2]
            if count1 > 5 or count2 > 5:
                continue

            del teams[team2_index]

            opponent_counts[team1[0]][team2[0]] += 1
            opponent_counts[team1[1]][team2[0]] += 1
            opponent_counts[team1[0]][team2[1]] += 1
            opponent_counts[team1[1]][team2[1]] += 1
            opponent_counts[team2[0]][team1[0]] += 1
            opponent_counts[team2[1]][team1[0]] += 1
            opponent_counts[team2[0]][team1[1]] += 1
            opponent_counts[team2[1]][team1[1]] += 1

            return (team1, team2)
        else:
            raise Exception("unable to find match for team: {}".format(team1))

    def generate_randomized_ordering(self, elements):
        elements_remaining = list(elements)
        while elements_remaining:
            num_elements_remaining = len(elements_remaining)
            i = self.random_number_generator.randrange(num_elements_remaining)
            yield elements_remaining[i]
            del elements_remaining[i]

    class Error(Exception):
        pass


class ParsedArguments:

    def __init__(self, names, random_number_generator):
        self.names = names
        self.random_number_generator = random_number_generator


if __name__ == "__main__":
    main()
