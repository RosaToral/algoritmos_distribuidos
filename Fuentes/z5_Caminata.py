#
#      TORAL MALDONADO ROSA GUADALUPE
#               2153045948

# PRACTICA 3 Version 3: BUSQUEDA DE CONTENIDO EN UNA RED
#               PIF Segall

#         ALGORITMOS DISTRIBUIDOS

'''
  Se trabaja con 5 nodos
  Hace una busqueda primero en amplitud.
'''

import sys
from random import randint, choice
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
  def __init__(self, text, ttl, value, nodes, path):
    self.text = text #Mensaje M o Regresa
    self.ttl = ttl #Contador de la distancia a recorrer
    self.value = value #El contenido que desea buscarse
    self.nodes = nodes #Lista de nodos
    self.path = path #camino de nodos recorrido

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

  def getPath(self):
    return self.path



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
    if event.getName().getValue() in self.content and self.id not in event.getName().getNodes():
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
    input ("\t Presione enter para continuar:\n ")

  def receive(self, event):
    '''
      Acciones de cada proceso. Se definen todas las acciones y los mnsajes que se mandan.
      Los mensajes que se mandan son objetos de la clsse Message y los textos de Mensajes que se mandan son:
      M: mensaje que recorre el grafo enviando la lista de nodos, el contenido a buscar y decrementando el ttl para la distancia
      REGRESA: mensaje de regreso que envia al padre la lista de nodos que tienen el cotenido a buscar
    '''
    if event.getName().getText() == "INICIA":
      print ("\nEl nodo {} quiere buscar el contenido {}".format(self.id, event.getName().getValue()))
      print ("a una distsncia de {} nodos a su alrededor".format(event.getName().getTtl()))
      input ("Presione enter para continuar:\n ")

      self.state = True
      r = choice(self.neighbors)
      newevent = Event(Message("M", event.getName().getTtl()-1, event.getName().getValue(), [], event.getName().getPath()+[self.id]), self.clock, r, self.id)
      self.transmit(newevent)

    elif event.getName().getText() == "M":
      print ("[ {} ]: recibi M en t={} del nodo {}".format(self.id, self.clock, event.getSource()))
      print ("\t ttl: {}".format(event.getName().getTtl()))
      print ("\t El camino recorrido: {} \n".format(event.getName().getPath()+[self.id]))

      if event.getSource() != self.id: #para evitar un error si el mensaje se manda de un nodo a si mismo
        self.OK[event.getSource()] = True

      if self.state == False:
        self.father = event.getSource()
        self.state = True

      flag = 0

      if event.getName().getTtl() > 0:
        r = choice(self.neighbors)
        aux = []
        while flag != (r==self.father or r in event.getName().getPath() or r in aux):
          r = choice(self.neighbors)
          flag+=1


      if event.getName().getTtl()==0 or flag==len(self.neighbors) or False not in self.OK.values():
        #si el ttl es cero o si su unico vecino era su padre
        c = self.makeList(event)
        p = event.getName().getPath().pop()
        print ("\t Mando de regreso a {} \n".format(p))

        newevent = Event(Message("REGRESA", event.getName().getTtl(),event.getName().getValue(), c, event.getName().getPath()	), self.clock + 1.0, p, self.id)
        self.transmit(newevent)

      elif flag != len(self.neighbors):
        r = choice(self.neighbors)
        while r==self.father or r in event.getName().getPath():
          r = choice(self.neighbors)
        newevent = Event(Message("M", event.getName().getTtl()-1, event.getName().getValue(), [], event.getName().getPath()+[self.id]), self.clock + 1, r, self.id)
        self.transmit(newevent)

      self.printData()

    else: #si event.getName().getText() = REGRESA, entonces
      print ("[ {} ]: recibi REGRESA en t={} del nodo {}".format(self.id, self.clock, event.getSource()))
      print ("\t ttl: {}".format(event.getName().getTtl()))
      print ("\t El camino recorrido: {} \n".format(event.getName().getPath()))

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

      if len(event.getName().getPath()) > 0:
        p = event.getName().getPath().pop()
        print ("\t Mando de regreso a {} \n".format(p))
        newevent = Event(Message("REGRESA", event.getName().getTtl(), event.getName().getValue(), c, event.getName().getPath()), self.clock + 1.0, p, self.id)
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


  #se inicia el evento semilla enviando un mensaje M al mismo nodo
  seed = Event(Message("INICIA", 2, b, [], []), 0.0, 1, 1)
  experiment.init(seed)
  experiment.run()

print ("Numero de mensajes: {}".format(experiment.nMessages))
print ("Tiempo transcurrido: {}".format(experiment.nTime))
