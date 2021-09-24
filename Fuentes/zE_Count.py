#
#      TORAL MALDONADO ROSA GUADALUPE
#               2153045948

# EXAMEN Algoritmo 2: CONTEO DE NODOS
#               PIF Segall

#         ALGORITMOS DISTRIBUIDOS

'''
  Se trabaja con 5 nodos
  Hace una busqueda primero en amplitud.
  Se cuentan los nodos empezando por las ramas.
  El nodo i manda el mensaje de ida sin valores.
  El conteo de nodos en el nodo i es 0 sin contarse a si mismo..
  Cuando el nodo i ya no tiene nodos por visitar, manda un mensaje
  de regreso al padre aumentando el conteo en 1 para contarse a si mismo.
  El nodo padre de i acumula lo que i le manda en su propio conteo.
  El nodo que inicio el recorrido imprime el numero de nodos en el grafo
  TAREA: contar el numero de nodos en el grafo
'''

import sys
from event import Event
from model import Model
from process import Process
from simulator import Simulator
from simulation import Simulation



class Message():
  '''
    Esta clase sirve para poder hacer los mensajes.
    El mensaje M no lleva valores, por lo que se guarda una cadena vacia
    El mensaje Regresa lleva el numero de nodos
  '''

  def __init__(self, text, n_nodos):
    self.n_nodos = n_nodos
    self.text = text

  def getNNodos(self):
    return self.n_nodos

  def getText(self):
    return self.text


class Count(Model):
  # Hereda de la clase model e implementa de los metodos abstractos "init()" y "receive()"

  def init(self):
    '''
      Inicializacion de las variables del algoritmo.
    '''
    self.father = self.id #el padre. Al proncipio es el mismo
    self.state = False #estado del nodo actual
    self.OK = dict.fromkeys(self.neighbors, False) #banderas de vecinos que saben que ya fui visitado
    self.n_T = 0 #conteo de los nodos que lleva el nodo actual sin contarse a si mismo

    print ("Inicio funciones {}".format(self.id))
    self.printData()

  def printData(self):
    '''
      Metodo auxiliar para imprimir los datos en el tiempo
    '''
    print ("\t Mi padre es: {}".format(self.father))
    print ("\t Mi estado es: {}".format(self.state))
    print ("\t Banderas de mis vecinos: {}".format(self.OK))
    print ("\t Numero de nodos que he contado: {} \n".format(self.n_T))
    #input ("\t Presione enter para continuar:\n ")

  def receive(self, event):
    '''
      Acciones de cada proceso. Se definen todas las acciones y los mnsajes que se mandan.
      Los mensajes que se mandan son del tipo STRING y son:
      M: mensaje que se manda del nodo i a sus vecinos para iniciar el recorrido
      REGRESA: mensaje que se manda al padre junto con el conteo que se hizo
    '''
    if event.getName().getText() == "M":
      print ("[ {} ]: recibi M en t={} del nodo {}".format(self.id, self.clock, event.getSource()))

      if event.getSource() != self.id:
        self.OK[event.getSource()] = True

      if self.state == False:
        self.father = event.getSource()
        self.state = True
        for n in self.neighbors:
          if n != self.father:
            newevent = Event(Message("M", ''), self.clock + 1, n, self.id)
            self.transmit(newevent)

      if False not in self.OK.values() and self.father != self.id:
        print ("\t Mando de regreso a mi padre {} \n".format(event.getSource()))
        newevent = Event(Message("REGRESA", self.n_T + 1), self.clock + 1.0, self.father, self.id)
        self.transmit(newevent)

      self.printData()

    else: #si event.getName().getText() = REGRESA, entonces
      print ("[ {} ]: recibi REGRESA en t={} del nodo {}".format(self.id, self.clock, event.getSource()))
      self.OK[event.getSource()] = True
      self.n_T += event.getName().getNNodos() #se aumenta el numero de nodos

      if False not in self.OK.values():
        if self.father != self.id:
          print ("\t Mando de regreso a mi padre {} \n".format(event.getSource()))
          newevent = Event(Message("REGRESA", self.n_T + 1), self.clock + 1.0, self.father, self.id)
          self.transmit(newevent)
        else:
          #Se imprime el numero de nodos
          print ("\n\t Total de nodos contados: {}\n".format(self.n_T + 1))
          print ("\t Datos finales") #es simple formato

      self.printData()



if __name__ == "__main__":
  if len(sys.argv) != 2:
    print ("Por favor proporcione el nombre de la grafica de comunicaciones")
    raise SystemExit(1)

  #se crea una instancia de la clase Simulation y se le pasa como parametros el archivo
  #con el grafo y el tiempo maximo de ejecucion
  experiment = Simulation(sys.argv[1], 20)

  # asocia un pareja proceso/modelo con cada nodo de la grafica
  for i in range(1,len(experiment.graph)+1):
    m = Count()
    experiment.setModel(m, i)

  #se arranca el evento semilla con un mensaje M del nodo 1 al mismo nodo
  seed = Event(Message("M", ''), 0.0, 1, 1)
  experiment.init(seed)
  experiment.run()

print ("Numero de mensajes: {}".format(experiment.nMessages))
print ("Tiempo transcurrido: {}".format(experiment.nTime))
