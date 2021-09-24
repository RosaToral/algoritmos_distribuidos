#
#      TORAL MALDONADO ROSA GUADALUPE
#               2153045948

# PRACTICA 3 Version 1: RECORRIDO DE UN GRAFO A UNA DISTSNCIA
#               PIF Segall

#         ALGORITMOS DISTRIBUIDOS

'''
  Se trabaja con 5 nodos
  Hace una busqueda primero en amplitud.
  El nodo que inicia y la distancia son aleatorios.
  El algoritmo utiliza rl mismo mensaje pars el recorrido de ida y el de regrso
  El nodo i comienza el recorrido enviando el mensaje M a sus vecinos y decrementando el ttl
  para indicar que ese nivel del arbol ya fue recorrido
  Si el ttl es 0, el nodo i inicia el recorrido de regreso.
  TAREA: recorrer un grafo hasta una cierta distancia (indicada por el ttl)
'''

import sys
from random import randint
from event import Event
from model import Model
from process import Process
from simulator import Simulator
from simulation import Simulation



class Message():
  '''
    Esta clase sirve para representar al mensaje M.
    Se cuentan los niveles que se han visitado.
  '''
  def __init__(self, text, ttl):
    self.text = text #Mensaje M
    self.ttl = ttl #Contador de la distancia a recorrer

  '''
    Metodos para obtener los valores de sus parametros
  '''

  def getText(self):
    return self.text

  def getTtl(self):
    return self.ttl


class PifSegall(Model):
  # Hereda de la clase model e implementa de los metodos abstractos "init()" y "receive()"

  def init(self):
    '''
      Inicializacion de las variables del algoritmo.
    '''
    self.father = self.id #el padre. Al principio es el mismo
    self.state = False #estado del nodo
    self.OK = dict.fromkeys(self.neighbors, False) #banderas de vecinos que saben que ya fui visitado

    print ("Inicio funciones {}".format(self.id))
    self.printData()


  def printData(self):
    '''
      Metodo auxiliar para imprimir los datos en el tiempo
    '''
    print ("\t Mi padre es: {}".format(self.father))
    print ("\t Mi estado es: {}".format(self.state))
    print ("\t Banderas de mis vecinos: {}".format(self.OK))
    #input ("\t Presione enter para continuar:\n ")

  def receive(self, event):
    '''
      Acciones de cada proceso. Se definen todas las acciones y los mnsajes que se mandan.
      Los mensajes que se mandan son objetos de la clsse Message y los textos de Mensajes que se mandan son:
      M: mensaje que recorre el grafo. Decrementa el ttl cuando va de ida.
    '''
    if event.getName().getText() == "M":
      print ("[ {} ]: recibi M en t={} del nodo {}".format(self.id, self.clock, event.getSource()))
      print ("\t ttl: {}".format(event.getName().getTtl()))

      if event.getSource() != self.id: #para evitar un error si el mensaje se manda de un nodo a si mismo
        self.OK[event.getSource()] = True

      if self.state == False:
        self.father = event.getSource()
        self.state = True

        if event.getName().getTtl() > 0:
          #si el ttl es igual a cero, ya se llego a la distancia establecida y ya no debe seguir enviando mensajes M
          for n in self.neighbors:
            if n != self.father:
              newevent = Event(Message("M", event.getName().getTtl()-1), self.clock + 1, n, self.id)
              self.transmit(newevent)
      if event.getName().getTtl()==0 or self.neighbors==[self.father]:
        #si el ttl es cero o si su unico vecino era su padre
        if (False not in self.OK.values() or event.getName().getTtl()==0) and self.father != self.id:
          #si todas las banderas indican que ya fue visitado un nodo,
          #se inicia el recorrido de regreso
          print ("\t Mando de regreso a mi padre {} \n".format(event.getSource()))

          newevent = Event(Message("M", event.getName().getTtl()), self.clock + 1.0, self.father, self.id)
          self.transmit(newevent)

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
    m = PifSegall()
    experiment.setModel(m, i)

  #numeros aleatorios
  n = randint(1,5) #quien inicia
  t = randint(1,2) #a que distancia

  print ("\nEl nodo {} inicia el recorrido".format(n))
  print ("a una distancia de {} nodos a su alrededor".format(t))
  input ("Presione enter para continuar:\n ")

  #se inicia el evento semilla enviando un mensaje M al mismo nodo
  seed = Event(Message("M", t), 0.0, n, n)
  experiment.init(seed)
  experiment.run()

print ("Numero de mensajes: {}".format(experiment.nMessages))
print ("Tiempo transcurrido: {}".format(experiment.nTime))
