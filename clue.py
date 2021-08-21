from dataclasses import dataclass
import traceback
import random
import itertools

import constraint


@dataclass
class Player:
    name: str
    hand: list

    def take_turn(self):
        print('this is your hand:', self.hand)
        while True:
            command = input('What do you want to do? [suggest, accuse]: ')

            if command == 'suggest':
                while True:
                    suggestion = input('Suggest? (person,weapon,room): ')

                    try:
                        person, weapon, room = suggestion.split(',')

                        if not person in game.people:
                            print(f'{person} not in {game.people}')
                            continue
                        if not weapon in game.weapons:
                            print(f'{weapon} not in {game.weapons}')
                            continue
                        if not room in game.rooms:
                            print(f'{room} not in {game.rooms}')
                            continue

                        return Suggestion(self.name, person, weapon, room)
                    except Exception as e:
                        print('Could not understand you, please try again')
                        traceback.print_exc()
                        continue
            elif command == 'accuse':
                while True:
                    suggestion = input('Accuse? (person,weapon,room): ')

                    try:
                        person, weapon, room = suggestion.split(',')

                        if not person in game.people:
                            print(f'{person} not in {game.people}')
                            continue
                        if not weapon in game.weapons:
                            print(f'{weapon} not in {game.weapons}')
                            continue
                        if not room in game.rooms:
                            print(f'{room} not in {game.rooms}')
                            continue

                        return Accusation(self.name, person, weapon, room)
                    except Exception as e:
                        print('Could not understand you, please try again')
                        traceback.print_exc()
                        continue
            else:
                print('Please choose one of [suggest, accuse].')
                continue

    def respond_to_suggestion(self, suggestion):
        print(f'{self.name}, do you have any cards that disprove this? ')
        suggested_cards_in_hand = [
            c for c in self.hand if c in suggestion.cards]

        if not any(suggested_cards_in_hand):
            return Pass(self.name)
        else:
            while True:
                card_to_show = input(f'Choose a card from {suggested_cards_in_hand}: ')

                if not card_to_show in suggested_cards_in_hand:
                    print(
                        'That wasn\t a card that matches the suggestion.')
                    continue
                else:
                    # suggesting_player.get_shown(self.name, card_to_show)
                    return ShowedCard(self.name, card_to_show)

    def get_shown(self, otherplayer_name, card):
        print(f'{otherplayer_name} showed {self.name} {card}.')

    def add_card(self, card):
        self.hand.append(card)

    def suggestion_disproved(self, suggestion, disproving_player_name):
        pass


class SimpleConstraintAIPlayer(Player):
    """ Keep track of the cards in hand and the ones that have been shown. """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.problem = constraint.Problem()
        self.problem.addVariable('person', Clue.people)
        self.problem.addVariable('weapon', Clue.weapons)
        self.problem.addVariable('room', Clue.rooms)

    def add_card(self, card):
        self.problem.addConstraint(constraint.NotInSetConstraint(card))
        self.hand.append(card)

    def get_shown(self, showed_card):
        print(f'{showed_card.player_name} showed {self.name} {showed_card.card}')
        self.problem.addConstraint(
            constraint.NotInSetConstraint(showed_card.card))

    def suggestion_disproved(self, suggestion, disproving_player_name):
        pass

    def respond_to_suggestion(self, suggestion):
        suggested_cards_in_hand = [
            c for c in self.hand if c in suggestion.cards]

        if not any(suggested_cards_in_hand):
            return Pass(self.name)
        else:
            card_to_show = random.sample(suggested_cards_in_hand, k=1)[0]
            # suggesting_player.get_shown(self.name, card_to_show)
            return ShowedCard(self.name, card_to_show)

    def take_turn(self):
        # TODO need to inspect events? and add somenotinsetconstraints
        solutions = self.problem.getSolutions()
        print(f'{self.name}', len(solutions), solutions if len(solutions) < 10 else None)

        if len(solutions) == 1:   # certainty is 1, accuse
            s = solutions[0]
            return Accusation(self.name, s['person'], s['weapon'], s['room'])

        else:  # still a possibility
            s = random.sample(solutions, k=1)[0]
            return Suggestion(self.name, s['person'], s['weapon'], s['room'])


class BetterConstraintAIPlayer(SimpleConstraintAIPlayer):
    """ keep track of what card other players have revealed. """

    def suggestion_disproved(self, suggestion, disproving_player_name):
        self.problem.addConstraint(
            constraint.SomeNotInSetConstraint(suggestion.cards))


@dataclass
class Pass:
    player_name: str


@dataclass
class ShowedCard:
    player_name: str
    card: str


@dataclass
class Suggestion:
    player_name: str
    person: str
    weapon: str
    room: str

    @property
    def cards(self):
        return self.person, self.weapon, self.room


@dataclass
class Accusation(Suggestion):
    pass


class Win(Exception):
    pass


class Clue:
    people = ('scarlet', 'plum', 'green', 'mustard', 'white', 'blue')
    weapons = ('pipe', 'knife', 'candlestick', 'rope', 'gun', 'wrench')
    rooms = ('dining', 'kitchen', 'billiards', 'ball',
             'hall', 'conservatory', 'library', 'study', 'lounge')

    full_deck = people + weapons + rooms

    def __init__(self, *args, **kwargs):
        self.players = []
        self.events = []
        self.clues = None
        self.turncount = 0
        self.setup(*args, **kwargs)

    def setup(self, n_real_players=1, n_players=4, aiplayer=itertools.cycle([SimpleConstraintAIPlayer])):
        people, weapons, rooms = list(Clue.people), list(
            Clue.weapons), list(Clue.rooms)
        p = random.sample(people, k=1)[0]
        people.remove(p)
        w = random.sample(weapons, k=1)[0]
        weapons.remove(w)
        r = random.sample(rooms, k=1)[0]
        rooms.remove(r)
        self.clues = (p, w, r)

        print('SECRET:', self.clues)

        deck = people + weapons + rooms
        print(deck)
        print(len(Clue.full_deck), len(deck))
        random.shuffle(deck)

        players = [Player(name=str(i), hand=[]) for i in range(n_real_players)]
        players.extend([next(aiplayer)(name=str(i), hand=[])
                        for i in range(n_real_players, n_players)])
        random.shuffle(players)

        while deck:
            for p in players:
                try:
                    p.add_card(deck.pop())
                except IndexError:
                    break

        self.players = players
        print(self.players)
        return self

    def suggest(self, suggestion):
        self.events.append(suggestion)

        print(suggestion)

        # starting with the player to the left of the current player...
        curr_player = [p for p in self.players if p.name ==
                       suggestion.player_name][0]
        curr_idx = self.players.index(curr_player)
        for player in self.players[curr_idx+1:] + self.players[:curr_idx]:
            response = player.respond_to_suggestion(suggestion)
            print(response)
            self.events.append(response)

            if isinstance(response, ShowedCard):
                curr_player.get_shown(response)

                for p in self.players:
                    p.suggestion_disproved(suggestion, player.name)

                break

    def accuse(self, accusation):
        self.events.append(accusation)
        print(accusation)

        if accusation.cards == self.clues:
            print(f'Player {accusation.player_name} has won!')
            raise Win(accusation.player_name)
        else:
            print(f'Player {accusation.player_name} has made an incorrect accusation. They lose.')

            # remove them from the turn order
            player = [p for p in self.players if p.name ==
                      accusation.player_name][0]
            self.players.remove(player)

            # redistribute cards
            while player.hand:
                for p in self.players:
                    try:
                        p.add_card(player.hand.pop())
                    except IndexError:
                        break

    def run(self):
        self.turncount = 0
        while self.players:
            for player in self.players:
                try:
                    self.turncount += 1
                    print(f'#{self.turncount}: Player {player.name}\'s turn')
                    response = player.take_turn()

                    if isinstance(response, Accusation):
                        self.accuse(response)
                    if isinstance(response, Suggestion):
                        self.suggest(response)

                except Win as e:
                    self.winner = e
                    return self


def run_experiment(n_runs=100, **kwargs):
    import sys
    import time

    with open('test.log', 'w') as f:
        _stdout = sys.stdout
        sys.stdout = f
        t1 = time.time()
        runs = [Clue(**kwargs).run()
                for i in range(n_runs)]
        t2 = time.time()
        sys.stdout = _stdout

    print(kwargs)
    print(n_runs, 'runs in', t2 - t1, 'average = ', (t2 - t1) / n_runs)
    avg_turns = sum(r.turncount for r in runs) / len(runs)
    print('Average Turns: ', avg_turns)
    wins = {}
    for r in runs:
        wins.setdefault(str(r.winner), 0)
        wins[str(r.winner)] += 1

    print('Wins:', wins)
    return wins, avg_turns


if __name__ == '__main__':
    # c = Clue(n_real_players=0)
    # c.run()
    onegoodplayer = itertools.cycle(
        [BetterConstraintAIPlayer, SimpleConstraintAIPlayer, SimpleConstraintAIPlayer])
    allgoodplayer = itertools.cycle([BetterConstraintAIPlayer])
    nogoodplayer = itertools.cycle([SimpleConstraintAIPlayer])

    run_experiment(n_runs=1000, n_real_players=0,
                   n_players=3, aiplayer=nogoodplayer)
    run_experiment(n_runs=1000, n_real_players=0,
                   n_players=3, aiplayer=onegoodplayer)
    run_experiment(n_runs=1000, n_real_players=0,
                   n_players=3, aiplayer=allgoodplayer)
    run_experiment(n_runs=100, n_real_players=0,
                   n_players=4, aiplayer=onegoodplayer)
    run_experiment(n_runs=100, n_real_players=0,
                   n_players=5, aiplayer=onegoodplayer)
    run_experiment(n_runs=100, n_real_players=0,
                   n_players=6, aiplayer=onegoodplayer)
