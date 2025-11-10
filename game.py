#!/usr/bin/env python
#
#
#   B  L  A  C  K  J  A  C  K 
#        G  A  M  E 
#     I N   P Y T H O N 
#
#  AUTHOR: Felix Gillberg TE24, LICENSE: MIT
#

import random
import json
from enum import Enum, auto
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Any

# ==================== ENUMS ====================

class GameState(Enum): #In c++ or any static language we can write enum class but here we need to import the Enum from enum library but we it still gets the work done 
    BETTING = auto() #the auto function here automatically assigns values to the ENUM members after its position, 1, 2, 3 ...
    PLAYER_TURN = auto() #see the documentation on PyPi.org 
    DEALER_TURN = auto()
    ROUND_OVER = auto()
    GAME_OVER = auto() #Normally we would like to set this to False but it needs to be assigned at runtime since it is 'situational' 

class RoundResult(Enum):
    VICTORY = auto()
    LOSS = auto()
    TIE = auto()
    BLACKJACK = auto()
    BUSTED = auto()

# ==================== CARD ====================

class Card:
    def __init__(self, suit: str, rank: str):
        self.suit = suit #Initialize our Card properties, these are suit & rank which are both of type string
        self.rank = rank
    
    @property                                         # Use of class attributes / decorators are preferred by the author 
    def value(self) -> int:
        if self.rank in ['J', 'Q', 'K']:
            return 10       #10, J, Q, K are all of value 10 by DEFAULT according to the BlackJack rules 
        elif self.rank == 'A':
            return 11  # Or 1 but we will handle the exception later on 
        return int(self.rank)
    
    def __str__(self):
        return f"{self.rank}{self.suit[0]}" # Just STD behavior in terms of __str__ output, i.e. nothing special 

# ==================== DECK ====================

class Deck:
    def __init__(self, num_decks: int = 6): #My teacher said it would be about six decks in the game, so set it to default 6, can be changed.
        self.num_decks = num_decks
        self.cards: List[Card] = [] #Simple array (Originally we were going to use a doubly linked list, but the author found it easier to implement an array-like Deck since it is only six decks of cards and not one thousand - so O(n) doesn't cause that much trouble 
        self._build_deck() # Method for constructing the deck, assign suit , rank etc.
        self.shuffle()  # Method for shuffling / mixing the cards 
    
    def _build_deck(self):
        self.cards = []
        for _ in range(self.num_decks):
            for suit in ['Hearts', 'Diamonds', 'Clubs', 'Spades']:
                for rank in ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']:
                    self.cards.append(Card(suit, rank)) 
    
    def shuffle(self):
        random.shuffle(self.cards) #The use of the RANDOM Library API
    
    def draw(self) -> Card: #Return the Card type; 
        if not self.cards:
            self._build_deck() # Build the deck if self.cards doesn't already exist
            self.shuffle()
        return self.cards.pop() 
    
    def __len__(self):
        return len(self.cards) # private logic method for len() 

# ==================== HAND ====================

class Hand:
    def __init__(self):
        self.cards: List[Card] = [] 
        self.bet: int = 0
    
    @property
    def value(self) -> int:
        value = sum(card.value for card in self.cards)
        aces = sum(1 for card in self.cards if card.rank == 'A')
        while value > 21 and aces > 0:
            value -= 10
            aces -= 1
        return value
    
    @property
    def is_blackjack(self) -> bool:
        return len(self.cards) == 2 and self.value == 21
    
    @property
    def is_busted(self) -> bool:
        return self.value > 21
    
    def add_card(self, card: Card):
        self.cards.append(card)
    
    def clear(self):
        self.cards.clear()
        self.bet = 0
    
    def __str__(self):
        return ' '.join(str(card) for card in self.cards)

# ==================== PLAYER ====================

class Player:
    def __init__(self, name: str, bankroll: int = 1000):
        self.name = name
        self.bankroll = bankroll
        self.hand = Hand()
    
    def place_bet(self, amount: int) -> bool:
        if amount <= self.bankroll:
            self.hand.bet = amount
            self.bankroll -= amount
            return True
        return False
    
    def reset_hand(self):
        self.hand.clear()
    
    def __str__(self):
        return f"{self.name} (${self.bankroll})"

# ==================== MAIN GAME ====================

class BlackjackGame:
    """ Class for the main game loop & logic, we need to specify num_decks and bets, edit num_decks after request
        In this class we will have a structured public: and private:, just like in C++ we keep heavy logic and calculations in the private section and the public section will contain the information / results of calculations
    """
    def __init__(self, num_decks: int = 6, min_bet: int = 10, max_bet: int = 500):
        self.deck = Deck(num_decks)
        self.player = Player("Player")
        self.dealer_hand = Hand()
        self.min_bet = min_bet
        self.max_bet = max_bet
        self.game_state = GameState.BETTING #Default state of the game 
        self.round_result: Optional[RoundResult] = None
    
    def place_bet(self, amount: int) -> bool: # Either player is Playing, or not Playing
        if self.game_state != GameState.BETTING:
            return False
        
        if amount < self.min_bet or amount > self.max_bet:
            return False
        
        if self.player.place_bet(amount):
            self._start_round()
            return True
        return False
    
    def _start_round(self):
        self.player.reset_hand() #Call all the methods in the correct order to initialize the round 
        self.dealer_hand.clear()
        
        self.player.hand.add_card(self.deck.draw())
        self.dealer_hand.add_card(self.deck.draw())
        self.player.hand.add_card(self.deck.draw())
        self.dealer_hand.add_card(self.deck.draw())
        
        self.game_state = GameState.PLAYER_TURN
        
        if self.player.hand.is_blackjack:
            self._handle_blackjack() 
    
    def _handle_blackjack(self):
        if self.dealer_hand.cards[0].value >= 10:
            if len(self.dealer_hand.cards) == 2 and self.dealer_hand.value == 21:
                self.round_result = RoundResult.TIE
                self.player.bankroll += self.player.hand.bet
            else:
                self.round_result = RoundResult.BLACKJACK
                self.player.bankroll += int(self.player.hand.bet * 2.5)
        else:
            self.round_result = RoundResult.BLACKJACK
            self.player.bankroll += int(self.player.hand.bet * 2.5)
        
        self.game_state = GameState.ROUND_OVER
    
    def hit(self) -> bool:
        if self.game_state != GameState.PLAYER_TURN:
            return False
        
        self.player.hand.add_card(self.deck.draw())
        
        if self.player.hand.is_busted:
            self.round_result = RoundResult.BUSTED
            self.game_state = GameState.ROUND_OVER
        return True
    
    def stand(self) -> bool:
        if self.game_state != GameState.PLAYER_TURN:
            return False
        
        self._dealer_play()
        return True
    
    def _dealer_play(self):
        self.game_state = GameState.DEALER_TURN
        
        while self.dealer_hand.value < 17:  # Game AI
            self.dealer_hand.add_card(self.deck.draw())
        
        self._determine_round_result()
    
    def _determine_round_result(self):
        player_value = self.player.hand.value
        dealer_value = self.dealer_hand.value
        
        if self.player.hand.is_busted:
            self.round_result = RoundResult.BUSTED
        elif self.dealer_hand.is_busted:
            self.round_result = RoundResult.VICTORY
            self.player.bankroll += self.player.hand.bet * 2
        elif player_value > dealer_value:
            self.round_result = RoundResult.VICTORY
            self.player.bankroll += self.player.hand.bet * 2
        elif player_value < dealer_value:
            self.round_result = RoundResult.LOSS
        else:
            self.round_result = RoundResult.TIE
            self.player.bankroll += self.player.hand.bet
        
        self.game_state = GameState.ROUND_OVER
    
    def start_new_round(self):
        if self.game_state != GameState.ROUND_OVER:
            return
        
        self.game_state = GameState.BETTING
        self.round_result = None
    
    def get_game_info(self) -> Dict[str, Any]: #Return a hashmap / dictionary with key and values, aligns with JSON format aswell.
        return { 
            'game_state': self.game_state,
            'round_result': self.round_result,
            'player_bankroll': self.player.bankroll,
            'player_hand': str(self.player.hand),
            'player_value': self.player.hand.value,
            'dealer_hand': str(self.dealer_hand),
            'dealer_value': self.dealer_hand.value,
            'dealer_up_card': str(self.dealer_hand.cards[0]) if self.dealer_hand.cards else None,
            'can_hit': self.game_state == GameState.PLAYER_TURN and not self.player.hand.is_busted,
            'can_stand': self.game_state == GameState.PLAYER_TURN,
            'deck_size': len(self.deck)
        }

# ==================== SIMPLE SAVE SYSTEM ====================

class SaveSystem:
    """ Class for saving Javascript-Object-Notation formatted data in a file, specify time + date  """
    def __init__(self, save_dir: str = "saves"):
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(exist_ok=True)
    
    def save_game(self, player: Player, filename: str = None) -> str:
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"blackjack_{timestamp}.json"
        
        save_path = self.save_dir / filename
        
        save_data = {
            'player_name': player.name,
            'bankroll': player.bankroll,
            'save_date': datetime.now().isoformat()
        }
        
        with open(save_path, 'w', encoding='utf-8') as f: # -r-xx-w write permission for the file, specify UTF-8
            json.dump(save_data, f, indent=2)
        
        return str(save_path)

# ==================== MAIN ====================

def main(): #Since the author codes in C++ and Rust he will implement a main() function similar to int main(int argc, char **argv)
    game = BlackjackGame()
    save_system = SaveSystem()
    
    print("=== Blackjack Game ===")
    
    while game.player.bankroll > game.min_bet:
        info = game.get_game_info()
        
        if info['game_state'] == GameState.BETTING:
            print(f"\n--- Round Start ---")
            print(f"Bankroll: ${info['player_bankroll']}")
            print(f"Cards remaining: {info['deck_size']}")
            
            bet_input = input(f"Enter bet amount (${game.min_bet}-${game.max_bet}): ").strip()
            try:
                bet = int(bet_input)
                if game.place_bet(bet):
                    print(f"Bet placed: ${bet}")
                else:
                    print("Invalid bet amount")
            except ValueError:
                print("Please enter a valid number")
        
        elif info['game_state'] == GameState.PLAYER_TURN:
            print(f"\n--- Your Turn ---")
            print(f"Your hand: {info['player_hand']} (Value: {info['player_value']})")
            print(f"Dealer shows: {info['dealer_up_card']}")
            
            if info['can_hit']:
                action = input("(h)it or (s)tand? ").lower()
                if action == 'h':
                    game.hit()
                elif action == 's':
                    game.stand()
                else:
                    print("Invalid action")
            else:
                game.stand()
        
        elif info['game_state'] == GameState.ROUND_OVER:
            print(f"\n--- Round Over ---")
            print(f"Your hand: {info['player_hand']} ({info['player_value']})")
            print(f"Dealer hand: {info['dealer_hand']} ({info['dealer_value']})")
            print(f"Result: {info['round_result'].name}")
            print(f"New Bankroll: ${info['player_bankroll']}")
            
            if input("Save game? (y/n): ").lower() == 'y':
                save_path = save_system.save_game(game.player)
                print(f"Game saved to: {save_path}")
            
            game.start_new_round()
    
    print("\n=== Game Over ===")
    print("You're out of money!")

if __name__ == "__main__":
    main()
