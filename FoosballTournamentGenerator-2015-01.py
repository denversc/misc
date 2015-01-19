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
