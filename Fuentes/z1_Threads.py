#
#   TORAL MALDONADO ROSA GUADALUPE
#             2153045948

# PRACTICA 1 PARTE 1: VENTA DE TICKES
#       modelo cliente-servidor

#       ALGORITMOS DISTRIBUIDOS

'''
  Se trabaja con 7 nodos
  Los nodos 2 a 7 son los clientes y el nodo 1 es el servidor
  Cuando un nodo requiera ver el mapa, envia una solicitud al servidor
  Si el mapa esta libre, el nodo 1 permite que el nodo solicitante vea el mapa
  Si el mapa esta siendo ocupado, encola el id
  Solo un nodo por instante puede ver el mapa
  Los nodos se encolan en orden segun vayan pidiendo el mapa
  ZONA CRITICA: el mapa
'''

import sys
from time import sleep
from random import randint, uniform
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
      El proceso 1 es el servidor, por lo que es el que inicializa
      la cola y el estado del mapa.
    '''
    self.sucesor = self.neighbors[0] #el sucesor de cada nodo es el primero de sus vecinos
    if self.id == 1:
      self.cola = list() #cola donde se formaran los nodos que esten esperando
      self.estado = "LIBRE" #estado del mapa. Inicialmente no hay solicitudes

    print ("Inicio funciones {}".format(self.id))
    print ("Mis vecinos son: {}".format(self.neighbors))
    print ("Mi sucesor es: {} \n".format(self.sucesor))

  def receive(self, event):
    '''
      Acciones de cada proceso. Se definen todas las acciones y los mnsajes que se mandan.
      Los mensajes que se mandan son del tipo STRING y son:
      SOLICITUD: el nodo servidor recibe una solicitud para ver el mapa
                de un nodo cliente.
                Se puso un sleep entre 1 y 3 para simular que tarda en enviarlo
      OK: el servidor avisa al cliente que puede ver el mapa.
        Se puso un sleep de 1 a 5 para simular que el cliente esta escogiendo su lugar.
      LIBERA: cuando el cliente termina de ver el mapa, avisa al servidor
            que ya lo libero
    '''
    if event.getName() == "SOLICITUD":
      print ("[ {} ]: recibi SOLICITUD en t={} del nodo ".format(self.id, self.clock, event.getSource()))
      if self.estado == "LIBRE":
        #Si el mapa esta libre, se le manda al nodo que lo pidio
        print ("\t Enviando mapa a {}... \n".format(event.getSource()))
        sleep(uniform(1,2.5))
        #se manda OK al nodo que mando la solicitud
        newevent = Event("OK", self.clock + 1.0, event.getSource(), self.id)
        self.transmit(newevent)
        self.estado = "OCUPADO"
      else:
        #Si el mapa no esto disponible, se encola al nodo para que espere
        self.cola.append(event.getSource())
        print ("\t Espere nodo {} el mapa esta ocupado".format(event.getSource()))

    elif event.getName() == "OK":
      global mapa
      print ("[ {} ]: recibi OK en t={}".format(self.id, self.clock))
      print ("\t Estoy viendo el mapa ...")

      #el cliente elige un lugar y si esta ocupado, elige otro
      f=randint(0, 4)
      c=randint(0, 4)
      while mapa[f][c]==1:
        f=randint(0, 4)
        c=randint(0, 4)
      mapa[f][c]=1
      sleep(randint(1,5))

      #el cliente libera el mapa
      newevent = Event("LIBERA", self.clock + 1.0, self.sucesor, self.id) #se le manda al servidor
      print ("\t ya termine \n")
      self.transmit(newevent)

    else: #si event.getName() = LIBERA, entonces
      print ("[ {} ]: recibi LIBERA en t={}".format(self.id, self.clock))
      if len(self.cola)==0:
        #si no hay clientes esperando, se pone estado libre
        print ("\n")
        self.estado="LIBRE"
      else:
        #si hay clientes esperando, se le avisa al cliente del frente de la cola que puede ver el mpa
        print ("\t Nodo {} el mapa esta libre, puede revisarlo[\n".format(self.cola[0]))
        newevent = Event("OK", self.clock + 1.0, self.cola[0], self.id)
        del self.cola[0] #se saca al cliente del frente
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

  #tiempos aleatorios. Se escojen en un rango menor al tiempo maximo
  #para evitar que un nodo pida el mapa en los tiempos ultimos tiempos
  #ya que puede suceder que la simulacion se detenga antes de enviar
  #el mapa o de liberarlo
  r1=randint(0, 15)
  r2=randint(0, 15)

  #nodos aleatorios. El nodo 1 es el servidor, por lo que no se toma en cuenta
  n1=0
  n2=0
  while n2==n1:
    n1=randint(2, 7)
    n2=randint(2, 7)

  #se hacen dos solicitudes para arrancar el simulador
  seed1 = Event("SOLICITUD", r1, 1, n1) #solicitudes de dos nodos en diferentes tiempos
  seed2 = Event("SOLICITUD", r2, 1, n2)
  experiment.init(seed1)
  experiment.init(seed2)
  experiment.run()

  print("{} Lugares ocupados".format(experiment.nMessages))
  for fila in mapa:
    print(fila)
