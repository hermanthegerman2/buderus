# -*# -*- coding: iso8859-1 -*-
## -----------------------------------------------------
## Logik-Generator  V1.5
## -----------------------------------------------------
## Copyright � 2012, knx-user-forum e.V, All rights reserved.
##
## This program is free software; you can redistribute it and/or modify it under the terms
## of the GNU General Public License as published by the Free Software Foundation; either
## version 3 of the License, or (at your option) any later version.
##
## This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
## without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
## See the GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License along with this program;
## if not, see <http://www.gnu.de/documents/gpl-3.0.de.html>.

### USAGE:  python.exe LogikGenerator.py [--debug --en1=34 --en2="TEST"]



import sys
import codecs
import os
import base64 
import marshal
import re
try:
    from hashlib import md5
except ImportError:
    import md5 as md5old
    md5 = lambda x='': md5old.md5(x)
import inspect
import time
import socket
import tempfile
import zlib
import zipfile

##############
### Config ###
##############

## Name der Logik
LOGIKNAME="Buderus"
## Logik ID
LOGIKID="12264"

## Ordner im GLE
LOGIKCAT="www.knx-user-forum.de"


## Beschreibung
LOGIKDESC="""

"""
VERSION="V0.2"


## Bedingung wann die kompilierte Zeile ausgef�hrt werden soll
BEDINGUNG="EI"
## Formel die in den Zeitspeicher geschrieben werden soll
ZEITFORMEL=""
## Nummer des zu verwenden Zeitspeichers
ZEITSPEICHER="0"

## AUF True setzen um Bin�ren Code zu erstellen
doByteCode=False
#doByteCode=True

## Base64Code �ber SN[x] cachen
doCache=False

## Doku erstellen Ja/Nein
doDoku=True

debug=False
livedebug=False

showList=False
#############################
########## Logik ############
#############################
LOGIK = '''# -*- coding: iso8859-1 -*-
## -----------------------------------------------------
## '''+ LOGIKNAME +'''   ### '''+VERSION+'''
##
## erstellt am: '''+time.strftime("%Y-%m-%d %H:%M")+'''
## -----------------------------------------------------
## Copyright � '''+ time.strftime("%Y") + ''', knx-user-forum e.V, All rights reserved.
##
## This program is free software; you can redistribute it and/or modify it under the terms
## of the GNU General Public License as published by the Free Software Foundation; either
## version 3 of the License, or (at your option) any later version.
##
## This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
## without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
## See the GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License along with this program;
## if not, see <http://www.gnu.de/documents/gpl-3.0.de.html>.

## -- ''' +re.sub("\n","\n## -- ",LOGIKDESC)+ ''' 

#5000|"Text"|Remanent(1/0)|Anz.Eing�nge|.n.|Anzahl Ausg�nge|.n.|.n.
#5001|Anzahl Eing�nge|Ausg�nge|Offset|Speicher|Berechnung bei Start
#5002|Index Eingang|Default Wert|0=numerisch 1=alphanummerisch
#5003|Speicher|Initwert|Remanent
#5004|ausgang|Initwert|runden bin�r (0/1)|typ (1-send/2-sbc)|0=numerisch 1=alphanummerisch
#5012|abbruch bei bed. (0/1)|bedingung|formel|zeit|pin-ausgang|pin-offset|pin-speicher|pin-neg.ausgang

5000|"'''+LOGIKCAT+'''\\'''+LOGIKNAME+'''_'''+VERSION+'''"|0|3|"E1 IP:Port"|"E2 Typ"|"E3 senden"|2|"A1 Daten"|"A2 SystemLog"

5001|3|2|0|1|1

# EN[x]
5002|1|"192.168.178.10:22"|1 #* IP:Port
5002|2|1|0 #* Typ
5002|3|""|1 #* Senden

# Speicher
5003|1||0 #* logic

# Ausg�nge
5004|1|""|0|1|0 #* Daten
5004|2|""|0|1|1 #* SystemLog

#################################################
'''
#####################
#### Python Code ####
#####################
code=[]

code.append([3,"EI",r"""
if EI == 1:
  global socket
  import socket
  class buderus_connect(object):
      def __init__(self,localvars):
          from hs_queue import Queue
          from hs_queue import hs_threading as threading
          self.id = "buderus_connect"
          self.logik = localvars["pItem"]
          self.MC = self.logik.MC
          EN = localvars['EN']
          self.device_connector = EN[1]
          self.device_type = EN[2]
          self._thread = None

          ## Achtung:
          ## Die Anzahl der Bytes je Datentyp bezieht sich auf den Stand 01/2009. Bei fr�heren Regelger�teversionen 
          ## kann die Anzahl niedriger sein. 
          
          ## Funktionstyp / Name / Datenl�nge in Bytes
          
          self.monitor_data_type = {
              0x80 : ("Heizkreis 1", 18),
              0x81 : ("Heizkreis 2", 18),
              0x82 : ("Heizkreis 3", 18),
              0x83 : ("Heizkreis 4", 18),
              0x84 : ("Warmwasser", 12),
              0x85 : ("Strategie wandh�ngend", 12),
              0x87 : ("Fehlerprotokoll", 42),
              0x88 : ("bodenstehender Kessel", 42),
              0x89 : ("Konfiguration", 24),
              0x8A : ("Heizkreis 5", 18),
              0x8B : ("Heizkreis 6", 18),
              0x8C : ("Heizkreis 7", 18),
              0x8D : ("Heizkreis 8", 18),
              0x8E : ("Heizkreis 9", 18),
              0x8F : ("Strategie bodenstehend", 30),
              0x90 : ("LAP", 18),
              0x92 : ("wandh�ngende Kessel 1", 60),
              0x93 : ("wandh�ngende Kessel 2", 60),
              0x94 : ("wandh�ngende Kessel 3", 60),
              0x95 : ("wandh�ngende Kessel 4", 60),
              0x96 : ("wandh�ngende Kessel 5", 60),
              0x97 : ("wandh�ngende Kessel 6", 60),
              0x98 : ("wandh�ngende Kessel 7", 60),
              0x99 : ("wandh�ngende Kessel 8", 60),
              0x9B : ("W�rmemenge", 36),
              0x9C : ("St�rmeldemodul", 6),
              0x9D : ("Unterstation", 6),
              0x9E : ("Solarfunktion", 54),
          }
          self._hs_message_queue = Queue()

          self.hs_queue_thread = threading.Thread(target=self._send_to_hs_consumer,name='buderus_hs_consumer')
          self.hs_queue_thread.start()

          self.connect()

      def debug(self,msg):
          #self.log(msg,severity='debug')
          print "DEBUG: %r" % (msg,)

      def connect(self):
          from hs_queue import hs_threading as threading
          self._thread = threading.Thread(target=self._connect,name='Buderus-Moxa-Connect')
          self._thread.start()

      def _send_to_hs_consumer(self):
          while True:
              (out,msg) = self._hs_message_queue.get()
              ## Auf iKO's schreiben
              for iko in self.logik.Ausgang[out][1]:
                  try:
                      ## Logik Lock im HS sperren
                      self.MC.LogikList.calcLock.acquire()
                      
                      ## Wert im iKO beschreiben
                      iko.setWert(out,msg)
                      
                      ## Logik Lock im HS freigeben
                      self.MC.LogikList.calcLock.release()
                      
                      iko.checkLogik(out)
                  except:
                      self.MC.Debug.setErr(sys.exc_info(),"%r" % msg)

      def send_to_output(self,out,msg):
          ## werte fangen bei 0 an also AN[1] == Ausgang[0]#
          out -= 1
          self._hs_message_queue.put((out,msg))

      def log(self,msg,severity='info'):
          import time
          try:
              from hashlib import md5
          except ImportError:
              import md5 as md5old
              md5 = lambda x,md5old=md5old: md5old.md5(x)
          
          _msg_uid = md5( "%s%s" % ( self.id, time.time() ) ).hexdigest()
          _msg = '<log><id>%s</id><facility>buderus</facility><severity>%s</severity><message>%s</message></log>' % (_msg_uid,severity,msg)
          
          self.send_to_output( 2, _msg )

      def incomming(self,msg):
          self.debug("incomming message %r" % msg)

      def to_hex(self,list_of_dec):
          try:
              if not type(list_of_dec) == list:
                  list_of_dec = [list_of_dec]
              return " ".join( ["%.2x".upper() % x for x in list_of_dec] )
          except:
              return list_of_dec

              
              

## Bei dem Kommunikationsmodul wird zwischen einem "Normal-Modus" und einem "Direkt-Modus"
## unterschieden. 
## "Normal-Modus" Bei diesem Modus werden laufend alle sich �ndernden Monitorwerte 
## sowie Fehlermeldungen �bertragen. 
## "Direkt-Modus" Bei diesem Modus kann der aktuelle Stand aller bisher vom Regelger�t 
## generierten Monitordaten en Block abgefragt und ausgelesen werden. 
## Mittels des Kommandos 0xDD kann von "Normal-Modus" in den "Direkt-Modus" umgeschaltet werden. 
## In diesem Modus kann auf alle am ECOCAN-BUS angeschlossenen Ger�te zugegriffen und es k�nnen 
## ger�teweise die Monitorwerte ausgelesen werden. 
## Der "Direkt-Modus" kann durch das Kommando 0xDC wieder verlassen werden. 
## Au�erdem wird vom "Direkt-Modus" automatisch in den "Normal-Modus" zur�ckgeschaltet, wenn f�r die 
## Zeit von 60 sec kein Protokoll des "Direkt-Modus" mehr gesendet wird. 
              
      def _connect(self):
          import time,socket,sys
          MODE_NORMAL = 0xDE
          MODE_DIRECT = 0xDD

          self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
          _ip,_port = self.device_connector.split(":")
          self.sock.connect( ( _ip, int(_port) ) )
          try:
              print "DEBUG: Try"
 ##             ## setze nomal mode
 ##             while True:
 ##                 print "DEBUG: Setze set_mode"                  
 ##                 if self.set_mode(MODE_NORMAL):
 ##                     self.debug("Normal Mode gesetzt")
 ##                     self.debug("Packet %r" % ( self.to_hex(MODE_NORMAL) ) )
 ##                     self.debug("Normal Mode gesetzt")
 ##                     break
 ##                 time.sleep(2)
              
              
              while True:
                  print "DEBUG: _3964r_Send: Also im Sende Mode"
                  Send_Data = [ 0xA2 , 0x01 , 0x23, 0x24, 0x53, 0x66 ]
                  if self._3964r_Send(Send_Data) == 0:
                      print "DEBUG: Daten sind erfolgreich gesendet"
                      self.debug("Send_Data %r" % ( self.to_hex(Send_Data) ) )
                      break
                  time.sleep(2)
              
              while True:
                  print "DEBUG: _3964r_Receive: Also in Empfangs Mode"
                  Receive_Data = []
                  if self._3964r_Receive(Receive_Data) == 0:   
                     print "DEBUG: Daten sind erfolgreich empfangen"
                     
                     ## packet an Ausgang 1
                     ### self.send_to_output( 1, Receive_Data )
                     
                     self.debug("Reveice_Data %r" % ( self.to_hex(Receive_Data) ) )
              
          except:
              self.MC.Debug.setErr(sys.exc_info(),"")
              time.sleep(10)
              self.connect()

###########################################################################################################
#####                                      Die 3964R Prozedure !                                      #####
###########################################################################################################                   
              
## Warum diese Prozedure ?
## Diese Prozedure dient dazu Kollisionen zu verhindern und St�rungen zu erkennen.
## -> Kollisionen werden dadurch verhindert, dass nur dann gesendet werden kann, wenn die Gegenstelle (hier 
## also das Buderus RS232 Gateway) eingewilligt hat (mit DLE geantwortet hat).
## -> St�rungen: Durch das Mitsenden eine Pr�fsumme (BCC) mit dem Datenstrom kann von der Gegenstelle 
## nachgepr�ft werden, ob es zu einer St�rung gekommen ist.
## Dies nur als Motivation.
              
## Die Steuerzeichen f�r die Prozedur 3964R sind der Norm DIN 66003 f�r den 7-Bit-Code entnommen. Sie
## werden allerdings mit der Zeichenl�nge 8 Bit �bertragen (Bit I7 = 0). Am Ende jedes Datenblocks wird zur
## Datensicherung ein Pr�fzeichen(BCC) gesendet.
              
## STX = 0x02     ## bedeutet soviel wie "ich m�chte senden, darf ich ?"
## DLE = 0x10     ## bedeutet soviel wie "ich best�tige, du darfst senden!"
## ETX = 0x03     ## die beiden Zeichen "DLE ETX" zeigen an, das das Ende der Daten erreicht ist. 
## NAK = 0x15     ## NAK steht f�r "Not Acknoledge" also soviel wie "Kein Best�tigung" Irgend was 
##                ## hat nicht geklappt.


## Das Blockpr�fzeichen BCC wird durch eine exklusiv-oder-Verkn�pfung �ber alle Datenbytes der
## Nutzinformation, inclusive der Endekennung DLE, ETX gebildet.

## Es gibt noch eine Besonderheit: Befindet sich in Transport Daten selbst ein DLE Zeichen, wird es beim 
## Senden gedoppelt. Es wird also ein zweites eingef�gt und beim BCC ber�cksichtigt das auch. Somit ist 
## sichergestellt, dass es nur Paare von "DLE DLE" oder "DLE ETX" geben kann und das "DLE ETX" einzig am 
## Ende auftauche kann.
## Damit dadurch die Daten aber nicht ver�ndert werden, ist das zweite DLE auf der Empfangs Seite wieder
## zu entfernen. Da es aber beim BCC mit gez�hlt wurde, ist es hierbei aber mit zu Ber�cksichtigen. 




## Empfangen mit der Prozedur 3964R
## --------------------------------------------------------------------------------------------------
##
## Beispiel f�r einen fehlerlosen Datenverkehr: bei Empfang
## Prozedur 3964R                        Peripherieger�t
##                                <--                 STX
##      DLE                    -->
##                                <--          1. Zeichen der zu �bertragenden Daten
##                                <--
##                                <--
##                                <--          n. Zeichen der zu �bertragenden Daten
##                                <--               DLE
##                                <--               ETX
##                                <--               BCC
##      DLE                    -->
##
## Im Ruhezustand, wenn kein Sendeauftrag und kein Warteauftrag des Interpreters zu bearbeiten ist, wartet
## die Prozedur auf den Verbindungsaufbau durch das Peripherieger�t. Empf�ngt die Prozedur ein STX und
## steht ihr ein leerer Eingabepuffer zur Verf�gung, wird mit DLE geantwortet.
## Nachfolgende Empfangszeichen werden nun in dem Eingabepuffer abgelegt. Werden zwei aufeinander
## folgende Zeichen DLE empfangen, wird nur ein DLE in den Eingabepuffer �bernommen.
## Nach jedem Empfangszeichen wird w�hrend der Zeichenverzugszeit (ZVZ) auf das n�chste Zeichen
## gewartet. Verstreicht die Zeichenverzugszeit ohne Empfang, wird das Zeichen NAK an das
## Peripherieger�t gesendet und der Fehler an den Interpreter gemeldet.
## Mit erkennen der Zeichenfolge DLE, ETX und BCC beendet die Prozedur den Empfang und sendet DLE
## f�r einen fehlerfrei (oder NAK f�r einen fehlerhaft) empfangenen Block an das Peripherieger�t.
## Treten w�hrend des Empfangs �bertragungsfehler auf (verlorenes Zeichen, Rahmenfehler), wird der
## Empfang bis zum Verbindungsabbau weitergef�hrt und NAK an das Peripherieger�t gesendet. Dann wird
## eine Wiederholung des Blocks erwartet. Kann der Block auch nach insgesamt sechs Versuchen nicht
## fehlerfrei empfangen werden, oder wird die Wiederholung vom Peripherieger�t nicht innerhalb der
## Blockwartezeit von 4 sec gestartet, bricht die Prozedur 3964R den Empfang ab und meldet den Fehler an
## den Interpreter.

              
      def _3964r_Receive(self, list_of_bytes):
          
          STX = 0x02
          DLE = 0x10
          ETX = 0x03
          NAK = 0x15
          
          import select
          
          ZVZ = 0.200   ## Zeichenverzugszeit  220 ms
          BWZ = 5       ## Blockwartezeit 5 sec
          
          _3964r_ErrCode = 0    ## Fehlercode loeschen
      
          while True:
             _r,_w,_e = select.select([self.sock],[],[],BWZ)
             if self.sock in _r:
                data = ord( self.sock.recv(1) )
                if data == STX:
                   self.debug("STX <--- empfangen")
                   ## jetzt ist DLE zur�cksenden damit die Daten losgeschickt werden
                   self.sock.send( chr(DLE))
                   self.debug("---> DLE gesendet")
                   break
                else:
                   self.debug(" !! KEINE STX: wird ignoriert!! ")
                   ## Zeiche ignorieren und weitere Zeichen lesen
                   continue
             else:
                ## kein STX innerhalb der Blockwartezeit empfangen
                _3964r_ErrCode = 8
                return _3964r_ErrCode
            
          ## Nun die DATEN empfangen !
          
          
          for _loop in xrange(6):
             ## nun sind 6 Versuche erlaubt, die Daten zu empfangen
             
             bcc = 0
             DLE_merker = 0
             Ende = 0
             
             while not (Ende):
                _r,_w,_e = select.select([self.sock],[],[],ZVZ)
                if self.sock in _r:
                   data = ord( self.sock.recv(1) )
                   if (data == DLE) and ( not DLE_merker):
                      self.debug("erstes DLE in DATA gefunden")
                      DLE_merker = 1
                      bcc ^= data     ## faellt weg bei "DLE nicht in BCC"
                   elif (data == ETX) and (DLE_merker):
                      ## direkt nach einem DLE ist nun das ETX empfange worden, also das Ende ist erreicht
                      ## bcc ist aber nur vom DLE berechnet, noch nicht vom ETX
                      ## w�re das zweite Zeichen nach dem DLE wieder ein DLE, w�rde es in den n�chsten ELSE Zweig
                      ## gehen und gespeichert werden. Das erste DLE ist damit wieder entfernt, aber bei BCC 
                      ## mitgez�hlt worden, was nach 3964R richtig ist. BCC wird �ber alle Zeichen gemacht.
                      Ende = 1
                   else:
                      ## Zeichen in list_of_bytes speichern
                      list_of_bytes.append(data)
                      bcc ^= data
                      DLE_merker = 0    ## merker zur�cksetzen
                      self.debug("Data %r" % ( self.to_hex(data) ) )
                      ## und weitere Zeichen lesen
                      continue
                else:
                   ## NAK rauschicken
                   self.sock.send( chr(NAK) )
                   _3964r_ErrCode = 9
                   return _3964r_ErrCode
             
             bcc ^= ETX     ## das DLE ist ja schon in bcc, das ETX hiermit nun auch
            
             ## nun BCC lesen       
             _r,_w,_e = select.select([self.sock],[],[],ZVZ)
             if self.sock in _r:
                data = ord( self.sock.recv(1) )
                if data == bcc:
                   ## erfolgreicher Empfang von BCC
                   self.debug("Received BBC -> OK")
                   ## Best�tigung schicken
                   self.sock.send( chr(DLE) )
                   return 0 ## Kein Fehler
                else:    
                   ## enpfangenes BCC stimmt nicht
                   self.debug("Falsches BBC -> NAK")
                   ## NAK rauschicken
                   self.sock.send( chr(NAK) )
             else:
                ## keine BCC innerhalb von ZVZ empfangen
                self.debug("kein BBC -> NAK")
                ## NAK rausschicken    
                self.sock.send( chr(NAK) )
                return 5 ## Fehler zurueckgeben
          else:
             _3964r_ErrCode = 10
          
          return _3964r_ErrCode
 
 ## ENDE _3964r_Receive
 
 
## Senden mit der Prozedur 3964R
## --------------------------------------------------------------------------------------------------
## 
## Der Signalflu� ist hier genauso wie beim Empfang (siehe oben), nur das die Richtung anderum ist.
##
## Zum Aufbau der Verbindung sendet die Prozedur 3964R das Steuerzeichen STX aus. Antwortet das
## Peripherieger�t vor Ablauf der Quittungsverzugzeit (QVZ) von 2 sec mit dem Zeichen DLE, so geht die
## Prozedur in den Sendebetrieb �ber. Antwortet das Peripherieger�t mit NAK, einem beliebigen anderen
## Zeichen (au�er DLE) oder die Quittungsverzugszeit verstreicht ohne Reaktion, so ist der
## Verbindungsaufbau gescheitert. Nach insgesamt drei vergeblichen Versuchen bricht die Prozedur das
## Verfahren ab und meldet dem Interpreter den Fehler im Verbindungsaufbau.
## Gelingt der Verbindungsaufbau, so werden nun die im aktuellen Ausgabepuffer enthaltenen
## Nutzinformationszeichen mit der gew�hlten �bertragungsgeschwindigkeit an das Peripherieger�t
## gesendet. Das Peripherieger�t soll die ankommenden Zeichen in Ihrem zeitlichen Abstand �berwachen.
## Der Abstand zwischen zwei Zeichen darf nicht mehr als die Zeichenverzugszeit (ZVZ) von 220 ms
## betragen.
## Jedes im Puffer vorgefundene Zeichen DLE wird als zwei Zeichen DLE gesendet. Dabei wird das Zeichen
## DLE zweimal in die Pr�fsumme �bernommen.
## Nach erfolgtem senden des Pufferinhalts f�gt die Prozedur die Zeichen DLE, ETX und BCC als
## Endekennung an und wartet auf ein Quittungszeichen. Sendet das Peripherieger�t innerhalb der
## Quittungsverzugszeit QVZ das Zeichen DLE, so wurde der Datenblock fehlerfrei �bernommen. Antwortet
## das Peripherieger�t mit NAK, einem beliebigen anderen Zeichen (au�er DLE), einem gest�rten Zeichen
## oder die Quittungsverzugszeit verstreicht ohne Reaktion, so wiederholt die Prozedur das Senden des
## Datenblocks. Nach insgesamt sechs vergeblichen Versuchen, den Datenblock zu senden, bricht die
## Prozedur das Verfahren ab und meldet dem Interpreter den Fehler im Verbindungsaufbau.
## Sendet das Peripherieger�t w�hrend einer laufenden Sendung das Zeichen NAK, so beendet die
## Prozedur den Block und wiederholt in der oben beschriebenen Weise.
 
      def _3964r_Send(self, list_of_bytes):
          
          STX = 0x02
          DLE = 0x10
          ETX = 0x03
          NAK = 0x15
          
          import select
          
          QVZ = 0.200      

          _3964r_ErrCode = 0    ## Fehlercode loeschen
          packet = []
          checksum = 0
          self.debug("_3964r_Send")
          for _loop in xrange(3):
             self.sock.send( chr(STX) )
             self.debug("STX gesendet")
             _r,_w,_e = select.select([self.sock],[],[],QVZ)
             if self.sock in _r:
                  data = ord( self.sock.recv(1) )
                  if data == DLE:
                      ## jetzt ist FREI zum Senden
                      self.debug("Received DLE")
                      break
             else:
                ## timeout n�chster Versuch machen (von den 3 erlaubten Versuchen)
                continue
          else:
             self.debug("Nach 3 mal STX senden innerhalb von QVZ kein DLE empfangen")
             _3964r_ErrCode = 1
             return _3964r_ErrCode
        
          ## nun senden der Daten
          self.debug("Daten senden")
          ## nun sind 6 Versuche erlaubt
          for _loop in xrange(6):
             ## BCC wird schon inklusive DLE und ETX auf 0x13 initialisiert
             bcc = 0x13   
             for _byte in list_of_bytes:
                self.sock.send( chr(_byte))
                self.debug("Send Data %r" % ( self.to_hex(_byte) ) )
                bcc ^= _byte
                ## Wenn das DLE Zeichen in DATA vorkommt ist es nach 3964R zweimal zu senden
                if _byte == DLE:
                   self.sock.send( chr(DLE))
                   self.debug("Send Data ++ %r" % ( self.to_hex(DLE) ) )
                   bcc ^= DLE
                 
             ## nun sind alle Daten raus
             ## jetzt den ABSCHLUSS anzeigen mit DLE, ETX und zum Nachpr�fen f�r die Gegenseite BCC
             self.sock.send( chr(DLE))
             self.debug("Send Abschluss DLE %r" % ( self.to_hex(DLE) ) )
             ## KEIN BCC, weil schon in Initialisierung geschehen
             self.sock.send( chr(ETX))
             self.debug("Send Abschluss ETX %r" % ( self.to_hex(ETX) ) )
             ## KEIN BCC, weil schon in Initialisierung geschehen
             self.sock.send( chr(bcc))
             self.debug("Send Abschluss BCC %r" % ( self.to_hex(bcc) ) )
             
             ## Nun ist alles draussen
             ## jetzt mu� noch die Empfangsbestaetigung DLE zur�ckkommen
             
             _r,_w,_e = select.select([self.sock],[],[],QVZ)
             if self.sock in _r:
                  data = ord( self.sock.recv(1) )
                  if data == DLE:
                      ## jetzt ist der Empfang best�tigt
                      self.debug("Empfang bestaetigt mit DLE")
                      break
             else:
                ## timeout n�chster Versuch machen (von den 6 erlaubten Versuchen)
                continue
          else:
             self.debug("Nach 6 mal Daten senden, kein DLE innerhalb von QVZ empfangen")
             _3964r_ErrCode = 2
             return _3964r_ErrCode
        
          ## Senden: habe fertig
          self.debug("Daten senden fertig")
          ## _3964r_ErrCode zur�ckgeben (sollt hier 0 sein
          return _3964r_ErrCode

## ENDE _3964r_Send

          

 


      def direct_read_request(self):
          ## Mit dem Kommando "0xA2 <ECOCAN-BUS-Adresse>" k�nnen die Monitordaten des ausgew�hlten 
          ## ECOCAN-BUS-Ger�tes von der Kommunikationskarte ausgelesen werden. 
          pass
      
      def direct_read_answer(self):
          ## Die Kommunikationskarte antwortet mit : 
          ## 0xAB <ECOCAN-BUS-Adresse> <TYP> <OFFSET> <6 Daten-Byte> 
          ## 0xAB = Kennung f�r Monitordaten 
          ## ECOCAN-BUS-Adresse = die abgefragte Adresse zur Best�tigung 
          ## TYP = Typ der gesendeten Monitordaten

          ## Daten unter dem entsprechenden Typ werden nur gesendet wenn auch die entsprechende Funktionalit�t 
          ## im Regelger�t eingebaut ist. 
          ## OFFSET = Offset zur Einsortierung der Daten eines Typ�s

          ## Als Endekennung f�r das abgefragte Regelger�t oder falls keine Daten vorhanden sind, wird der 
          ## nachfolgende String 
          ## 0xAC <ECOCAN-BUS-Adresse> gesendet          

          ## Die Abfrage der gesamten Monitordaten braucht nur zu Beginn oder nach einem Reset zu erfolgen. 
          ## Nach erfolgter Abfrage der Monitordaten sollte wieder mit dem Kommando 0xDC in den "Normal-Modus" 
          ## zur�ckgeschaltet werden. 

          pass


      def normal_read(self):
          ## Im "Normal-Modus" werden die Monitordaten nach folgendem Muster �bertragen: 
          ## 0xA7 <ECOCAN-BUS-Adresse> <TYP> <OFFSET> <DATUM> 
          ## 0xA7 = Kennung f�r einzelne Monitordaten 
          ## ECOCAN-BUS-Adresse = Herkunft�s Adresse des Monitordatum�s (hier Regelger�teadresse) 
          ## TYP = Typ der empfangenen Monitordaten       
          ## OFFSET = Offset zur Einsortierung der Daten eines Typ�s 
          ## DATUM = eigentlicher Messwert 
          pass
          




"""])

debugcode = """

"""
postlogik=[0,"",r"""

5012|0|"EI"|"buderus_connect(locals())"|""|0|0|1|0
5012|0|"EC[3]"|"SN[1].incomming(EN[3])"|""|0|0|0|0

"""]

####################################################################################################################################################

###################################################
############## Interne Funktionen #################
###################################################

LGVersion="1.5"

livehost=""
liveport=0
doSend=False
noexec=False
nosource=False
doZip=False
for option in sys.argv:
    if option.find("--new")==0:
        try:
            LOGIKID=int(option.split("=")[1].split(":")[0])
            LOGIKNAME=option.split("=")[1].split(":")[1]
            try: 
                LOGIKCAT=option.split("=")[1].split(":")[2]
            except:
                pass
        except:
            print "--new=id:name[:cat]"
            raise
            sys.exit(1)

        if LOGIKID >99999 or LOGIKID == 0:
            print "invalid Logik-ID"
            sys.exit(1)

        if LOGIKID <10000:
            LOGIKID+=10000
        LOGIKID="%05d" % LOGIKID
        f=open(inspect.currentframe().f_code.co_filename,'r')
        data=""
        while True: 
            line = f.readline()
            if line.find("LOGIKID=") == 0:
                line = "LOGIKID=\""+LOGIKID+"\"\n"
            if line.find("LOGIKNAME=") == 0:
                line = "LOGIKNAME=\""+LOGIKNAME+"\"\n"
            if line.find("LOGIKCAT=") == 0:
                line = "LOGIKCAT=\""+LOGIKCAT+"\"\n"
            data += line
            if not line: 
                break 
        f.close()
        open(str(LOGIKID)+"_"+LOGIKNAME+".py",'w').write(data)
        sys.exit(0)

    if option=="--list":
        showList=True
      
    if option=="--debug":
        debug=True

    if option=="--noexec":
        noexec=True

    if option=="--nosource":
        nosource=True    

    if option=="--zip":
        doZip=True

    if option=="--nocache":
        doCache=False
      
    if option.find("--live")==0:
        livedebug=True
        debug=True
        doByteCode=False
        doCache=True
        try:
            livehost=option.split("=")[1].split(":")[0]
            liveport=int(option.split("=")[1].split(":")[1])
        except:
            print "--live=host:port"

    if option.find("--send")==0:
        doSend=True
        try:
            livehost=option.split("=")[1].split(":")[0]
            liveport=int(option.split("=")[1].split(":")[1])
        except:
            print "--send=host:port"
          

print "HOST: "+livehost+" Port:" +str(liveport)
### DEBUG ####
EI=True
EA=[]
EC=[]
EN=[]
SA=[]
SC=[]
SN=[]
AA=[]
AC=[]
AN=[]
OC=[]
ON=[]
if debug or doSend:
    EA.append(0)
    EC.append(False)
    EN.append(0)
    AA.append(0)
    AC.append(False)
    AN.append(0)
    SA.append(0)
    SC.append(False)
    SN.append(0)
    ON.append(0)
    OC.append(False)

    ## Initialisieren ##
    for logikLine in LOGIK.split("\n"):
        if logikLine.find("5001") == 0:
            for i in (range(0,int(logikLine.split("|")[3]))):
              ON.append(0)
              OC.append(False)
        if logikLine.find("5002") == 0:
            EN.append(logikLine.split("|")[2].replace('\x22',''))
            EA.append(logikLine.split("|")[2])
            EC.append(False)
        if logikLine.find("5003") == 0:
            if logikLine.split("|")[3][0] == "1":
                SN.append(re.sub('"','',logikLine.split("|")[2]))
            else:
                try:
                    SN.append(int(logikLine.split("|")[2]))
                except:
                    pass
                    SN.append(logikLine.split("|")[2])
            SA.append(logikLine.split("|")[2])
            SC.append(False)
        if logikLine.find("5004") == 0:
            AN.append(logikLine.split("|")[2])
            AA.append(logikLine.split("|")[2])
            AC.append(False)


def bool2Name(b):
  if int(b)==1:
    return "Ja"
  else:
    return "Nein"
def sbc2Name(b):
  if int(b)==1:
    return "Send"
  else:
    return "Send By Change"


def addInputDoku(num,init,desc):
  return '<tr><td class="log_e1">Eingang '+str(num)+'</td><td class="log_e2">'+str(init)+'</td><td class="log_e3">'+str(desc)+'</td></tr>\n'
def addOutputDoku(num,sbc,init,desc):
  return '<tr><td class="log_a1">Ausgang '+str(num)+' ('+sbc2Name(sbc)+')</td><td class="log_a2">'+str(init)+'</td><td class="log_a3">'+str(desc)+'</td></tr>\n'

LOGIKINHTM=""
LOGIKOUTHTM=""

i=0
LEXPDEFINELINE=LHSDEFINELINE=LINDEFINELINE=LSPDEFINELINE=LOUTDEFINELINE=0
for logikLine in LOGIK.split("\n"):
    if logikLine.find("5000") == 0:
        LEXPDEFINELINE=i
        LOGIKREMANT=bool2Name(logikLine.split("|")[2])
        LOGIKDEF=logikLine
    if logikLine.find("5001") == 0:
        LHSDEFINELINE=i
        ANZIN=int(logikLine.split("|")[1])
        ANZOUT=int(logikLine.split("|")[2])
        ANZSP=int(logikLine.split("|")[4])
        CALCSTARTBOOL=logikLine.split("|")[5]
        CALCSTART=bool2Name(CALCSTARTBOOL)
    if logikLine.find("5002") == 0:
        LINDEFINELINE=i
        desc=re.sub('"','',LOGIKDEF.split("|")[3+int(logikLine.split("|")[1])])
        if logikLine.find("#*") >0:
            desc=logikLine.split("#*")[1]
        LOGIKINHTM+=addInputDoku(logikLine.split("|")[1],logikLine.split("|")[2],desc)
    if logikLine.find("5003") == 0 or logikLine.find("# Speicher") == 0:
        LSPDEFINELINE=i
    if logikLine.find("5004") == 0:
        LOUTDEFINELINE=i
        desc=re.sub('"','',LOGIKDEF.split("|")[(4+ANZIN+int(logikLine.split("|")[1]))])
        if logikLine.find("#*") >0:
            desc=logikLine.split("#*")[1]
        LOGIKOUTHTM+=addOutputDoku(logikLine.split("|")[1],logikLine.split("|")[4],logikLine.split("|")[2],desc)
    i=i+1


if livedebug:
    EC.append(0)
    EN.append("")


sendVars=""

for option in sys.argv:
    if option.find("--sa") == 0:
        SA[int(option[4:option.find("=")])]=option.split("=")[1]
        sendVars+="SA["+str(int(option[4:option.find("=")]))+"]="+option.split("=")[1]+"\n"
    if option.find("--sn") == 0:
        SN[int(option[4:option.find("=")])]=option.split("=")[1]
        SC[int(option[4:option.find("=")])]=True
        sendVars+="SN["+str(int(option[4:option.find("=")]))+"]="+option.split("=")[1]+"\n"
        sendVars+="SC["+str(int(option[4:option.find("=")]))+"]=1\n"
    if option.find("--aa") == 0:
        AA[int(option[4:option.find("=")])]=option.split("=")[1]
        sendVars+="AA["+str(int(option[4:option.find("=")]))+"]="+option.split("=")[1]+"\n"
    if option.find("--an") == 0:
        AN[int(option[4:option.find("=")])]=option.split("=")[1]
        AC[int(option[4:option.find("=")])]=True
        sendVars+="AN["+str(int(option[4:option.find("=")]))+"]="+option.split("=")[1:]+"\n"
        sendVars+="AC["+str(int(option[4:option.find("=")]))+"]=1\n"
    if option.find("--ea") == 0:
        EA[int(option[4:option.find("=")])]=option.split("=")[1]
        sendVars+="EA["+str(int(option[4:option.find("=")]))+"]="+option.split("=")[1:]+"\n"
    if option.find("--en") == 0:
        EN[int(option[4:option.find("=")])]="".join(option.split("=",1)[1])
        EC[int(option[4:option.find("=")])]=True
        sendVars+="EN["+str(int(option[4:option.find("=")]))+"]="+"".join(option.split("=")[1:])+"\n"
        sendVars+="EC["+str(int(option[4:option.find("=")]))+"]=1\n"
    if option.find("--ec") == 0:
#        EC[int(option[4:option.find("=")])]=int(option.split("=")[1])
        sendVars+="EC["+str(int(option[4:option.find("=")]))+"]="+option.split("=")[1]+"\n"
        print sendVars
    if option.find("--sc") == 0:
#        EC[int(option[4:option.find("=")])]=int(option.split("=")[1])
        sendVars+="SC["+str(int(option[4:option.find("=")]))+"]="+option.split("=")[1]+"\n"
        print sendVars
    if option.find("--on") == 0:
        ON[int(option[4:option.find("=")])]=option.split("=")[1]
        sendVars+="ON["+str(int(option[4:option.find("=")]))+"]="+option.split("=")[1]+"\n"
    if option.find("--oc") == 0:
        OC[int(option[4:option.find("=")])]=True
        sendVars+="OC["+str(int(option[4:option.find("=")]))+"]=1\n"
    if option.find("--ei") == 0:
        EI=(int(option.split("=")[1])==1)
        sendVars+="EI=1\n"
    if option.find("--run") == 0:
        sendVars+="eval(SN["+str(ANZSP+1)+"])\n"


def symbolize(LOGIK,code):
      symbols = {}
      for i in re.findall(r"(?m)^500([234])[|]([0-9]{1,}).*[@][@](.*)\s", LOGIK):
          varName=((i[0]=='2') and 'E') or ((i[0]=='3') and 'S') or ((i[0]=='4') and 'A')
          isunique=True
          try:
              type(symbols[i[2]])
              sym=i[2]
              isunique=False
          except KeyError:
              pass
          ## �berpr�ft auch die alternativen Varianten
          if re.match("[ACN]",i[2][-1:]):
              try:
                  type(symbols[i[2][:-1]])
                  sym=i[2][:-1]
                  isunique=False
              except KeyError:
                  pass
          if isunique:
              symbols[i[2]]=[varName,"["+i[1]+"]"]
          else:
              print "Variablen Kollision :" +repr(i[2])+" ist in " +repr(symbols[sym]) + " und  "+ varName +"["+i[1]+"] vergeben"
              sys.exit(1)

      ## Symbole wieder entfernen
      LOGIK=re.sub("[@][@]\w+", "",LOGIK)

      #im Code tauschen
      for i in symbols.keys():
          code=[code[0],re.sub("[\@][\@]"+i+"([ACN])",symbols[i][0]+"\\1"+symbols[i][1],code[1]),re.sub("[\@][\@]"+i+"([ACN])",symbols[i][0]+"\\1"+symbols[i][1],code[2])]
          code=[code[0],re.sub("[\@][\@]"+i+"",symbols[i][0]+"N"+symbols[i][1],code[1]),re.sub("[\@][\@]"+i+"",symbols[i][0]+"N"+symbols[i][1],code[2])]
      return LOGIK,code

NCODE=[]
commentcode=[]
for codepart in code:
    NLOGIK,codepart=symbolize(LOGIK,codepart)

    NCODE.append(codepart)

    if codepart[0]==0 or codepart[0]==3:
        commentcode.append("##########################\n###### Quelltext: ########\n##########################"+"\n##".join(codepart[2].split("\n"))+"\n")
    #else:
    #    commentcode.append("#"+codepart[2].split("\n")[1]+"\n################################\n## Quelltext nicht �ffentlich ##\n################################")


NLOGIK,postlogik = symbolize(LOGIK,postlogik)
LOGIK=NLOGIK

code=NCODE

## Doku
doku = """
<html>
<head><title></title></head>
<link rel="stylesheet" href="style.css" type="text/css">
<body><div class="titel">"""+LOGIKNAME+"""</div>
<div class="nav"><A HREF="index.html">Hilfe</A> / <A HREF="logic.html">Logik</A> / """+LOGIKNAME+""" / <A HREF="#anker1">Eing&auml;nge</A> / <A HREF="#anker2">Ausg&auml;nge</A></div><div class="field0">Funktion</div>
<div class="field1">"""+re.sub("\r\n|\n","<br>",LOGIKDESC.decode("iso-8859-1").encode("ascii","xmlcharrefreplace") )+"""</div>
<div class="field0">Eing&#228;nge</div>
<a name="anker1" /><table border="1" width="612" class="log_e" cellpadding="0" cellspacing="0">
<COL WIDTH=203><COL WIDTH=132><COL WIDTH=275>
<tr><td>Eingang</td><td>Init</td><td>Beschreibung</td></tr>
"""+LOGIKINHTM.decode("iso-8859-1").encode("ascii","xmlcharrefreplace") +"""
</table>
<div class="field0">Ausg&#228;nge</div>
<a name="anker2" /><table border="1" width="612" class="log_a" cellpadding="0" cellspacing="0">
<COL WIDTH=203><COL WIDTH=132><COL WIDTH=275>
<tr><td>Ausgang</td><td>Init</td><td>Beschreibung</td></tr>
"""+LOGIKOUTHTM.decode("iso-8859-1").encode("ascii","xmlcharrefreplace") +"""
</table>
<div class="field0">Sonstiges</div>
<div class="field1">Neuberechnung beim Start: """+CALCSTART+"""<br />Baustein ist remanent: """+LOGIKREMANT+"""<br />Interne Bezeichnung: """+LOGIKID+"""<br />Der Baustein wird im "Experten" in der Kategorie '"""+LOGIKCAT+"""' einsortiert.<br /></div>
</body></html>

"""

if doDoku:
  open("log"+LOGIKID+".html",'w').write(doku)


LIVECODE="""
if EN["""+str(ANZIN+1)+"""].find("<id"""+LOGIKID+""">")!=-1:
    print "LivePort " +str(len(EN["""+str(ANZIN+1)+"""]))+ " Bytes erhalten"
    try:
        __LiveDebugCode_="".join(__import__('re').findall("(?i)<id"""+LOGIKID+""">(.*)</id"""+LOGIKID+""">",EN["""+str(ANZIN+1)+"""]))
        print "LiveDebug-Daten ID:"""+LOGIKID+" Name:"+LOGIKNAME+""" "
    except:
        pass
        print "Fehler Datenlesen"
        __LiveDebugCode_=''
    if __LiveDebugCode_.find("<inject>") != -1:
        SN["""+str(ANZSP+2)+"""]+="".join(__import__('re').findall("(?i)<inject>([A-Za-z0-9\\x2B\\x3D\\x2F]+?)</inject>", __LiveDebugCode_))
        print "Daten erhalten Buffer: " + str(len(SN["""+str(ANZSP+2)+"""]))
    elif  __LiveDebugCode_.find("<compile />") != -1:
        print "Compile"
        try:
            __LiveBase64Code_=__import__('base64').decodestring(SN["""+str(ANZSP+2)+"""])
            print __LiveBase64Code_
        except:
            pass
            print "Base64 Error"
            raise
        try:
            SN["""+str(ANZSP+1)+"""]=compile(__LiveBase64Code_,'<LiveDebug_"""+LOGIKID+""">','exec')
            SC["""+str(ANZSP+1)+"""]=1
            print "Running"
        except:
            pass
            SN["""+str(ANZSP+1)+"""]="0"
            SC["""+str(ANZSP+1)+"""]=1
            print "Compile Error"

        SN["""+str(ANZSP+2)+"""]=''
    elif __LiveDebugCode_.find("<vars>") == 0:
        print "Run Script"
        try:
            __LiveBase64Code_=__import__('base64').decodestring("".join(__import__('re').findall("(?i)<vars>([A-Za-z0-9\\x2B\\x3D\\x2F]+?)</vars>", __LiveDebugCode_)))
        except:
            pass
            print "Script Base64 Error"
            __LiveBase64Code_='0'
        try:
            eval(compile(__LiveBase64Code_,'<LiveDebugVars"""+LOGIKID+""">','exec'))
        except:
            print "Script Error" 
            print __LiveBase64Code_
            print  __import__('traceback').print_exception(__import__('sys').exc_info()[0],__import__('sys').exc_info()[1],__import__('sys').exc_info()[2])
            raise
    else:
        print "unbekanntes TAG: " + repr(__LiveDebugCode_)
"""




#print LIVECODE

LOGIKFILE=LOGIKID+"_"+LOGIKNAME

## Debug Lines
NCODE=[]
if debug or livedebug:
    for codepart in code:
        codepart[2]=re.sub("###DEBUG###","",codepart[2])
        NCODE.append(codepart)
    code=NCODE

#print "\n".join(code)
def commentRemover(code):
    ## Komentar Remover 
    ## thanks to gaston
    codelist=code[2].split("\n")
    removelist=[]
    lencode=len(codelist)-1
    for i in range(1,lencode):
        codeline=codelist[lencode-i].lstrip(" \t")
        if len(codeline)>0:
            if codeline[0]=='#':
                removelist.insert(0,"REMOVED: ("+str(lencode-i)+") "+codelist.pop(lencode-i))
        else:
            codelist.pop(lencode-i)
    return ([code[0],code[1],"\n".join(codelist)],"\n".join(removelist))

Nremoved=""
NCode=[]
for codepart in code:
    codepart, removed=commentRemover(codepart)
    Nremoved=Nremoved+removed
    NCode.append(codepart)

code=NCode

#print Nremoved
#print "\n\n"


#print code

if livedebug:
    NCODE="\n##### VERSION #### %04d-%02d-%02d %02d:%02d:%02d ###\n" % time.localtime()[:6]
    code.append(NCODE)

CODELENGTH=len(repr(code))



breakStart=str((int(CALCSTARTBOOL)-1)*-1)
LOGIKARRAY=LOGIK.split("\n")
lformel=""
def compileMe(code,doByteCode,BEDINGUNG=''):
    if doByteCode:
        data=compile(code,"<"+LOGIKFILE+">","exec")
        data=marshal.dumps(data)
        version = sys.version[:3]
        formel = ""
        if doByteCode==2:
            formel += "5012|0|\""+BEDINGUNG+"\"|\"eval(__import__('marshal').loads(__import__('zlib').decompress(__import__('base64').decodestring('"+re.sub("\n","",base64.encodestring(zlib.compress(data,6)))+"'))))\"|\""+ZEITFORMEL+"\"|0|"+ZEITSPEICHER+"|0|0"
        else:
            formel += "5012|0|\""+BEDINGUNG+"\"|\"eval(__import__('marshal').loads(__import__('base64').decodestring('"+re.sub("\n","",base64.encodestring(data))+"')))\"|\""+ZEITFORMEL+"\"|0|"+ZEITSPEICHER+"|0|0"
        formel+="\n"

    else:
        if doCache:
            LOGIKDEFARRAY=LOGIKARRAY[LHSDEFINELINE].split("|")
            if livedebug:
                LOGIKDEFARRAY[4]=str(ANZSP+2)
            else:
                LOGIKDEFARRAY[4]=str(ANZSP+1)
            LOGIKARRAY[LHSDEFINELINE]="|".join(LOGIKDEFARRAY)
            LOGIKARRAY[LSPDEFINELINE]+="\n"+"5003|"+str(ANZSP+1)+"|\"0\"|0 # Base64 Code-Cache"
            if livedebug:
                LOGIKARRAY[LSPDEFINELINE]+="\n"+"5003|"+str(ANZSP+2)+"|\"\"|0 # LivePortBase64Buffer"
            if livedebug:
                formel = "5012|0|\"EI or EC["+str(ANZIN+1)+"]\"|\"eval(compile(__import__('base64').decodestring('"+re.sub("\n","",base64.encodestring(LIVECODE))+"'),'<"+LOGIKFILE+">','exec'))\"|\"\"|0|0|0|0\n"
                #formel += "5012|0|\"("+BEDINGUNG+") or SC["+str(ANZSP+1)+"]\"|\"eval(SN["+str(ANZSP+1)+"])\"|\""+ZEITFORMEL+"\"|0|"+ZEITSPEICHER+"|0|0"
                formel += "5012|0|\"\"|\"eval(SN["+str(ANZSP+1)+"])\"|\""+ZEITFORMEL+"\"|0|"+ZEITSPEICHER+"|0|0"
            else:
                formel = "5012|0|\"EI\"|\"compile(__import__('base64').decodestring('"+re.sub("\n","",base64.encodestring(code))+"'),'<"+LOGIKFILE+">','exec')\"|\"\"|0|0|"+str(ANZSP+1)+"|0\n"
                formel += "5012|0|\""+BEDINGUNG+"\"|\"eval(SN["+str(ANZSP+1)+"])\"|\""+ZEITFORMEL+"\"|0|"+ZEITSPEICHER+"|0|0"
        else:
            formel = "5012|0|\""+BEDINGUNG+"\"|\"eval(compile(__import__('base64').decodestring('"+re.sub("\n","",base64.encodestring(code))+"'),'<"+LOGIKFILE+">','exec'))\"|\""+ZEITFORMEL+"\"|0|"+ZEITSPEICHER+"|0|0"
    #formel+="\n## MD5 der Formelzeile: "+md5.new(formel).hexdigest()
    return formel

formel=""
for i in range(len(code)):
    codepart=code[i]
    if codepart[0]==1:
        tempBC=1
    if codepart[0]==2:
        tempBC=2
    else:
        tempBC=doByteCode
    if livedebug:
        doCache=True
        formel=compileMe(LIVECODE,False,BEDINGUNG="")
        break
    formel+=compileMe(codepart[2],tempBC,BEDINGUNG=codepart[1])
    #formel+=commentcode[i]+"\n\n"
        
### DEBUG ###

formel+="\n"+postlogik[2]

## Debuggerbaustein

if livedebug:
    LOGIKDEFARRAY=LOGIKARRAY[LEXPDEFINELINE].split("|")
    LOGIKDEFARRAY[3]=str(ANZIN+1)
    LOGIKDEFARRAY[3+ANZIN]+="|\"E"+str(ANZIN+1)+" DEBUG\""
    LOGIKARRAY[LEXPDEFINELINE]="|".join(LOGIKDEFARRAY)
    LOGIKDEFARRAY=LOGIKARRAY[LHSDEFINELINE].split("|")
    LOGIKDEFARRAY[1]=str(ANZIN+1)
    LOGIKARRAY[LHSDEFINELINE]="|".join(LOGIKDEFARRAY)
    LOGIKARRAY[LINDEFINELINE]+="\n"+"5002|"+str(ANZIN+1)+"|\"\"|1 # Debugger Live in"


LOGIK = "\n".join(LOGIKARRAY)

allcode=""
for i in code:
  allcode+=i[2]+"\n"

if showList:
    codeobj=allcode.split("\n")
    for i in range(0,len(codeobj)):
        print str(i)+": "+codeobj[i]

if debug and not livedebug:
    debugstart=time.clock()
    allcode += debugcode
    if not noexec:
        exec(allcode)
    else:
        compile(allcode,"<code>","exec")

    debugtime=time.clock()-debugstart
    print "Logikausfuehrzeit: %.4f ms" % (debugtime)
    if debugtime>1:
      print """
###############################################
### !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! ###
### !!!ACHTUNG: sehr lange Ausf�rungszeit!! ###
### !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! ###
###############################################
"""

if debug or doSend:
    del EN[0]
    del SN[0]
    del AN[0]

if livedebug:
    #formel=lformel
    LOGIK="""############################\n####  DEBUG BAUSTEIN #######\n############################\n"""+LOGIK
    livesend=re.sub("\n","",base64.encodestring(allcode))
    sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    sock.connect((livehost,liveport))
    Livepackets=0
    while livesend!="":
        Livepackets+=1
        sock.sendall("<xml><id"+LOGIKID+"><inject>"+livesend[:4000]+"</inject></id"+LOGIKID+"></xml>")
        livesend=livesend[4000:]
        time.sleep(0.1)
    time.sleep(1)
    sock.sendall("<xml><id"+LOGIKID+"><compile /></id"+LOGIKID+"></xml>")
    print str(Livepackets)+ " Packet per UDP verschickt"
    sock.close()

if doSend:
    ## Das ausl�sen �ber den Debug verhindern
    sendVars="EC["+str(ANZIN+1)+"]=0\n"+sendVars
    sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    sock.connect((livehost,liveport))
    sock.sendall("<xml><id"+LOGIKID+"><vars>"+re.sub("\n","",base64.encodestring(sendVars)+"</vars></id"+LOGIKID+"></xml>\n"))
    sock.close()


if VERSION !="":
    VERSION="_"+VERSION
if debug:
    VERSION+="_DEBUG"


open(LOGIKFILE+VERSION+".hsl",'w').write(LOGIK+"\n"+formel+"\n")
def md5sum(fn):
    m = md5()
    f=open(fn,'rb')
    while True: 
        data = f.read(1024) 
        if not data: 
            break 
        m.update(data) 
    f.close()
    return m.hexdigest() + " *" + fn + "\n"
    
#chksums = md5sum(LOGIKFILE+VERSION+".hsl")
#if not nosource:
#    chksums += md5sum(inspect.currentframe().f_code.co_filename)
#if doDoku:
#    chksums += md5sum("log"+LOGIKID+".html")
#
#open(LOGIKFILE+".md5",'w').write(chksums)

if doZip:
    #os.remove(LOGIKFILE+VERSION+".zip")
    z=zipfile.ZipFile(LOGIKFILE+VERSION+".zip" ,"w",zipfile.ZIP_DEFLATED)
    if not nosource:
        z.write(inspect.currentframe().f_code.co_filename)
    if doDoku:
        z.write("log"+LOGIKID+".html")
    z.write(LOGIKFILE+VERSION+".hsl")
#    z.write(LOGIKFILE+".md5")
    z.close()

print "Baustein \"" + LOGIKFILE + "\" erstellt"
print "Groesse:" +str(CODELENGTH)

if livedebug:
    print "########################################"
    print "####       DEBUGBAUSTEIN            ####"
    print "########################################"

print """
Neuberechnung beim Start: """+CALCSTART+"""
Baustein ist remanent: """+LOGIKREMANT+"""
Interne Bezeichnung: """+LOGIKID+"""
Kategorie: '"""+LOGIKCAT+"""'
Anzahl Eing�nge: """+str(ANZIN)+"""   """+repr(EN)+"""
Anzahl Ausg�nge: """+str(ANZOUT)+"""  """+repr(AN)+"""
Interne Speicher: """+str(ANZSP)+"""  """+repr(SN)+"""
"""

#print chksums
