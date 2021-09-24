#
#      TORAL MALDONADO ROSA GUADALUPE
#               2153045948

# PRACTICA 3 Version 3: BUSQUEDA DE CONTENIDO EN UNA RED
#               PIF Segall

#         ALGORITMOS DISTRIBUIDOS

'''
  Se trabaja con 5 nodos
  Hace una busqueda primero en amplitud.
  El nodo que inicia, lo que busca y la distancia son aleatorios.
  Cada nodo tiene una lista con el contenido que tiene.
  Hay 10 contenidos representados con numeros del 1 al 10
  El nodo i quiere buscar un contenido, asi que manda un mensaje
  a sus vecinos para encontrarlo junto con una lista para saber cuales nodos lo tienen
  y junto con un contandor que indica la distancia hasta donde buscar en la red.
  Se hace un recorrido de ida decrementanto el contador para saher cuando llegue a la distancia destinada
  Cuando el nodo i termino su recorrido o ya no tiene vecinos, manda un regresa a su padre junto con 
  la lista con los nodos que tienen el contenido buscado, incluyendose a el mismo si tambien lo tiene.
  La lista de nodos se va llenando en el recorrido de regreso.
  Los nodos padres guardan las listas de sus hijos en el arreglo OK para no perder los valores.
  El arreglo OK tiene uno de 3 valores para fads nodo: False, si es no visitado, True si ya se visito, o el arreglo de nodos si su hijo termino la busqueda y lo regreso al padre.
  El nodo que inicio la busqueda imprime la lista de nodos
  Tanto el mensaje de ida como el mensaje de regreso llevan el contenido a buscar y la lista de nodos.
  TAREA: regresar una lista con los nodos que tienen el contenido buscado
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
    Esta clase sirve para representar el mensaje de ida (M) y el de regreso
    M sirve oara enviar la lista hasta el fin de la distancia dada por el contador y que alli comience la busqueda
  '''
  def __init__(self, text, ttl, value, nodes):
    self.text = text #Mensaje M o Regresa
    self.ttl = ttl #Contador de la distancia a recorrer
    self.value = value #El contenido que desea buscarse
    self.nodes = nodes #Lista de nodos

  '''
    Metodos para obtener los valores de sus parametros
  '''

  def getText(self):
    return self.text

  def getTtl(self):
    return self.ttl

  def getValue(self):
    return self.value

  def getNodes(self):
    return self.nodes


class PifSegall(Model):
  # Hereda de la clase model e implementa de los metodos abstractos "init()" y "receive()"

  def init(self):
    '''
      Inicializacion de las variables del algoritmo.
    '''
    self.father = self.id #el padre. Al principio es el mismo
    self.state = False #estado del nodo
    self.OK = dict.fromkeys(self.neighbors, False) #banderas de vecinos que saben que ya fui visitado
    self.content = self.genContent() #lista de contenidos que posee el nodo

    print ("Inicio funciones {}".format(self.id))
    self.printData()

  def genContent(self):
    '''
      Metodo auxiliar para llenar el contenido de cada nodo con numeros alestorios del 1 al 10 no repetidos
    '''
    size = randint(1, 10)
    l = list()

    for i in range(size):
      r = randint(1, 10)
      if r in l:
        i-=1
      else:
        l.append(r)

    return l

  def makeList(self, event):
    '''
      Funcion auxiliar que ayuda a crear la lista con el id del nodo actual
    '''
    if event.getName().getValue() in self.content:
      #si el nodo tiene el  contenido, se agrega su id a un arreglo que se envia al padre
      print ("\t Yo tengo el contenido {}".format(event.getName().getValue()))
      c = [self.id]
    else:
      c = list()

    return c

  def printData(self):
    '''
      Metodo auxiliar para imprimir los datos en el tiempo
    '''
    print ("\t Mi padre es: {}".format(self.father))
    print ("\t Mi estado es: {}".format(self.state))
    print ("\t Banderas de mis vecinos: {}".format(self.OK))
    print ("\t Mi contenido es: {} \n".format(self.content))
    #input ("\t Presione enter para continuar:\n ")

  def receive(self, event):
    '''
      Acciones de cada proceso. Se definen todas las acciones y los mnsajes que se mandan.
      Los mensajes que se mandan son objetos de la clsse Message y los textos de Mensajes que se mandan son:
      M: mensaje que recorre el grafo enviando la lista de nodos, el contenido a buscar y decrementando el ttl para la distancia
      REGRESA: mensaje de regreso que envia al padre la lista de nodos que tienen el cotenido a buscar
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
              newevent = Event(Message("M", event.getName().getTtl()-1, event.getName().getValue(), []), self.clock + 1, n, self.id)
              self.transmit(newevent)

      if event.getName().getTtl()==0 or self.neighbors==[self.father]:
        #si el ttl es cero o si su unico vecino era su padre
        if (False not in self.OK.values() or event.getName().getTtl()==0) and self.father != self.id:
          #si todas las banderas indican que ya fue visitado un nodo,
          #se inicia el recorrido de regreso
          print ("\t Mando de regreso a mi padre {} \n".format(event.getSource()))

          c = self.makeList(event)

          newevent = Event(Message("REGRESA", event.getName().getTtl(),event.getName().getValue(), c), self.clock + 1.0, self.father, self.id)
          self.transmit(newevent)

      self.printData()

    else: #si event.getName().getText() = REGRESA, entonces
      print ("[ {} ]: recibi REGRESA en t={} del nodo {}".format(self.id, self.clock, event.getSource()))
      print ("\t ttl: {}".format(event.getName().getTtl()))
      self.OK[event.getSource()] = event.getName().getNodes() #se guarda la lista que envio su hijo

      c = self.makeList(event)

      for v in self.OK.values():
        try:
          #si la bandera del nodo hijo es un arreglo, se concatena a c
          #para enviar a un posible padre superior o imprimirla
          c += v
        except Exception as e:
          pass #para saltar el error provocado al momento de hacer la concatenacion

      print ("\t Lista de nodos {} \n".format(c))

      if False not in self.OK.values():
        if self.father != self.id:
          print ("\t Mando de regreso a mi padre {} \n".format(event.getSource()))
          newevent = Event(Message("REGRESA", event.getName().getTtl(), event.getName().getValue(), c), self.clock + 1.0, self.father, self.id)
          self.transmit(newevent)
        else: #la lista ya llego al nodo que inicio la busqueda
          print ("\n \t El valor {} esta en los nodos {} \n".format(event.getName().getValue(), c))
          print ("\t Datos finales") #simple formato de impresion

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
  n = randint(1,5) #quien busca
  b = randint(1,10) #que busca
  t = randint(1,2) #hasta donde hay que buscar

  print ("\nEl nodo {} quiere buscar el contenido {}".format(n, b))
  print ("a una distsncia de {} nodos a su alrededor".format(t))
  input ("Presione enter para continuar:\n ")

  #se inicia el evento semilla enviando un mensaje M al mismo nodo
  seed = Event(Message("M", t, b, []), 0.0, n, n)
  experiment.init(seed)
  experiment.run()

print ("Numero de mensajes: {}".format(experiment.nMessages))
print ("Tiempo transcurrido: {}".format(experiment.nTime))
