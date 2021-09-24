#
#      TORAL MALDONADO ROSA GUADALUPE
#               2153045948

# PRACTICA 2 Algoritmo 2: RECORRIDO DE NODOS
#               DFS Cidon 88

#         ALGORITMOS DISTRIBUIDOS

'''
  Se trabaja con 5 nodos
  Se hace una busqueda primero en profundidad.
  Un nodo avisa a todos sus vecinos que ya fue1 agregado al arbol,
  pero no espera ninguna notificacion de ellos.
  El nodo primero realiza el recorrido y despues  envia el mensaje de visitado,
  entonces el mensaje de descubrimiento que el nodo pueda enviar a los vecinos sera ignorado, pues ellos ya saben del estado del nodo
  TAREA: formar un arbol
'''

import sys
from event import Event
from model import Model
from process import Process
from simulator import Simulator
from simulation import Simulation

#Constantes para definir los estados de los vecinos
V = "visited"
NV = "unvisited"
P = "father"
H = "son"

class Cidon(Model):
  # Hereda de la clase model e implementa de los metodos abstractos "init()" y "receive()"

  def init(self):
    '''
      Inicializacion de las variables del algoritmo.
    '''
    self.state = NV #el estado. Al principio es unvisited
    self.neighbors_state = dict.fromkeys(self.neighbors, NV) #se llena con valores "unvisited" para inicialozar el arreglo

    print ("Inicio funciones {}".format(self.id))
    self.printData()

  def printData(self):
    '''
      Metodo auxiliar para imprimir los datos en el tiempo
    '''
    print ("\t Mi estado es: {} \n".format(self.state))
    print ("\t Mis vecinos son: {} \n".format(self.neighbors_state))
    #input ("\t Presione enter para continuar:\n ")

  def receive(self, event):
    '''
      Acciones de cada proceso. Se definen todas las acciones y los mnsajes que se mandan.
      Los mensajes que se mandan son del tipo STRING y son:
      INICIA: es el evento semilla
      DESCUBRE: el mensaje que se envia para agregar un nodo al recorrido
      VISITADO: mensaje que se envia a los vecinos para avisarles que ya fue visitado
    '''
    if event.getName() == "INICIA":
      print ("[ {} ]: recibi INICIA en t={} del nodo ".format(self.id, self.clock, event.getSource()))
      if self.state == NV:
        self.state = V
        self.explore()

        #se avisa a todos los vecinos que esten visitados o no visitados que ya me han visitado
        for n in self.neighbors_state:
          if self.neighbors_state[n]==V or self.neighbors_state[n]==NV:
            newevent = Event("VISITADO", self.clock + 1.001, n, self.id)
            self.transmit(newevent)
      self.printData()

    elif event.getName() == "DESCUBRE":
      print ("[ {} ]: recibi DESCUBRE en t={} del nodo {}".format(self.id, self.clock, event.getSource()))
      print ("\t Ya me visitaron")

      if self.state == NV:
        self.neighbors_state[event.getSource()] = P
        self.state = V
        self.explore()

        #si no he sido visitado, pongo a quien me envio el descubre como padre, cambio mi estado y aviso a mis vecinos
        for n in self.neighbors_state:
          if self.neighbors_state[n]==V or self.neighbors_state[n]==NV:
            newevent = Event("VISITADO", self.clock + 0.001, n, self.id)
            self.transmit(newevent)
      else:
        #de lo contrario, busco si tengo un hijo que siga explorando o pongo el estado de mi padre como visitado
        if self.neighbors_state[event.getSource()] == NV:
          self.neighbors_state[event.getSource()] = V
        if self.neighbors_state[event.getSource()] == H:
          self.explore()
      self.printData()

    else: #si event.getName() == "VISITADO"
      print ("[ {} ]: recibi VISITADO en t={} del nodo {}".format(self.id, self.clock, event.getSource()))

        #busco si tengo un hijo que siga explorando o pongo el estado de mi padre como visitado
      if self.neighbors_state[event.getSource()] == NV:
        self.neighbors_state[event.getSource()] = V
      if self.neighbors_state[event.getSource()] == H:
        self.neighbors_state[event.getSource()] = V
        self.explore()
      self.printData()

  def explore(self):
    '''
      Metodo encargado de continuar con el recorrido del grafo
    '''

    values = list(self.neighbors_state.values()) #guarda los valores del diccionario
    keys = list(self.neighbors_state.keys()) #guarda las llaves del diccionario

    #si hay un no visitado en el diccionario, es decir, en sus valores, obtiene el index de ese valor para saber que llave le corresponde y asi saber a quien enviar el mensaje. Lo mismo va para buscar un valor que sea padre
    if NV in values:
      i = values.index(NV)
      newevent = Event("DESCUBRE", self.clock + 1.0, keys[i], self.id)
      self.transmit(newevent)
      self.neighbors_state[keys[i]] = H
    elif P in values:
      i = values.index(P)
      newevent = Event("DESCUBRE", self.clock + 1.0, keys[i], self.id)
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
    m = Cidon()
    experiment.setModel(m, i)

  #se siembra el evento semilla para iniciar
  seed = Event("INICIA", -1.0, 1, 1)
  experiment.init(seed)
  experiment.run()

print ("Numero de mensajes: {}".format(experiment.nMessages))
print ("Tiempo transcurrido: {}".format(experiment.nTime))
