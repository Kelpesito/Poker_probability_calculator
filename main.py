import tkinter as tk
import tkinter.messagebox as msb
from PIL import Image, ImageTk
import os
from treys import Card, Evaluator, Deck
from collections import Counter
import pyfiglet
from colorama import init, Fore, Style
from yaspin import yaspin
from yaspin.spinners import Spinners


CARDS_FOLDER = "Cards" # Ruta a las imágenes
CARD_SIZE = (80, 120)  # Tamaño de las cartas

SUITS_SYMBOLS = ["♠", "♥", "♦", "♣"]  # Símbolos de los palos
SUITS = {"♠": "s", "♥": "h", "♦": "d", "♣": "c"}  # Correspondecia símbolo -
                                                  # palo
# Valores
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
# Correspondencia símbolo - nombre (para sprites de las cartas)
SUIT_NAMES = {"♠": "Spades", "♥": "Hearts", "♦": "Diamonds", "♣": "Clubs"}

STAGES = {3: "Flop", 4: "Turn", 5: "River"}  # Etapas (número de cartas
                                             # comunitarias)

# Traducciones de las manos al español
TRADUCTIONS = {"Royal Flush": "Escalera Real",
               "Straight Flush": "Escalera de Color",
               "Four of a Kind": "Póquer", "Full House": "Full",
               "Flush": "Color", "Straight": "Escalera",
               "Three of a Kind": "Trío", "Two Pair": "Doble Pareja",
               "Pair": "Par", "High Card": "Carta Alta"}
# Emojis para cada tipo de mano
EMOJIS = {"Royal Flush": "🦚", "Straight Flush": "🌈", "Four of a Kind": "🃏",
          "Full House": "🫄", "Flush": "🎨", "Straight": "🪜",
          "Three of a Kind": "👪", "Two Pair": "💏💏", "Pair": "👯",
          "High Card": "🦅"}


# Función para mapear str de carta a dirección de imagen de carta
def map_card_image(card):
    """
    Parámetro:
    ----------
    card: str
        Carta. (Ej: "2♠")
    ----------
    Devuelve:
    ---------
    str
        Formato de nombre de carta en sprite (Ej: card2_Spades.png)
    """
    rank, suit = card
    if rank == "T":
        rank = "10"
    
    return f"card{SUIT_NAMES[suit]}_{rank}.png"
    

# Clase Selector de Cartas
class CardSelector:
    def __init__(self, root, N):
        """
        Parámetros:
        -----------
        rooot: tk.Tk
            Ventana donde se ejecutará el selector de cartas
        N: int
            Número mínimo de cartas seleccionables
        """
        
        self.N = N  # Número de cartas que debe haber como mínimo (2 si es
                    # mano, 3 si es comunitarias)
        self.root = root
        self.root.title("Selector de Cartas")
        self.selected_cards = []  # Lista para guardar las cartas seleccionadas
    
        # Imagen de fondo
        with Image.open(os.path.join(CARDS_FOLDER, "background.png")) as img:
            img = img.resize((1200, 700))
            self.bgd = ImageTk.PhotoImage(img)
        bg_label = tk.Label(root, image=self.bgd)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        
        # Frames para las cartas
        self.card_frame = tk.Canvas(root, width=1200, height=700,
                                    highlightthickness=0, bg="green")
        self.card_frame.place(x=0, y=0)
        self.card_frame.pack(pady=20)
        
        self.card_buttons = {}  # Diccionario para guardar nombre de carta -
                                # imagen
        self.card_images = []  # Lista para guardar imágenes
        
        # Mostrar cartas
        self.load_cards()
        
        # Mostrar cartas seleccionadas
        self.selection_label = tk.Label(root, text="Cartas seleccionadas:",
                                        font=("Arial", 14), bg="lightgray")
        self.selection_label.pack(pady=10)
        self.selection_display = tk.Label(root, text="", font=("Arial", 12),
                                          bg="lightgray")
        self.selection_display.pack()
        
        # Botón de aceptar
        self.accept_button = tk.Button(root, text="Aceptar", font=("Arial", 14, "bold"), bg="#A6D493",
                                       activebackground="#4F6445", activeforeground="white",
                                       fg="white", relief="raised", bd=3, padx=20, pady=5,
                                       command=self.accept_selection)
        self.accept_button.pack(pady=10)
        
    # Función para cargar las imágenes de las cartas   
    def load_cards(self):
        """
        Carga las imágenes de las cartas y los botones asociados
        """
        # Se recorre para cada palo y valor
        for i, suit in enumerate(SUITS_SYMBOLS):
            for j, rank in enumerate(RANKS):
                card = rank + suit
                #Cargar imagen
                img_path = os.path.join(CARDS_FOLDER, "Cards",
                                        map_card_image(card))
                with Image.open(img_path) as img:
                    img = img.resize(CARD_SIZE)
                
                img_tk = ImageTk.PhotoImage(img)
                self.card_images.append(img_tk)
                
                # Creación del botón 
                btn = tk.Button(self.card_frame, image=img_tk,
                                command=lambda c=card: self.select_card(c))
                btn.grid(row=i, column=j, padx=3, pady=3)
                self.card_buttons[card] = btn 
    
    # Función para seleccionar una carta
    def select_card(self, card):
        """
        Parámetro:
        ----------
        card: str
            Representación de una carta (Ej: 2♠)
        ----------
        Si la carta seleccionada está en la lista, se deselecciona.
        Si no, y además no se supera el límite (2 cartas, si es mano; 5, si son
        comunitarias), se añade a la lista
        Finalmente se actualiza la vista
        """
        if card in self.selected_cards:
            self.selected_cards.remove(card)
        elif len(self.selected_cards) < 2 and self.N == 2 \
            or len(self.selected_cards) < 5 and self.N == 3:
            self.selected_cards.append(card)
        self.update_display()

    # Función para actualizar la vista de las cartas seleccionadas
    def update_display(self):
        """
        Añade (o se elimina) al label donde se muestran las cartas seleccionadas
        """
        self.selection_display.config(text=", ".join(self.selected_cards))
    
    # Función para aceptar la selección (guardar las cartas seleccionadas)
    def accept_selection(self):
        """
        Si hay menos cartas de las que debería, muestra un aviso.
        Si no, se destruye la ventana (y continúa el programa)
        """
        if len(self.selected_cards) < self.N:
            msb.showwarning("Selección inválida",
                            f"Debes seleccionar al menos {self.N} cartas.")
            return
        self.root.destroy()


# Función para convertir el str de carta a formato de treys
def convert_treys_format(card):
    """
    Parámetro:
    ----------
    card: str
            Representación de una carta (Ej: 2♠)
    ----------
    Devuelve:
    ---------
    treys.Card
        Carta en el formato de treys
    """
    rank, suit = card
    suit = SUITS[suit]
    
    return Card.new(rank + suit)


# Función para hacer la simulación de Monte Carlo y calcular probabilidades
def MonteCarlo_simulation(hand, community, n_players, num_simulations=100000):
    """
    Parámetros:
    -----------
    hand: list[treys.Card]
        Mano del jugador
    community: list[treys.Card]
        Cartas comunitarias
    n_players: int
        Número de rivales
    num_simulations: int
        Número de simulaciones de Monte Carlo (100000)
    -----------
    Devuelve:
    ---------
    win_rate: float
        Probabilidad de ganar la mano
    tie_rate: float
        Probabilidad de empatar la mano
    loss_rate: float
        Probabilidad de perder la mano
    sorted_hand_probs: list[tuple[str, float]]
        Lista con las diferentes manos posibles y su probabilidad
    """
    evaluator = Evaluator()  # Instancia para evaluar manos
    # Inicializar contadores a 0
    wins, ties, losses = 0, 0, 0
    hand_type_counter = Counter()
    rank_class_counter = Counter()
    
    for _ in range(num_simulations):
        deck = Deck()
        # Remover cartas conocidas del mazo
        for card in hand+community:
            deck.cards.remove(card)

        # Repartir manos a los oponentes
        opponents_hands = []
        for _ in range(n_players):
            opp_hand = [deck.draw(1)[0], deck.draw(1)[0]]  # 2 cartas
            opponents_hands.append(opp_hand)

        # Completar las comunitarias hasta 5
        current_community = community[:]
        while len(current_community) < 5:
            current_community.append(deck.draw(1)[0])

        # Evaluar tu mano
        # Puntuación de la mano (cuanto menor, mejor)
        score = evaluator.evaluate(hand, current_community)
        # Rango de la mano(0 = Escalera Real - 9: Carta Alta)
        rank_class = evaluator.get_rank_class(score)
        # Convierte el rango a str
        hand_type = evaluator.class_to_string(rank_class)  
        hand_type_counter[hand_type] += 1
        rank_class_counter[rank_class] += 1

        # Evaluar las de los oponentes y quedarse con el mínimo
        best_opp_score = min(evaluator.evaluate(h, current_community)
                             for h in opponents_hands)
        
        # Comparación de puntuaciones
        if score < best_opp_score:
            wins += 1
        elif score == best_opp_score:
            ties += 1
        else:
            losses += 1
            
    # Calcular ratios
    win_rate = wins / num_simulations * 100
    tie_rate = ties / num_simulations * 100
    loss_rate = losses / num_simulations * 100
    sorted_hand_probs = [(htype, count / num_simulations * 100)
                         for htype, count in hand_type_counter.most_common()]
    
    return win_rate, tie_rate, loss_rate, sorted_hand_probs


if __name__ == "__main__":
    while True:
        os.system('cls')
        print(Fore.RED \
              + pyfiglet.figlet_format("Poker Probs")\
              + Style.RESET_ALL)
        
        # Introducir mano del jugador
        input(Fore.GREEN + "Seleccionar mano (Enter): " + Style.RESET_ALL)
        root = tk.Tk()
        root.geometry("1200x700")
        app = CardSelector(root, 2)
        root.mainloop()
        hand = app.selected_cards
        print(Fore.GREEN \
              + f"Mano seleccionada:", Fore.RED, *hand, "\n" \
              + Style.RESET_ALL)

        # Introducir cartas comunitarias
        input(Fore.GREEN \
              + "Seleccionar cartas comunitarias (Enter): " \
              + Style.RESET_ALL)
        root = tk.Tk()
        root.geometry("1200x700")
        app = CardSelector(root, 3)
        root.mainloop()
        community = app.selected_cards
        print(Fore.GREEN \
              + f"Cartas seleccionadas:", Fore.RED, *community,
              f"({STAGES[len(community)]})","\n" \
              + Style.RESET_ALL)
        
        # Introducir número de rivales
        n_players = int(input(Fore.GREEN \
                              + "Introducir número de rivales: " \
                              + Fore.RED))
        print(Style.RESET_ALL)
        
        # Convertir cartas en instancias de treys
        hand = [convert_treys_format(card) for card in hand]
        community = [convert_treys_format(card) for card in community]
        
        # Calcular las probabilidades
        with yaspin(Spinners.runner,
                    text=Fore.GREEN \
                         + f"Calculando probabilidades..."
                         + Style.RESET_ALL) as sp:
            win_rate, tie_rate, loss_rate, sorted_hand_probs = \
                MonteCarlo_simulation(hand, community, n_players)
            sp.ok("✅")
        
        print()
        # Mostrar resultados
        print(Fore.GREEN \
              + f"👑 Probabilidad de victoria: {round(win_rate, 4)}%" \
              + Style.RESET_ALL)
        print(Fore.YELLOW \
              + f"🫤 Probabilidad de empate: {round(tie_rate, 4)}%" \
              + Style.RESET_ALL)
        print(Fore.RED \
              + f"🗿 Probabilidad de perder: {round(loss_rate, 4)}%" \
              + Style.RESET_ALL)
        
        print()
        print(Style.BRIGHT + Fore.GREEN \
              + f"Probabilidad de cada mano:" \
              + Style.RESET_ALL)
        for htype, prob in sorted_hand_probs:
            print(Fore.GREEN \
                  + f"{EMOJIS[htype]} {TRADUCTIONS[htype]}: " \
                  + f"{Fore.RED}{round(prob, 4)}%" \
                  + Style.RESET_ALL)
        
        print()
        cont = input(Fore.GREEN + f"Continuar [y/n]? {Fore.RED}")
        print(Style.RESET_ALL)
        if cont.lower() == "n":
            break
        