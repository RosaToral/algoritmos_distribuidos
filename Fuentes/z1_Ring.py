#
#   TORAL MALDONADO ROSA GUADALUPE
#             2153045948

# PRACTICA 1 PARTE 2: VENTA DE TICKES
#          grafo de anillo

#       ALGORITMOS DISTRIBUIDOS

'''
  Se trabaja con 7 nodos
  Todos los nodos tienen una aplicacion ue es en donde les llega el mapa y lo ven
  Todos los nodos tienen una variable que les permite decir si necesitan o no el mapa
  Hay una variable token que circula en el grafo
  Cuando un nodo requiera ver el mapa, envia una solicitud a traves de la aplicacion
    al algoritmo (servidor local)
  Si el nodo tiene el token, lo retiene mientras ve el mapa
  Si el nodo no tiene el token, debe esperar a que le llegue
  Solo un nodo por instante puede ver el mapa
  ZONA CRITICA: el mapa
'''

import sys
from time import sleep
from random import randint
from event import Event
from model import Model
from process import Process
from simulator import Simulator
from simulation import Simulation

#matriz que simboliza los lugares en el mapa
mapa = [[0,0,0,0,0],
        [0,0,0,0,0],
        [0,0,0,0,0],
        [0,0,0,0,0],
        [0,0,0,0,0]]

class ticketsSale(Model):
  # Hereda de la clase model e implementa de los metodos abstractos "init()" y "receive()"
  def init(self):
    '''
      Inicializacion de las variables del algoritmo y de cada proceso
      Cada proceso contiene el algoritmo, por lo que todos inicializan
      la variable solicitud_sc para indicar que han pedido el mapa.
    '''
    self.sucesor = self.neighbors[0] #el sucesor de cada nodo es el primero de sus vecinos
    #Variable que indica si alguien pidio el mapa
    self.solicitud_sc = False
    print ("Inicio funciones {}".format(self.id))
    print ("Mis vecinos son: {}".format(self.neighbors))
    print ("Mi sucesor es: {} \n".format(self.sucesor))

  def receive(self, event):
    '''
      Acciones de cada proceso. Se definen todas las acciones y los mensajes que se mandan.
      Los mensajes que se mandan son del tipo STRING y son:
      INIT: se inicializa el token en el nodo 1 y este lo manda al nodo 2
      SOLICITUD: cada nodo hace una solicitud al algoritmo dentro de si mismo
                cuando requieran ver el mapa. Se manda el mensaje a si mismo
      OK: el algoritmo le dice al nodo si puede o utilizar el mapa. Tambien es un
        mensaje del nodo al mismo nodo.
        Se puso un sleep de 1 a 5 para simular que el nodo esta escogiendo su lugar.
      LIBERA: cuando el nodo termina de ver el mapa, avisa al algoritmo
      TOKEN: es el token que va circulando alrededor del grafo.
    '''
    if event.getName() == "INIT":
      print ("[ {} ]: recibi INIT en t={}".format(self.id, self.clock))
      print("\t  Creo el token y se lo paso a", self.sucesor, "\n")
      newevent = Event("TOKEN", self.clock + 1.0, self.sucesor, self.id)
      self.transmit(newevent)

    elif event.getName() == "SOLICITUD":
      print ("[ {} ]: hago una SOLICITUD en t={} para ver el mapa".format(self.id, self.clock))
      print ("[ {} ]: recibi una SOLICITUD en t={} \n".format(self.id, self.clock))
      #se pone a True la variable solicitud_sc para indicar que hay una solicitud
      self.solicitud_sc=True

    elif  event.getName() == "OK":
      global mapa
      print ("[ {} ]: recibi OK en t={}".format(self.id, self.clock))
      print("\t Estoy viendo el mapa ...")

      #el cliente elige un lugar y si esta ocupado, entonces elige otro
      f=randint(0, 4)
      c=randint(0, 4)
      while mapa[f][c]==1:
        f=randint(0, 4)
        c=randint(0, 4)
      mapa[f][c]=1
      sleep(randint(2, 5))

      #el cliente desocupa el mapa y libera el token
      print("\t libero el token \n")
      newevent = Event("LIBERA", self.clock + 1.0, self.id, self.id)
      self.transmit(newevent)

    elif event.getName() == "LIBERA":
      print ("[ {} ]: recibi LIBERA en t={}".format(self.id, self.clock))
      #se pone a False la solicitud del nodo que manda el evento
      self.solicitud_sc=False
      print("\t Token liberado. Se manda a {} \n".format(self.sucesor))
      newevent = Event("TOKEN", self.clock + 1.0, self.sucesor, self.id)
      self.transmit(newevent)

    else: #si event.getName() = TOKEN
      print ("[ {} ]: recibi TOKEN en t={}".format(self.id, self.clock))
      if not self.solicitud_sc:
        #si el nodo con el token no quiere ver el mapa, rota el token
        print("\t No quiero ver el mapa. Paso el Token a{} \n".format(self.sucesor))
        newevent = Event("TOKEN", self.clock + 1.0, self.sucesor, self.id)
        self.transmit(newevent)
      else:
        #si quiere ver el mapa, se manda un ok a la aplicacion del nodo.
        print("\t Quiero ver el mapa \n")
        newevent = Event("OK", self.clock + 1.0, self.id, self.id) #se le manda al servidor
        self.transmit(newevent)


if __name__ == "__main__":
  if len(sys.argv) != 2:
    print ("Por favor proporcione el nombre de la grafica de comunicaciones")
    raise SystemExit(1)

  #se crea una instancia de la clase Simulation y se le pasa como parametros el archivo
  #con el grafo y el tiempo maximo de ejecucion
  experiment = Simulation(sys.argv[1], 20)

  # asocia un pareja proceso/modelo con cada nodo de la grafica
  for i in range(1,len(experiment.graph)+1):
    m = ticketsSale()
    experiment.setModel(m, i)

  #tiempos aleatorios. Empiezan en 1 ya que el primer evento, INIT, empieza en el tiempo 0
  #Se escojen en un rango menor al tiempo maximo para evitar que un nodo pida el mapa en 
  #los ultimos tiempos ya que puede suceder que la simulacion se detenga antes de enviar
  #el mapa o de liberarlo
  r1=randint(1, 15)
  r2=randint(1, 15)

  #nodos aleatorios
  n1=0
  n2=0
  while n2==n1:
    n1=randint(1, 7)
    n2=randint(1, 7)

  # inserta 3 eventos el evento semilla de arranque, INIT, y dos solicitudes
  seed1 = Event("INIT", 0.0, 1, 1)
  seed2 = Event("SOLICITUD", r1, n1, n1) #Se lanzan dos solicitudes en diferentes tiempos
  seed3 = Event("SOLICITUD", r2, n2, n2)
  experiment.init(seed1)
  experiment.init(seed2)
  experiment.init(seed3)
  experiment.run()

  print("{} Lugares ocupados".format(experiment.nTime))
  for fila in mapa:
    print(fila)
