import math, time, random, pygame as pg

# Diese classes sind nur für das Typing notwendig
class Player:...
class Enemy:...
class Menue:...
class Level_up_Menue(Menue):...

def collision(pos1:list[int], pos2:list[int], radius1:int, radius2:int)->bool: 
    """Überprüft, ob 2 Kreise kollidieren"""
    return math.sqrt((pos1[0]-pos2[0])**2 + (pos1[1]-pos2[1])**2) <= radius1 + radius2
def collision2(pos1:list[int], pos2:list[int], radius1:int, width2:int, height2:int)->bool: 
    """Überprüft, ob 1 Rechteck und 1 Kreis kollidieren"""
    minx2 = pos2[0] - width2 / 2
    miny2 = pos2[1] - height2 / 2
    testx = maxx2 = pos2[0] + width2 / 2
    testy = maxy2 = pos2[1] + height2 / 2
    if minx2 <= pos1[0] <= maxx2 and miny2 <= pos1[1] <= maxy2: iscollision = True  # überprüft ob der Kreis im Rechteck ist
    else:                                                                           # überprüft ob der Kreis das Rechteck berührt
        if (minx2 + maxx2) / 2 > pos1[0]: testx = minx2   # der Kreis ist links sonst rechts
        if (miny2 + maxy2) / 2 > pos1[1]: testy = miny2   # der Kreis ist oberhalb sonst unterhalb
        iscollision = math.sqrt((pos1[0] - testx) ** 2 + (pos1[1] - testy) ** 2) <= radius1
    return iscollision



class Shot:
    def __init__(self, position:list[int], vx:int, vy:int, damage:int, screen:pg.Surface):
        '''vx und vy in %. vx und vy können auch negativ sein.'''
        self.pos = position[::]         # kopiert die Inhalte des Spielerpositionsliste, ohne dass die beiden Listen verknüpft werden
        self.color = "#555555"
        self.radius = 3
        self.speed = 8
        self.vx = self.speed * vx       # bestimmt die Geschwindigkeit des Schusses in x und y richtung
        self.vy = self.speed * vy
        self.damage = damage            # übernimmt den Spielerschaden
        self.screen = screen
    
    def draw(self):
        '''stellt den Schuss auf dem Screen dar''' 
        pg.draw.circle(self.screen, self.color, (self.pos),self.radius)

    def move(self):
        self.pos[0] += self.vx
        self.pos[1] += self.vy
        # Überprüfung, ob der Schuss außerhalb des Screens ist. Wenn ja, wird er glöscht
        if self.pos[0] <= 0 or self.pos[0] >= self.screen.get_width(): shots.remove(self); del self; return None
        if self.pos[1] <= 0 or self.pos[1] >= self.screen.get_height(): shots.remove(self); del self; return None

        for enemy in enemies:   # Überprüft, ob Schuss und Gegner kollidieren. Wenn ja, wird dem Gegner Schaden zugefügt und der Schuss gelöscht
            if collision(enemy.pos, self.pos, enemy.radius, self.radius):
                enemy.hit(self.damage)
                shots.remove(self); del self
                return None



class Bar:
    def __init__(self, maximum:int, color:str, width:int = 50, height:int = 8, spacing:int = 1):
        self.color = color
        self.width = width      # Gesamtbreite
        self.height = height
        self.spacing = spacing
        try: 
            self.colom_width = self.width / maximum - self.spacing   # Breite eines Kästchens     # - spacing: für klare unterteilung
        except ZeroDivisionError: self.colom_width = self.width      # falls das Maximum == 0

    def draw(self, x:int, y:int, amount:float|int, screen:pg.Surface) -> tuple[int|float]:
        '''stellt die Bar auf dem Screen dar''' 
        x1 = x - (self.width) / 2       # definiert die Eckkoordinaten der Bar
        y1 = y - 30 - self.height / 2
            
        pg.draw.rect(screen, "black", pg.Rect(x1, y1, self.width, self.height))         # Bar outline
        x1 += self.spacing
        for _ in range(amount):
            pg.draw.rect(screen, self.color, 
                         pg.Rect(x1, y1 + self.spacing / 2, self.colom_width, self.height - self.spacing / 2))      # zeichnet die Kästchen
            x1 += self.colom_width + self.spacing                                       # geht zum nächsten Kästchen
        return x1, y1


class HealthBar(Bar):
    def __init__(self, max_health:int, width:int = 50, height:int = 8, spacing:int = 1):
        super().__init__(max_health, "red", width, height, spacing)
    
    def draw(self, x:int, y:int, health:float|int, screen:pg.Surface):
        '''stellt die Healthbar auf dem Screen dar''' 
        half = False                    # benötigt für halbe Leben
        if type(health) == float:
            health = int(health)
            half = True
        x1, y1 = super().draw(x, y, health, screen)
        if half:                                                                        # zeichnet halbes Kästchen
            pg.draw.rect(screen, self.color,  pg.Rect(x1, y1 + self.height / 2 - self.spacing / 2, self.colom_width, self.height / 2)) 
            x1 += self.spacing

        
class XpBar(Bar):
    def __init__(self, needed_xp:int, width:int = 200, height:int = 16, spacing:int = 2):
        self.max = needed_xp
        super().__init__(needed_xp, "#00cc00", width, height, spacing)


class Drop:
    def __init__(self, position:list[int], type:int, screen:pg.Surface):
        '''Es werden zwei Arten an Drops von den Gegnern nach deren Tötung hinterlassen.
        type == 1: kleiner Drop; 1 Erfahrungspunkt
        type == 2: großer Drop; 5 Erfahrungspunkte'''
        self.pos = position[::]                 # kopiert die Inhalte des Gegnerpositionsliste, ohne dass die beiden Listen verknüpft werden
        self.value = 1 if type == 1 else 5      # setzt die eigenschaften je nach Typ
        self.color = "#00ff00" if type == 1 else "#008800"
        self.width = 10 if type == 1 else 15
        self.screen = screen
    
    def draw(self):
        '''stellt den Drop auf dem Screen dar''' 
        pg.draw.rect(self.screen, self.color, pg.Rect(self.pos[0] - self.width / 2, self.pos[1] - self.width / 2, self.width, self.width))  #  zeichnet den Drop auf den Screen

    def pick_up(self, player:Player):
        if collision2(player.pos, self.pos, player.radius, self.width, self.width):     # überprüft ob es mit dem Spieler kollidiert
            player.xp[0] += self.value      # überträgt dem Spieler seine Erfahrungspunkte
            self.destroy()

    def destroy(self):
        drops.remove(self)
        del self


class Enemy:
    def __init__(self, position:list[int], screen:pg.Surface, player:Player):
        self.pos = position
        self.color = "#aa0000"
        self.radius = 15
        self.speed = 1
        self.damage = 0.5
        self.health = 3
        self.max_health = 3
        self.last_hitted = time.time()                  # Zeit zum Überprüfen, ob dem Gegner Schaden zugefügt werden kann
        self.min_damage_cooldown = max_FPS / 240        # alle 0.25 sekunden kann dem Gegner geschadet werden
        self.screen = screen
        self.player = player

        self.healthbar = HealthBar(self.max_health)

    def draw(self): 
        '''stellt den Gegner auf dem Screen dar''' 
        self.healthbar.draw(*self.pos, self.health, self.screen)             # zeichnen der Healthbar auf de Screen
        pg.draw.circle(self.screen, self.color, self.pos, self.radius)       # zeichnen des Gegners auf den Screen

    def move(self):
        direction = {"0":False,"1":False,"2":False,"3":False}   # Speicher für Bewegungsrichtung
        if self.pos[0] < self.player.pos[0]: self.pos[0] += self.speed + random.randint(-1, 1); direction["0"] = True   # Bestimmung der Bewegungsrichtung zum Spieler hin
        if self.pos[0] > self.player.pos[0]: self.pos[0] -= self.speed + random.randint(-1, 1); direction["1"] = True   # zusätzliche Wackelbewegung durch randim.randint
        if self.pos[1] < self.player.pos[1]: self.pos[1] += self.speed + random.randint(-1, 1); direction["2"] = True
        if self.pos[1] > self.player.pos[1]: self.pos[1] -= self.speed + random.randint(-1, 1); direction["3"] = True

        for enemy in enemies:   # Überprüft, ob es kollisionen zwischen unterschiedlichen Gegnern gibt. Wenn ja, mache die Bewegung rückgängig
            if enemy == self: continue
            elif collision(self.pos, enemy.pos, self.radius, enemy.radius): 
                if direction["0"]: self.pos[0] -= self.speed
                if direction["1"]: self.pos[0] += self.speed
                if direction["2"]: self.pos[1] -= self.speed
                if direction["3"]: self.pos[1] += self.speed
                break
        
        # Überprüfung ob es eine Kollision mid dem Soieler gibt. Wenn ja, füge ihm Schaden zu
        if collision(self.pos, self.player.pos, self.radius, self.player.radius): self.player.hit(self.damage)
        
    def hit(self, damage:float):
        if time.time() - self.last_hitted >= self.min_damage_cooldown:  # Überprüft, ob der Gegener getroffen werden kann
            self.last_hitted = time.time()                              # erneuert den letzten Trefferzeitpunkt
            self.health -= damage
            if self.health <= 0:                                        # Überprüft ob der Gegner tot ist. Wenn ja, lösche ihn
                enemies.remove(self)
                self.drop()
                del self

    def drop(self):
        number = random.randint(0, 10)
        if number > 9: drops.append(Drop(self.pos, 2, self.screen))     # 10% Wahrscheinlichkeit auf einen großen Drop
        elif number > 4: drops.append(Drop(self.pos, 1, self.screen))   # 50% Wahrscheinlichkeit auf einen kleinen Drop
                                                                        # 40% auf keinen Drop



class Player:
    def __init__(self, screen:pg.Surface):
        self.pos = [screen.get_width()//2, screen.get_height()//2]      # startposition == Screen Mitte
        self.xp = [0]                                                   # Die Erfahrungspunkte sind in einer Liste gespeichert, um sie von jedem Punkt im Programm zu verändern
        self.level = 0
        self.needed_xp_for_lvl = 0
        self.color = "#0000aa"
        self.radius = 20
        self.speed = 3
        self.diagonal_speed = self.speed * math.sqrt(2) / 2     # langsamere Teilgeschwindigkeiten für diagonal Laufen, da der Spieler sonst schneller wäre
        self.health = 5
        self.max_health = 5
        self.damage = 1
        self.last_hitted = time.time()                  # Zeit zum Überprüfen, ob dem Spieler Schden zugefügt werden kann
        self.min_damage_cooldown = max_FPS / 120        # alle 0.5 Sekunden kann dem Spieler geschadet werden
        self.last_shot = time.time()                    # Zeit zum Überprüfen, ob der Spieler schießen kann
        self.min_shot_cooldown = 1                      # jede Sekunden kann der Spieler schießen
        self.screen = screen
        self.healthbar = HealthBar(self.max_health, 200, 16,2)
        self.healthbar_pos = [140, 52]
        self.xpbar_pos = [140, 104]
        self.font = pg.font.SysFont("Arial", 20, True)          # erstellt eine Schriftart

    def draw(self): 
        '''stellt den Spieler auf dem Screen dar''' 
        hp_label = self.font.render("HP: ", False, "black")                    # zeichnet die Schrift für die Healthbar auf den Screen
        self.screen.blit(hp_label, [10, 10])
        self.healthbar.draw(*self.healthbar_pos, self.health, self.screen)     # zeichnen der Healthbar auf den Screen

        self.xpbar = XpBar(self.needed_xp_for_lvl)
        xp_label = self.font.render("XP: ", False, "black")         # zeichnet die Schrift für die Xpbar auf den Screen
        self.screen.blit(xp_label, [10, 62])
        self.xpbar.draw(*self.xpbar_pos, self.xp[0], self.screen)   # zeichnen der Healthbar auf den Screen

        lvl_label = self.font.render("Level: ", False, "black")     # zeichnet die Schrift für das Level auf den Screen
        self.screen.blit(lvl_label, [10, 114])
        lvl_number = self.font.render(f"{self.level}", False, "black")
        self.screen.blit(lvl_number, (90, 114))

        pg.draw.circle(self.screen, self.color, self.pos, self.radius, 4)      # zeichnen des Spielers auf den Screen

    def move(self):
        double_counter = 0                  # Speicher für mehrfache Eingaben
        for key in key_check.keys():        # testet für gleichzeitige Eingabe 
            if key_check[key]:
                double_counter += 1
        if double_counter % 1 != 0:
            if key_check["w"]: self.pos[1] -= self.speed    # bewegt den Spieler entsprechend der Eingabe
            if key_check["s"]: self.pos[1] += self.speed    # w:hoch, s:runter, a:links, d:rechts
            if key_check["a"]: self.pos[0] -= self.speed
            if key_check["d"]: self.pos[0] += self.speed
        else:
            if key_check["w"]: self.pos[1] -= self.diagonal_speed
            if key_check["s"]: self.pos[1] += self.diagonal_speed
            if key_check["a"]: self.pos[0] -= self.diagonal_speed
            if key_check["d"]: self.pos[0] += self.diagonal_speed

        if self.pos[0]-self.radius <= 0: self.pos[0] += self.speed      # überprüft, ob der Spieler im Screen ist. Wenn nicht, bewege ihn wieder rein
        elif self.pos[0]+self.radius >= self.screen.get_width(): self.pos[0] -= self.speed
        if self.pos[1]-self.radius <= 0: self.pos[1] += self.speed
        elif self.pos[1]+self.radius >= self.screen.get_height(): self.pos[1] -= self.speed

    def _find_nearest_enemy(self) -> Enemy:
        '''gibt den nähesten Gegner zum Spieler zurück'''
        closest:list[float, Enemy] = [99999, None]                  # Zwischenspeicher des nähesten Gegners und dessen Distanz
        for enemy in enemies:
            distance = math.sqrt((self.pos[0]-enemy.pos[0])**2 + (self.pos[1]-enemy.pos[1])**2) # brechnet die Distanz
            if distance < closest[0]: closest = [distance, enemy]   # falls der neue Gegner näher ist, übernimm ihn und seine Distanz
        return closest[1]   # gibt nur den Gegner, nicht die Distanz zurück

    def shoot(self):
        if time.time() - self.last_shot > self.min_shot_cooldown:   # Überprüft, ob der Spieler schießen kann
            self.last_shot = time.time()                            # erneuert den letzten Schusszeitpunkt
            nearest = self._find_nearest_enemy()                    # Erlangen des nahesten Gegners als Ziel
            if nearest == None: return None                         # Überprüft, ob es noch Gegner gibt. Wenn nicht, breche die Funktion ab
            dx = nearest.pos[0] - self.pos[0]                       # Betimmung der x und y Differenz
            dy = nearest.pos[1] - self.pos[1]
            try: prozent_x = dx / (abs(dx) + abs(dy))               # Bestimmung der x und y Anteile 
            except ZeroDivisionError: prozent_x = 1
            try: prozent_y = dy / (abs(dx) + abs(dy))
            except ZeroDivisionError: prozent_y = 1
            shots.append(Shot(self.pos, prozent_x, prozent_y, self.damage, self.screen))    # Erstellung des Schusses

    def hit(self, damage:float):
        if time.time() - self.last_hitted >= self.min_damage_cooldown:  # Überprüft, ob der Spieler geschdet werden kann
            self.last_hitted = time.time()                              # erneuert den letzten Schadenszeitpunkt
            self.health -= damage
            if self.health <= 0:                                        # Überprüft, ob der Spieler tot ist. Wenn ja, beende die Spielschleife
                global main_run
                main_run = False

    def level_up(self):
        if self.xp[0] >= self.needed_xp_for_lvl:
            self.xp[0] -= self.needed_xp_for_lvl
            self.level += 1
            Level_up_Menue(self.screen)     # Um die Belohnung zu bekommen
            self.needed_xp_for_lvl = 5 * math.sqrt(self.level * 4)   
                # damit wird eine neue Anzahl benötigter Erfahrungspunkte für ein Aufleveln festgelegt
                # damit die benötigte Erfahrungspunkteanzahl nicht zu schnell zu groß wird eine Wurzelfunktion


class Menue:
    def __init__(self, screen:pg.Surface):
        self.screen = screen
        self.bg = "#545454"

        # erstellt alle benötigten Schriftarten
        self.title_font = pg.font.SysFont("Arial", 50, True) 
        self.title_font.set_underline(True)
        self.main_font = pg.font.SysFont("Arial", 30, True)
        self.second_font = pg.font.SysFont("Arial", 20, True)
        self.ui_handler()

    def ui_handler(self):
        menue_run = True
        while menue_run:                        # Menü loop
            self.screen.fill(self.bg)
            for event in pg.event.get():        # schließt das Menü, wenn der Knopf ("f") gedrückt wird
                if event.type==pg.KEYDOWN and event.key==pg.K_f: menue_run = False
            self.text()                         # zeichnet Menü abhängig unterschiedliche Sachen
            pg.display.update()
    
    def text(self):...

class StartMenue(Menue):
    def __init__(self, screen:pg.Surface, start:bool=True):
        # auf dem Startbildschirm werden Sprüche gezeigt
        self.oldtime = time.time()                      # Zeit vom letzten Spruch
        self.cooldown = 30                              # alle 30 Sekunden ein neuer Spruch
        self.img = pg.image.load("title_screen.png")    # speichert das Titelbild
        self.img = pg.transform.scale(self.img, (screen.get_width(), screen.get_height()))  # skaliert das Bild auf die Größe des Bildschirms
        self.quots = [                                  # Spruch liste
            "Manche Gegner sind buggy. Denk nicht drüber nach!",
            "Beweg dich um zu überleben.",
            "0% KI, 100% Verzweiflung",
            "Wir hätten was einfacheres machen sollen.",
            "Wir brauchen 15 Punkte bitti ♥️.",
            "TPA Original Production",
            "Foge uns auf GitHub: 'HinoopDev' und 'Jojofallguy'"
        ]
        self.current_quot = self.quots[random.randint(0, len(self.quots)-1)]
        if start: self.go_on_text = "Drücke den Knopf um das Spiel zu starten."
        else: self.go_on_text = "Drücke den Knopf um das Spiel fortzusetzen"
        super().__init__(screen)
    
    def text(self):
        self.screen.blit(self.img, (0,0))               # stellt das Bild auf dem Screen dar
        if time.time() - self.oldtime >= self.cooldown:
            self.current_quot = self.quots[random.randint(0, len(self.quots)-1)]
            self.oldtime = time.time()
        quot = self.main_font.render(self.current_quot, False, "black")                              # zeichnet den Spruch aus den Screen
        self.screen.blit(quot, ((self.screen.get_width() - quot.get_width()) / 2, self.screen.get_height() * 2 / 3 - quot.get_height() / 2))

        title = self.title_font.render("Call of Seminarkurs: Zomby Warfare", False, "black")
        self.screen.blit(title, ((self.screen.get_width() - title.get_width()) / 2, self.screen.get_height() / 3 - title.get_height()))

        ui_tipp = self.second_font.render(self.go_on_text, False, "#343434")
        self.screen.blit(ui_tipp, ((self.screen.get_width() - ui_tipp.get_width()) / 2, self.screen.get_height() - ui_tipp.get_height() * 4))

class Level_up_Menue(Menue):
    def __init__(self, screen):
        self.img = pg.image.load("level_up_screen.png")         # speichert das Titelbild
        self.img = pg.transform.scale(self.img, (screen.get_width(), screen.get_height()))      # skaliert das Bild auf die Größe des Bildschirms
        super().__init__(screen)

    def text(self):
        self.screen.blit(self.img, (0,0))       # stellt das Bild auf dem Screen dar



if __name__=="__main__":
    key_check={"w":False,"s":False,"a":False,"d":False}         # Eingabespeicher
    GRAS = "#44aa44"
    max_FPS = 60                                                # maximal mögliche Bildrate

    pg.init()                                                   # startet pygame
    screen = pg.display.set_mode(flags=pg.FULLSCREEN)           # Erstellung des Screens
    pg.display.set_caption(
        "Call of Seminarkurs: Zomby Warfare")
    screen.fill(GRAS)
    clock = pg.time.Clock()                                     # Initialisierung der FPSbegrenzung

    pg.font.init()                                              # Initialisierung des Font Moduls

    while True:                 # diese Schleife wird beim Demonstrieren nicht geschlossen, 
                                # damit das Programm auch nach Beenden einer Runde nicht geschlossen wird

        StartMenue(screen)      # Erstellt den Startbildschirm  vor Beginn jeder Runde

        player = Player(screen)                                                 # Erstellung des Spielers
        shots:list[Shot] = []; enemies:list[Enemy] = [];drops:list[Drop] = []   # Erstellung der Schuss-, Gegner- und Droplisten 
        for _ in range(10): enemies.append(Enemy([random.randint(0, screen.get_width()), 
                                                random.randint(0, screen.get_height())], 
                                                screen, player))  # Erstellung der Gegner

        main_run = True
        while main_run:                     # Spielschleife
            screen.fill(GRAS)               # Screen Zurücksetzung nach jedem Durchlauf
            clock.tick(max_FPS)             # Begrenzung der maximalen FPS, damit das Spiel nicht bei anderer Hardware zu schnell geht
            for event in pg.event.get():    # Screen Event handler, damit das Programm nicht freezed
                if event.type==pg.QUIT: main_run = False                                # Überprüt ob das Spiel geschlossen weren soll
                if event.type==pg.KEYDOWN and event.key==pg.K_w: key_check["w"] = True  # Überprüft, welche Eingaben für die Spielerbewegung getätigt werden
                if event.type==pg.KEYDOWN and event.key==pg.K_s: key_check["s"] = True  # und Speicherung in den Speicher
                if event.type==pg.KEYDOWN and event.key==pg.K_a: key_check["a"] = True
                if event.type==pg.KEYDOWN and event.key==pg.K_d: key_check["d"] = True
                if event.type==pg.KEYDOWN and event.key==pg.K_f: StartMenue(screen, False)  # Pause
                if event.type==pg.KEYUP and event.key==pg.K_w: key_check["w"] = False       # 'Löscht' die Eingaben aus dem Speicher
                if event.type==pg.KEYUP and event.key==pg.K_s: key_check["s"] = False
                if event.type==pg.KEYUP and event.key==pg.K_a: key_check["a"] = False
                if event.type==pg.KEYUP and event.key==pg.K_d: key_check["d"] = False

            for enemy in enemies: enemy.move(); enemy.draw()    # Bewegt und zeichnet die Gegner

            for shot in shots: shot.draw(); shot.move()         # Bewegt und zeichnet die Schüsse 
            # um Fehler zu vermeiden, wenn der Shot zerstört wurde, erst den Shot zeichnen und dann erst bewegen, da er dabei auch gelöscht werden kann

            for drop in drops: drop.draw(); drop.pick_up(player)    # zeichnet den Drop und lässt ihn aufsammeln

            player.move()   # Spieler bewegen, zeichen und schießen lassen
            player.draw()
            player.shoot()
            player.level_up()

            pg.display.update() # alles im Grafikspeicher gespeichertes wird auf den Screen geladen
pg.display.quit()               # schließt den Screen und beendet das Programm