import io
import random


def main():
    names = load_names_from_file("names.txt")
    app = FoozeballTournamentGenerator(names)
    app.run()
    app.print_games()
    app.print_opponent_counts()

class FoozeballTournamentGenerator:

    def __init__(self, names):
        self.names = tuple(names)
        self.days = []

    def run(self):
        while not self.days_completed():
            self.generate_day()

    def days_completed(self):
        game_counts = set()
        for name in self.names:
            num_games = self.num_games_scheduled_for(name)
            game_counts.add(num_games)

        if len(game_counts) > 1:
            return False
        else:
            game_count = next(iter(game_counts))
            return game_count > len(self.names)

    def num_games_scheduled_for(self, name):
        count = 0
        for unused in self.get_scheduled_partners(name):
            count += 1
        return count

    def get_scheduled_partners(self, name):
        for day in self.days:
            for game in day:
                if game[0] == name:
                    yield game[1]
                elif game[1] == name:
                    yield game[0]
                elif game[2] == name:
                    yield game[3]
                elif game[3] == name:
                    yield game[2]

    def num_games_scheduled_as_partners(self, name1, name2):
        count = 0
        for partner in self.get_scheduled_partners(name1):
            if partner == name2:
                count += 1
        return count

    def get_scheduled_opponents(self, name):
        for day in self.days:
            for game in day:
                if game[0] == name or game[1] == name:
                    yield game[2]
                    yield game[3]
                elif game[2] == name or game[3] == name:
                    yield game[0]
                    yield game[1]

    def num_games_scheduled_as_opponents(self, name1, name2):
        count = 0
        for opponent in self.get_scheduled_opponents(name1):
            if opponent == name2:
                count += 1
        return count

    def generate_day(self):
        games = []
        self.days.append(games)

        names_remaining = list(self.get_randomly_ordered_names_for_day())
        while len(names_remaining) >= 4:
            name1 = names_remaining[0]
            del names_remaining[0]

            partner_counts = {x: self.num_games_scheduled_as_partners(name1, x)
                for x in names_remaining}
            partner_min_count = min(partner_counts.values())
            name2_found = False
            for name2 in names_remaining:
                if partner_counts[name2] == partner_min_count:
                    names_remaining.remove(name2)
                    break
            else:
                raise Exception("should never get here")

            name3 = names_remaining[0]
            del names_remaining[0]

            partner_counts = {x: self.num_games_scheduled_as_partners(name3, x)
                for x in names_remaining}
            partner_min_count = min(partner_counts.values())
            name4_found = False
            for name4 in names_remaining:
                if partner_counts[name4] == partner_min_count:
                    names_remaining.remove(name4)
                    break
            else:
                raise Exception("should never get here")

            games.append((name1, name2, name3, name4))

            if self.days_completed():
                break

    def get_randomly_ordered_names_for_day(self):
        game_count_names_map = {}
        for name in self.names:
            game_count = self.num_games_scheduled_for(name)
            if game_count in game_count_names_map:
                game_count_names_map[game_count].append(name)
            else:
                game_count_names_map[game_count] = [name]

        while len(game_count_names_map) > 0:
            game_count = min(game_count_names_map)
            names = game_count_names_map[game_count]
            del game_count_names_map[game_count]
            while len(names) > 0:
                name = random.choice(names)
                yield name
                names.remove(name)

    def print_games(self):
        for (day_index, games) in enumerate(self.days):
            print("")
            print("Day {}".format(day_index+1))
            print("")
            for (game_index, game) in enumerate(games):
                print("Game {}: {} & {} vs. {} & {}".format(
                    game_index + 1, game[0], game[1], game[2], game[3]))

    def print_opponent_counts(self):
        for name in sorted(self.names):
            opponents = {x:0 for x in self.names}
            for day in self.days:
                for game in day:
                    if name == game[0] or name == game[1]:
                        opponents[game[2]] += 1
                        opponents[game[3]] += 1
                    elif name == game[2] or name == game[3]:
                        opponents[game[0]] += 1
                        opponents[game[1]] += 1

            opponent_counts = [(opponents[x], x) for x in opponents]
            opponent_counts.sort()
            opponent_counts.reverse()

            print("")
            print("{} opponents:".format(name))
            for (count, opponent_name) in opponent_counts:
                print("  {} {}".format(count, opponent_name))


def load_names_from_file(path):
    with io.open(path, "rt", encoding="utf8") as f:
        for line in f:
            name = line.strip()
            if len(name) > 0:
                yield name


if __name__ == "__main__":
    main()
