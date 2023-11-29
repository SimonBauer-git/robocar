#*******************************************************************************
#
# File Name:   main.py
# Project  :   Einführungsprojekt 2023
#              Programmiervorlesung 4, Staubsauger
#
# Description: Hauptdatei für den Betrieb des Robocars
#
# Ver.     Date         Author                       Comments
# -------  ----------   --------------               ------------------------------
# 1.00     01.06.2023   Bachelorprojekt Robocar      erste Version
# 1.1      23.10.2023   Rudolf Gregor                Programmierbeispiel erstellt
# 1.2      31.10.2023   Rudolf Gregor                Abfrage GP20 eingebaut
# 1.3      12.11.2023   Rudolf Gregor                Zur Vorlage reduziert
#
# Copyright (c) 2023 THI
#****************************************************************************

import random
import basecar

# -----------------------------------------------------------------------------------------------------------
### Define constants
# -----------------------------------------------------------------------------------------------------------

MinAbstandHindernis=10  #Ab zehn Zentimetern Abstand wird ein Objekt als Hindernis eingestuft
MinHelligkeitWeisseFlaeche=500  # Ab diesem gemittelten Helligkeitswert wird Flaeche als weiss angesehen

V_Mittel=60       # Mittlere Geschwindigkeit beider Raeder

Printausgabe=False      # Wenn True, dann werden prints ausgegeben

### Rueckgabewerte fuer Hinderniserkennung
FALSE=0     # Kein Hindernis
GERADE=1    # Hindernis gerade vor dem RoboCar
LINKS=2     # Hindernis links vor dem RoboCar
RECHTS=3    # Hindernis rechts vor dem RoboCar

# ------------------------------------------------------------------------------------------------------------
### Ruecklichter initialisieren
# ------------------------------------------------------------------------------------------------------------
basecar.initBacklights()
# ------------------------------------------------------------------------------------------------------------

# ------------------------------------------------------------------------------------------------------------
### Ultraschallsensor initialisieren
# ------------------------------------------------------------------------------------------------------------
# Sonar
sonarPara = basecar.Sonar()

# ------------------------------------------------------------------------------------------------------------
### Ultraschallsensor auslesen. Rueckgabewert ist die Distanz zu einem Objekt in [cm]
# ------------------------------------------------------------------------------------------------------------
# Sonar
def THI_Auslesen_Ultraschallsensoren(basecar): 
    try:            # Das Auslesen kann auch nicht klappen -> Exception muss geprüft werden
        return basecar.sonar.distance
    except RuntimeError:
        return 1    # Auslesen klappt nicht, falls Distanz zu gering. Also niedrige Distanz zurückgeben
    
# ------------------------------------------------------------------------------------------------------------
### Funktionen zum Auslesen der Liniensensoren
# ------------------------------------------------------------------------------------------------------------

def THI_Auslesen_Liniensensoren(basecar): # Gibt Werte zwischen 0 (schwarz) und 1024 (weiss) zurueck
    Sensor_Links=1024 - basecar.adc2.value * 1024 / 65536
    Sensor_Rechts=1024 - basecar.adc1.value * 1024 / 65536

    if(Printausgabe == True):
        print("Liniensensoren links " , Sensor_Links, " Rechts: ", Sensor_Rechts)
    return Sensor_Links,Sensor_Rechts

# ------------------------------------------------------------------------------------------------------------
### Funktionen zum Ansteuern der Motoren
# ------------------------------------------------------------------------------------------------------------

def THI_MotorSpeed(basecar, V_Links, V_Rechts):  # Geschwindigkeitswerte im Bereich -255 bis +255Wenn der Abstand kleiner ist als 
    # Ansteuern der Motoren
    # Maximalgeschwindigkeit auf 255 begrenzt
    # Motoren duerfen auch rueckwaerts drehen -> RoboCar rotiert auf der Stelle

    if(V_Links > 255):
        V_Links=255
    elif(V_Links<-255):
        V_Links=-255
    if(V_Rechts > 255):
        V_Rechts=255
    elif(V_Rechts<-255):
        V_Rechts=-255

    basecar.motor2.throttle=V_Links / 255       # Basecar erwartet Werte von -1 bis +1
    basecar.motor1.throttle=V_Rechts / 255      # Basecar erwartet Werte von -1 bis +1

    if(Printausgabe == True):
        print("Motorgeschwindigkeiten: links =", V_Links, ", rechts = ", V_Rechts)


# ------------------------------------------------------------------------------------------------------------
### Grundlegende Fahrfunktionen fuer Staubsauger: stehenbleiben, geradeaus, drehen links und rechts
# ------------------------------------------------------------------------------------------------------------

def THI_StopRoboCar(basecar):
    THI_MotorSpeed(basecar, 0, 0)  # Beide Motoren Geschwindigkeit null -> stehen bleiben

def THI_GeradeausFahren(basecar, V_RoboCar):
    THI_MotorSpeed(basecar, V_RoboCar, V_RoboCar)   # Beide Motoren gleiche Geschwindigkeit -> gerade Fahrt

def THI_DrehenRechts(basecar, V_RoboCar):
    THI_MotorSpeed(basecar, V_RoboCar, -V_RoboCar)  # Links vorwaerts, rechts rueckwaerts -> Drehen nach rechts
    
def THI_DrehenLinks(basecar, V_RoboCar):
    THI_MotorSpeed(basecar, -V_RoboCar, V_RoboCar)  # Links rueckwaerts, rechts vorwaerts -> Drehen nach links


# ------------------------------------------------------------------------------------------------------------
### Funktionen zur Detektion eines Hindernisses
### Falls gemessener Abstand kleiner als oben definierte Schwelle, dann gilt ein Hindernis als erkannt
### Oder wenn RoboCar auf schwarze Flaeche faehrt
# ------------------------------------------------------------------------------------------------------------
def THI_HindernisVoraus(basecar):
    
    Abstand=999
    
    Abstand = THI_Auslesen_Ultraschallsensoren(basecar)
    if(Abstand < MinAbstandHindernis):
        return GERADE
    else:
    # Hindernis kann auch sein: RoboCar faehrt ueber schwarze Linie
        Sensor_Links,Sensor_Rechts = THI_Auslesen_Liniensensoren(basecar)

        if ((Sensor_Links + Sensor_Rechts) / 2) < MinHelligkeitWeisseFlaeche:
            if (Sensor_Links < Sensor_Rechts):
                return LINKS
            if (Sensor_Rechts < Sensor_Links):
                return RECHTS        
    return FALSE
        



# ------------------------------------------------------------------------------------------------------------
### Reaktion auf Hindernis: Stehenbleiben, Zuruecksetzen und vom Hindernis wegdrehen
# ------------------------------------------------------------------------------------------------------------
def THI_ZuruecksetzenUndDrehen(basecar, Hindernis):
    print("RoboCar zuruecksetzen und drehen")
    Zufallszahl=0.5+random.random()    # Zufallszahl zwischen 0.5 und 1.5

    THI_GeradeausFahren(basecar, -V_Mittel)  # Rueckwaerts fahren
    basecar.time.sleep(0.6)         # Eine Sekunde warten -> eine Sekunde rueckwarts fahren

    if((Hindernis == LINKS) or (Hindernis == GERADE)):
        if(Printausgabe == True):
            print("Drehen nach rechts fuer ", Zufallszahl, " Sekunden")
        THI_DrehenRechts(basecar, V_Mittel)   # Vom Hindernis wegdrehen
    else:
        THI_DrehenLinks(basecar, V_Mittel)   # Vom Hindernis wegdrehen
       
        if(Printausgabe == True):
            print("Drehen nach rechts fuer ", Zufallszahl, " Sekunden")
    basecar.time.sleep(Zufallszahl)         # Zufallszahl in Sekunden warten
    THI_StopRoboCar(basecar)                # Stehenbleiben
       

# SICHERHEITSFUNKTION
# RoboCar geht erst zur Endlosschleife, wenn Taste GP20 gedrückt wurde
# Damit wollen wir verhindern, dass Ihnen RoboCar auf dem Tisch losfährt und runterfällt
# Warten auf Drücken von GP20 zum Starten
while basecar.btn1.value == True:
    print("Warte auf Button GP20: ", basecar.btn1.value)
    basecar.time.sleep(0.5)  # halbe Sekunde schlafen legen    

# Tonsignal als Rückmeldung, dass Button gedrückt
basecar.simpleio.tone(basecar.board.GP22, 784, duration=0.5)

# Vorbereitung Endlosschleife. Ausgabe Text mit zwei führenden Leerzeilen (\n\n)
print("\n\nTHI Linienfolger fuer RoboCar")


basecar.time.sleep(1)   # Eine Sekunde warten
# Vorbereitung Endlosschleife
print("THI Staubsauger fuer RoboCar")

# ------------------------------------------------------------------------------------------------------------
### Endlosschleife
# ------------------------------------------------------------------------------------------------------------

while True:
    Hindernis=FALSE   # Variable fuer ersten Durchlauf belegen, freie Fahrt
    while(Hindernis == FALSE):   # Kein Hindernis voraus -> freie Fahrt
        
        THI_GeradeausFahren(basecar, V_Mittel)
        Hindernis = THI_HindernisVoraus(basecar)
    if (Hindernis != FALSE):
        THI_ZuruecksetzenUndDrehen(basecar, Hindernis)

    # Schleife beendet -> Hindernis erkannt
    # Zueruecksetzen und vom Hindernis wegdrehen
    # Steuere RoboCar so an, dass er zunächst ein Stück rückwärts fährt
    # und sich dann vom Hindernis wegdreht.
         
    # Schleife fortsetzen und wieder geradeaus fahren
