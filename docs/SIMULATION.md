# PoolMind Advanced Physics Simulator - Dokumentacja Implementacji

## 🎯 Realizacja Milestones

### ✅ **Milestone 1: Podstawowa Fizyka Kul** - UKOŃCZONE
**Implementacja:** `scripts/demo/physics_simulator.py`

**Zrealizowane funkcje:**
- ✅ Klasa `Ball` z wektorami prędkości (vx, vy) i fizycznymi właściwościami
- ✅ Tarcie i stopniowe spowalnianie kul (`friction = 0.98`)
- ✅ Detekcja kolizji między kulami (odległość < 2*radius)
- ✅ Sprężyste odbicia między kulami z zachowaniem pędu
- ✅ Ograniczenie ruchu do granic stołu
- ✅ Klasa `PhysicsEngine` zarządzająca całą symulacją fizyki

**Kluczowe komponenty:**
```python
class Ball:
    def __init__(self, ball_id, x, y, ...):
        self.vx = 0.0  # prędkość x
        self.vy = 0.0  # prędkość y
        self.friction = 0.98  # współczynnik tarcia

    def update_physics(self, dt):
        # Aktualizacja pozycji i aplikacja tarcia

class PhysicsEngine:
    def _resolve_ball_collision(self, ball1, ball2):
        # Fizyka sprężystych odbić
```

### ✅ **Milestone 2: Odbicia od Band** - UKOŃCZONE
**Zrealizowane funkcje:**
- ✅ Detekcja kolizji z bandami stołu (lewa, prawa, górna, dolna)
- ✅ Odbicia z zachowaniem kąta (kąt padania = kąt odbicia)
- ✅ Utrata energii przy odbiciu (`wall_restitution = 0.7`)
- ✅ Separacja kul przy nakładaniu się

**Implementacja:**
```python
def _handle_wall_collision(self, ball):
    if ball.x - ball.radius <= self.table_x_min:
        ball.x = self.table_x_min + ball.radius
        ball.vx = -ball.vx * self.wall_restitution
```

### ✅ **Milestone 3: System Łuz i Wpadania Kul** - UKOŃCZONE
**Zrealizowane funkcje:**
- ✅ 6 łuz rozmieszczonych realistycznie (4 narożne + 2 środkowe)
- ✅ Efekt "wciągania" kuli w pobliżu łuzy
- ✅ Automatyczne wykluczanie kul po wpadnięciu
- ✅ Komunikaty o wpadnięciu kul

**Implementacja:**
```python
def _check_pocket_collisions(self, balls):
    for pocket_x, pocket_y in self.pocket_positions:
        if distance_to_pocket <= self.pocket_radius:
            if distance_to_pocket <= ball.radius:
                ball.active = False  # Kula wpadła
            else:
                # Efekt wciągania
                ball.vx += dx * force_strength / distance_to_pocket
```

### ✅ **Milestone 4: Symulacja Uderzeń Kija** - UKOŃCZONE
**Zrealizowane funkcje:**
- ✅ Interaktywne celowanie myszką (click + drag)
- ✅ Wizualizacja linii celowania
- ✅ Wskaźnik siły uderzenia
- ✅ Aplikacja impulsu do kuli białej
- ✅ Presety siły (klawisze 1-5)
- ✅ Losowe uderzenia (SPACE)

**Implementacja:**
```python
def apply_cue_strike(self, cue_ball, target_x, target_y, force):
    dx = target_x - cue_ball.x
    dy = target_y - cue_ball.y
    # Normalizacja i aplikacja siły
    cue_ball.apply_impulse(nx * force, ny * force)
```

### ✅ **Milestone 5: Zaawansowane Scenariusze** - UKOŃCZONE
**Implementacja:** `scripts/demo/enhanced_simulation.py`

**Zrealizowane scenariusze:**
- ✅ `standard_break` - Standardowe ustawienie rozbicia
- ✅ `scattered_balls` - Kule rozproszone po stole
- ✅ `corner_pocket` - Trening łuzy narożnej
- ✅ `bank_shot` - Trening odbić od bandy
- ✅ `combination_shot` - Trening uderzeń kombinowanych
- ✅ `defense_position` - Pozycje obronne
- ✅ `end_game` - Scenariusz końcowy (8-ball + kilka kul)

**Klasa ScenarioManager:**
```python
class ScenarioManager:
    def __init__(self, virtual_table):
        self.scenarios = {
            "standard_break": self._setup_standard_break,
            "scattered_balls": self._setup_scattered_balls,
            # ... inne scenariusze
        }
```

### ✅ **BONUS: System Zapisywania/Odtwarzania** - UKOŃCZONE
**Implementacja:** `scripts/demo/replay_system.py`

**Dodatkowe funkcje:**
- ✅ Nagrywanie sekwencji ruchu kul
- ✅ Zapis do plików JSON
- ✅ Odtwarzanie z kontrolą prędkości
- ✅ Analiza statystyk ruchu
- ✅ Detekcja kolizji i wpadnięć
- ✅ Generowanie raportów

## 🚀 Kompletna Integracja z PoolMind Pipeline

### Enhanced Simulation (`enhanced_simulation.py`)
**Funkcje:**
- ✅ Pełna integracja z systemem detekcji ArUco
- ✅ Pipeline: Virtual Table → ArUco → Homography → Detection → Tracking → Game Engine
- ✅ Overlay z wizualizacją wykrytych kul
- ✅ Web interface integration (FrameHub)
- ✅ Real-time FPS monitoring
- ✅ Interaktywne sterowanie scenariuszami

### Sterowanie i Kontrola
**Klawisze:**
- `SPACE` - Pauza/wznowienie
- `N/P` - Następny/poprzedni scenariusz
- `R` - Reset kul
- `1-5` - Presety siły uderzenia
- `D` - Toggle debug overlay
- `Q/ESC` - Wyjście
- `Mouse Click+Drag` - Celowanie i uderzenie

## 🎮 Użycie

### Podstawowy symulator fizyki:
```bash
export PYTHONPATH="$(pwd)/src"
python scripts/demo/physics_simulator.py
```

### Rozszerzony symulator z scenariuszami:
```bash
export PYTHONPATH="$(pwd)/src"
python scripts/demo/enhanced_simulation.py
```

### System replay:
```bash
export PYTHONPATH="$(pwd)/src"
python scripts/demo/replay_system.py
```

## 🔧 Konfiguracja

Wszystkie parametry fizyki można dostosować w konstruktorach:

```python
# Fizyka kul
ball.friction = 0.98          # Tarcie (0-1)
ball.min_velocity = 0.1       # Minimalna prędkość

# Fizyka kolizji
physics.restitution = 0.8     # Sprężystość kolizji kul
physics.wall_restitution = 0.7 # Sprężystość odbić od bandy

# Łuzy
physics.pocket_radius = 25.0   # Promień łuzy
```

## 📊 Funkcje Analizy

System replay oferuje szczegółową analizę:
- **Statystyki ruchu:** odległość, prędkość, czas aktywności każdej kuli
- **Detekcja kolizji:** automatyczne wykrywanie zderzeń między kulami
- **Śledzenie wpadnięć:** monitoring kul wpadających do łuz
- **Analiza uderzeń:** segmentacja i analiza pojedynczych uderzeń

## 🎯 Osiągnięcia

✅ **Wszystkie 5 głównych milestones zrealizowane**
✅ **Dodatkowy system replay i analizy**
✅ **Pełna integracja z pipeline'em PoolMind**
✅ **Interaktywne sterowanie i scenariusze**
✅ **Realistyczna fizyka z zachowaniem pędu**
✅ **Scalabilny system do dalszego rozwoju**

Symulator jest teraz kompletnym narzędziem do testowania, treningu i rozwoju systemu PoolMind z realistyczną fizyką kul bilardowych.

## 🎮 Dostępne Skrypty Symulacyjne

### 1. **Virtual Table Simulator** (`scripts/demo/virtual_table.py`)
Generuje syntetyczny obraz stołu bilardowego z markerami ArUco i simulowanymi kulami.

```bash
cd PoolMind
export PYTHONPATH="$(pwd)/src"
./scripts/demo/virtual_table.py
```

**Funkcje:**
- ✅ Realistyczny wygląd stołu bilardowego
- ✅ 4 markery ArUco w prawidłowych pozycjach (0,1,2,3)
- ✅ 15 kul w formacji trójkąta + bila
- ✅ Animowane ruchy kul
- ✅ Interaktywne wpadanie kul (SPACE)

**Sterowanie:**
- `SPACE` - Wpadnięcie losowej kuli
- `R` - Reset kul do pozycji początkowej
- `Q/ESC` - Wyjście

### 2. **Enhanced Simulation** (`scripts/demo/enhanced_simulation.py`)
Kompletna symulacja pipeline'u PoolMind z wirtualnym stołem.

```bash
cd PoolMind
export PYTHONPATH="$(pwd)/src"
./scripts/demo/enhanced_simulation.py --scenario break_shot
```

**Testy:**
- ✅ Detekcja markerów ArUco
- ✅ Detekcja kul (HoughCircles)
- ✅ Klasyfikacja kolorów kul
- ✅ Wizualizacja wyników
- ✅ Pomiar wydajności (FPS)

**Dostępne scenariusze:**
- `break_shot` - Rozbicie
- `corner_pocket` - Łuza narożna
- `side_pocket` - Łuza środkowa
- `bank_shot` - Odbicie od bandy
- `cluster` - Grupa kul
- `safety_play` - Gra obronna
- `final_balls` - Końcówka gry

### 3. **Physics Simulator** (`scripts/demo/physics_simulator.py`)
Zaawansowana symulacja fizyki z realistycznymi kolizjami.

```bash
cd PoolMind
export PYTHONPATH="$(pwd)/src"
./scripts/demo/physics_simulator.py
```

**Fizyka:**
- ✅ Kolizje między kulami z zachowaniem pędu
- ✅ Odbicia od band z stratą energii
- ✅ System łuz z efektem wciągania
- ✅ Symulacja uderzeń kija
- ✅ Tarcie i spowalnianie kul

**Sterowanie:**
- `Mouse Click+Drag` - Celowanie i uderzenie
- `1-5` - Presety siły uderzenia
- `SPACE` - Losowe uderzenie
- `R` - Reset kul
- `Q/ESC` - Wyjście

### 4. **Camera Test Tool** (`scripts/tools/camera_test.py`)
Test z prawdziwą kamerą USB/wbudowaną.

```bash
cd PoolMind
export PYTHONPATH="$(pwd)/src"
./scripts/tools/camera_test.py --camera 0
```

**Funkcje:**
- ✅ Test różnych kamer (`--camera 0,1,2...`)
- ✅ Lista dostępnych kamer (`--list-cameras`)
- ✅ Detekcja markerów ArUco na żywo
- ✅ Detekcja kul na zielonym tle
- ✅ Maska obszaru stołu
- ✅ Zapis klatek (`S`)

**Sterowanie:**
- `A` - Przełącz markery ArUco
- `B` - Przełącz detekcję kul
- `T` - Przełącz maskę stołu
- `S` - Zapisz bieżącą klatkę
- `Q/ESC` - Wyjście

## 🛠️ Konfiguracja Skryptów

Wszystkie skrypty używają pliku `config/config.yaml`. Można dostosować:

```yaml
camera:
  width: 1280
  height: 720
  fps: 30

detection:
  hsv_green_lower: [35, 30, 30]   # Zakres koloru zielonego stołu
  hsv_green_upper: [85, 255, 255]
  ball_min_radius: 8              # Min promień kuli
  ball_max_radius: 18             # Max promień kuli
  hough_dp: 1.2                   # Parametry HoughCircles
  hough_min_dist: 16
  hough_param1: 120
  hough_param2: 18

calibration:
  corner_ids: [0, 1, 2, 3]        # ID markerów ArUco
  table_w: 2000                   # Wymiary stołu (piksele)
  table_h: 1000
```

## 🎯 Przypadki Użycia

### Rozwój bez sprzętu
Użyj `enhanced_simulation.py` do:
- Testowania algorytmów detekcji
- Rozwoju interfejsu użytkownika
- Debugowania logiki gry
- Demonstracji funkcji

### Kalibracja kamery
Użyj `camera_test.py` do:
- Testowania jakości obrazu
- Sprawdzania detekcji markerów
- Dostosowania parametrów HSV
- Optymalizacji pozycji kamery

### Integracja systemu
Użyj `physics_simulator.py` do:
- Trenowania AI/modeli
- Generowania danych testowych
- Testowania pipeline'u end-to-end
- Prezentacji dla klientów

## 📊 Benchmark Wydajności

| Skrypt | FPS (typowe) | Użycie CPU | Opis |
|--------|--------------|-----------|------|
| `virtual_table.py` | 30+ | Niskie | Tylko generowanie obrazu |
| `enhanced_simulation.py` | 20-30 | Średnie | Pipeline CV |
| `physics_simulator.py` | 25-35 | Średnie | Fizyka + rendering |
| `camera_test.py` | 15-25 | Średnie-Wysokie | Kamera + CV |
