# Projekt z przedmiotu systemy rekomendacji
## System rekomendacji bohaterów dla gry dota 2

## Założenia
Projekt dotyczy systemu rekomendacji dla fazy wyboru bohaterów typu All picks. 
All pick można podzielić na dwie fazy. W pierwszej każdy z graczy w tym samym czasie banuje jednego z bohaterów (mogą się powtarzać).
Każdy ze zbanowanych bohaterów ma 50% szans na zbanowanie w danej rozgrywce. 
W kolejnej fazie parami dwóch graczy z przeciwnych drużyn wybiera postacie. Jeśli wybrali takich samych bohaterów to wybór jest powtarzany. 

Ideą systemu jest traktowanie fazy wyborów jako gry kombinatorycznej. W związku z tym może być ona reprezentowana za pomocą drzewa, na którym wywoływany będzie algorytm monte carlo tree search. Ostateczna rekomendacja zaproponowana jest na podstawie ilorazu zwycięstw oraz liczby odwiedziń danego węzła w drzewie.
![zalozenia](https://github.com/roudie/dota_mcts/blob/master/plots/system.PNG)
## Dane
Dane zawierają 1.9mln meczy dla all picks i dotyczą 119 bohaterów.
Każdy z meczy zawiera informacje o wyniku, pickach, banach oraz innych uzyskanych wynikach w grze.

## Ekstrakcja cech 
Synergia - macierz prawdopodobieństwa wygranej, w drużynie w której współwystępuje para bohaterów.

Counter pick - macierz prawdopodobieństwa wygranej, gdzie w jednej drużynie występuje dany bohater, natomiast w przeciwnej inny.

Wybory postaci są kodowane metodą one hot

## Model predykcji wyniku
Jednym z potrzebnych elementów w algorytmie mcts jest informacja o wyniku symulowanej gry. Aby stworzyć model predykcyjny wykorzystano dane z meczy na których trenowano modele takie jak: MLP, LinearSVM, SGD. Najlepsze wyniki dawał model LinearSVM wynoszące 59% accuracy.

## Walidacja

