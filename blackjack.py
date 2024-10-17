from fasttea import FastTEA, Model, Msg, CSSFramework, Element
from fasttea.html import h1, h3, p, div, img, button
from fasttea.picocss import container, grid, group
import random

from pydantic import BaseModel, computed_field
from typing import List
from enum import Enum


class Suit(str, Enum):
    HEARTS = 'hearts'
    DIAMONDS = 'diamonds'
    CLUBS = 'clubs'
    SPADES = 'spades'


class Rank(str, Enum):
    TWO = '2'
    THREE = '3'
    FOUR = '4'
    FIVE = '5'
    SIX = '6'
    SEVEN = '7'
    EIGHT = '8'
    NINE = '9'
    TEN = '10'
    JACK = 'J'
    QUEEN = 'Q'
    KING = 'K'
    ACE = 'A'


class GameState(str, Enum):
    INITIAL = 'Initial'
    BETTING = 'Betting'
    PLAYER_TURN = 'PlayerTurn'
    DEALER_TURN = 'DealerTurn'
    GAME_OVER = 'GameOver'


class Card(BaseModel):
    suit: Suit
    rank: Rank

    @computed_field
    def value(self) -> int:
        if self.rank == Rank.ACE:
            return 11
        elif self.rank in [Rank.JACK, Rank.QUEEN, Rank.KING]:
            return 10
        else:
            return int(self.rank.value)


class BlackjackModel(Model):
    deck: List[Card] = []
    player_hand: List[Card] = []
    dealer_hand: List[Card] = []
    game_state: GameState = GameState.INITIAL
    bet: int = 0
    balance: int = 1000

    def init_deck(self) -> None:
        self.deck = [Card(suit=suit, rank=rank) for suit in Suit for rank in Rank]
        self.shuffle_deck()

    def shuffle_deck(self) -> None:
        random.shuffle(self.deck)

    def __init__(self, **data):
        super().__init__(**data)
        self.init_deck()

    def calculate_hand_value(self, hand: List[Card]) -> int:
        total = sum(card.value for card in hand)
        num_aces = sum(1 for card in hand if card.rank == Rank.ACE)

        while total > 21 and num_aces > 0:
            total -= 10
            num_aces -= 1

        return total


app = FastTEA(BlackjackModel(), css_framework=CSSFramework.PICO)


def deal(model: BlackjackModel) -> BlackjackModel:
    if 0 < model.bet <= model.balance:
        model.player_hand = [model.deck.pop(), model.deck.pop()]
        model.dealer_hand = [model.deck.pop()]
        model.game_state = GameState.PLAYER_TURN
        model.balance -= model.bet
    return model


def hit(model: BlackjackModel) -> BlackjackModel:
    if model.game_state == GameState.PLAYER_TURN:
        model.player_hand.append(model.deck.pop())
        if model.calculate_hand_value(model.player_hand) > 21:
            model.game_state = GameState.GAME_OVER
    return model


def stand(model: BlackjackModel) -> BlackjackModel:
    model.game_state = GameState.DEALER_TURN
    while model.calculate_hand_value(model.dealer_hand) < 17:
        model.dealer_hand.append(model.deck.pop())
    model.game_state = GameState.GAME_OVER
    return model


def place_bet(model: BlackjackModel, amount: int) -> BlackjackModel:
    if amount <= model.balance and model.game_state == GameState.INITIAL:
        model.bet = amount
    return model


def evaluate_game(model: BlackjackModel) -> BlackjackModel:
    if model.game_state == GameState.GAME_OVER:
        player_value = model.calculate_hand_value(model.player_hand)
        dealer_value = model.calculate_hand_value(model.dealer_hand)
        if player_value > 21:
            model.game_state = GameState.GAME_OVER
        elif dealer_value > 21:
            model.game_state = GameState.GAME_OVER
            model.balance += model.bet * 2
        elif player_value > dealer_value:
            model.game_state = GameState.GAME_OVER
            model.balance += model.bet * 2
        elif player_value < dealer_value:
            model.game_state = GameState.GAME_OVER
        else:
            model.game_state = GameState.GAME_OVER
            model.balance += model.bet
    return model


@app.update
def update(msg: Msg, model: BlackjackModel) -> tuple[BlackjackModel, None]:
    if msg.action == "Deal":
        model = deal(model)
    elif msg.action == "Hit":
        model = hit(model)
    elif msg.action == "Stand":
        model = stand(model)
    elif msg.action == "Restart":
        balance = model.balance
        new_model = BlackjackModel()
        new_model.balance = balance
        return new_model, None
    elif msg.action.startswith("PlaceBet"):
        amount = int(msg.action.split("_")[1])
        model = place_bet(model, amount)

    model = evaluate_game(model)
    return model, None


@app.view
def view(model: BlackjackModel) -> Element:
    return container({"style":"transform: scale(0.8); transform-origin: 0 0;"}, [

            div({},[
                h1({}, "Blackjack"),
                view_hands(model),
                view_controls(model),
                view_bet_and_balance(model),
                p({"style": "font-size: 12px;"}, "Card images provided by https://kenney.nl")
            ])
    ])


def view_hands(model: BlackjackModel) -> Element:
    return div({},
        [
            h3({}, "Dealer Hand"),
            view_hand(model.dealer_hand),
            p({}, f"Value: {model.calculate_hand_value(model.dealer_hand)}"),
            h3({}, "Player Hand"),
            view_hand(model.player_hand),
            p({}, f"Value: {model.calculate_hand_value(model.player_hand)}")
        ]
    )


def view_hand(hand: list[Card]) -> Element:
    return div({"style": "display: flex; flex-wrap: wrap; gap: 10px;"}, [view_card(card) for card in hand])
    #return grid({}, [view_card(card) for card in hand])

def get_card_image_name(card:Card)->str:
    return f'card_{card.suit.value}_{card.rank.value}.png'

def get_card_letter(card:Card)->str:
    letter = {
        'hearts':'♥',
        'diamonds': '♦',
        'clubs' : '♣',
        'spades' : '♠'}

    return letter[card.suit.value]

def view_card(card: Card) -> Element:
    return img({"src": f"/static/cards/"+get_card_image_name(card),
                "style": "width: 100px; height: auto;",
                "alt": f"{card.rank.value} of {card.suit.value}"})


def view_controls(model: BlackjackModel) -> Element:
    return group({},
        [
            button({"onClick": "Deal", "disabled": "true" if model.game_state != GameState.INITIAL or model.bet == 0 else None}, "Deal"),
            button({"onClick": "Hit", "disabled": "true" if model.game_state != GameState.PLAYER_TURN else None}, "Hit"),
            button({"onClick": "Stand", "disabled": "true" if model.game_state != GameState.PLAYER_TURN else None}, "Stand"),
            button({"onClick": "Restart"}, "Restart")
        ]
    )


def view_bet_and_balance(model: BlackjackModel) -> Element:
    return div({},
        [
            p({}, f"Balance: ${model.balance}"),
            p({}, f"Current Bet: ${model.bet}"),
            group({},
                [
                    button(
                        {
                            "onClick": f"PlaceBet_{amount}",
                            "disabled": "true" if model.game_state != GameState.INITIAL else None
                        },
                        f"Bet ${amount}"
                    )
                    for amount in [10, 25, 50]
                ]
            )
        ]
    )

app.run()