#
#TORAL MALDONADO ROSA GUADALUPE
#          2153045948

# PRACTICA 4: DIFUSION BRADCAST
#            CBCast

#    ALGORITMOS DISTRIBUIDOS

'''
  Se trabaja con 3 nodos
  Cuando el nodo i quiere enviar un mensaje, se manda a todos los nodos del grafo junto con el reloj local.
  Cuando el nodo i recibe un mensaje, revisa en su reloj si ese mensaje era el que esperaba.
  Si es el mensaje esperado, actualiza su reloj con el reloj mas grande entre rl suyo propio y el que le llega.
  Si no es, lo poospone.
  Cuando se actualiza el reloj de i, revisa si tiene mensajes pospuestos por atender.
  De ser asi, lo atiende y actualiza el reloj nuevamente.
  TAREA: Recibir mensajes segun un orden causal

'''

import sys
from event import Event
from random import randint
from model import Model
from process import Process
from simulator import Simulator
from simulation import Simulation



class Message():
  '''
    Esta clase sirve para representar el mensaje y el reloj que se manda.
  '''
  def __init__(self, text, reloj):
    self.text = text #Mensaje a eifundir
    self.reloj = reloj #Reloj que se manda en el mensaje

  '''
    Metodos para obtener los valores de sus parametros
  '''

  def getText(self):
    return self.text

  def getReloj(self):
    return self.reloj


class CBCast(Model):
  # Hereda de la clase model e implementa de los metodos abstractos "init()" y "receive()"

  def init(self):
    '''
      Inicializacion de las variables del algoritmo.
      Para el evento inicia, reloj se utiliza para guardar los tiempos en los que se mandan los mensajes
    '''
    aux = self.neighbors.copy()
    aux.append(self.id) #se debe agregar el propio id para contar en el reloj
    aux.sort() #para que los relojes tengan sus entradas en el mismo orden
    self.reloj = dict.fromkeys(aux, 0) #reloj vectorial local. Se guarda como un diccionario para que las entradas coincidan con el id del nodo
    self.deferred = {} #lista de mensajes en espera. Se guards como un diccionario con el id del nodo que manda el mensaje como llave, y el mensaje como contenido

    print ("Inicio funciones {}".format(self.id))
    self.printData()


  def printData(self):
    '''
      Metodo auxiliar para imprimir los datos en el tiempo
    '''
    print ("\t Mi reloj es: {}".format(self.reloj.values()))
    print ("\t Mensajes diferidos: {}".format(self.deferred))
    input ("\t Presione enter para continuar:\n ")


  def compare_with_local(self, recived, id_recived):
    '''
      Metodo auxiliar que compara cualquier reloj con el reloj local.
      Recibe como parametros el reloj y el id del nodo que lo manda
      Regresa:
        True si el mensaje que llego es el que se esperaba y !las entradas del reloj que llego son menores a las del reloj local
        False si no se cumple alguna de las anteriores
    '''
    flag = 0
    #se compara entrada por entrada que las entradas del reloj recivido sean menores al local.
    #la vandera, flag se pone a 1 de ser asi.
    #con una sola entrada que no cumpla, la bandera cambia a 0 y se deja de comparar
    for e in self.reloj:
      if e != id_recived:
        if self.reloj[e] >= recived[e]:
          flag = 1
        else:
          flag = 0
          break

    #si el mensaje que llego es el que se esperaba y si todas las entradas del recibido son menores al local
    if recived[id_recived]==self.reloj[id_recived]+1 and flag == 1:
      return True
    else:
      return False


  def max(self, clock):
    '''
      Metodo auxiliar que escoje las entradas mas grandes entre un reloj y el reloj local
      para asignarlas al reloj local
      Recive como parametro el reloj con el que hay que comparar
    '''
    #si la entrada r del reloj recibido es mayor a la del local,
    #se cambia la entrada del local con la recibida
    #de otro modo se conserva la entrada del local
    for r in self.reloj:
      if self.reloj[r] < clock[r]:
        self.reloj[r] = clock[r]


  def pop_message(self):
    '''
      Metodo auxiliar que sirve para sacar los mensajes de la lista de mensajes diferidos
    '''
    for n in self.deferred:
      print ("\nse sacaran los mensajes pendientes del nodo {}".format(self.id))
      reloj_recv = self.deferred[n].getReloj()
      print ("\t reloj recibido del nodo {}: {}".format(n, reloj_recv.values()))
      print ("\t reloj local: {}".format(self.reloj.values()))

      #si el id del nodo que envia el reloj, es diferente del local y el mensaje es el que se esperaba,
      #se recibe el mensaje
      if n!=self.id and self.compare_with_local(reloj_recv, n):
        print (("\t\t recibi mensaje "+self.deferred[n].getText()+" en t={} del nodo {} \n").format(self.clock+1, n))
        self.max(reloj_recv)
        del self.deferred[n] #se elimina el mensaje
        if len(self.deferred) == 0: #si ya no hay mensajes por revisar, se detiene el metodo
          break
        else:
          n = self.deferred.keys()[0] #si todavia hay mensajes, se busca desde el principio


  def receive(self, event):
    '''
      Acciones de cada proceso. Se definen todas las acciones y los mnsajes que se mandan.
      Los mensajes que se mandan son el mensaje a difundir y el reloj
      INICIA: mensaje de texto que inicia el algoritmo
      El nodo emisor puede enviar cualquier cosa
    '''
    if event.getName().getText() == "INICIA":
      print ("[ {} ]: mando un mensaje a difundir en t={}".format(self.id, self.clock))
      self.reloj[self.id] += 1

      #los tiempos para enviarlos vienen en la variable reloj del mensaje.
      #Solo aqui se hace este cambio de tipo de variable para poder asignar los tempos en los que se mandan los mensajes
      for n in range(len(self.neighbors)):
        #se manda una copia del reloj para evitar problemas de escritura en memoria
        newevent = Event(Message("Hola desde {}".format(self.id), self.reloj.copy()), event.getName().getReloj()[n], self.neighbors[n], self.id)
        self.transmit(newevent)

      self.printData()

    else:
      print ("[ {} ]: recibi CLOCK en t={} del nodo {}".format(self.id, self.clock, event.getSource()))
      print ("\t reloj recibido: {}".format(event.getName().getReloj().values()))
      print ("\t reloj local: {}".format(self.reloj.values()))

      #si el id del nodo que envia el reloj, es diferente del local y el mensaje es el que se esperaba,
      #se recibe el mensaje. De otra manera se pospone (difiere
      if event.getSource()!=self.id and self.compare_with_local(event.getName().getReloj(), event.getSource()):
        print ("\t recibi mensaje "+event.getName().getText())
        self.max(event.getName().getReloj())
        self.pop_message() #se saca algun mensaje de la$lista de diferidos
      else:
        print ("\t mensaje diferido")
        self.deferred[event.getSource()] = event.getName()

      self.printData()




if __name__ == "__main__":
  if len(sys.argv) != 2:
    print ("Por favor proporcione el nombre de la grafica de comunicaciones")
    raise SystemExit(1)

  #se crea una instancia de la clase Simulation y se le pasa como parametros el archivo
  #con el grafo y el tiempo maximo de ejecucion
  experiment = Simulation(sys.argv[1], 6)

  # asocia un pareja proceso/modelo con cada nodo de la grafica
  for i in range(1,len(experiment.graph)+1):
    m = CBCast()
    experiment.setModel(m, i)

  t1 = randint(1,3) #tiempo en el que el nodo decide hacer el brodscat
  t2 = randint(1,6) #tiempo en el que se manda a uno de sus vecinos
  t3 = randint(1,6) #tiempo en el que se manda a uno de sus vecinos
  while t2 == t3:
    #para evitar tiempos iguales
    t2 = randint(1,6)
    t3 = randint(1,6)

  #se inicia el evento semilla enviando un mensaje INICIA al mismo nodo
  #en el reloj del mensaje se manda una lista con los tiempos en los que se desea se eeciban los mensajes
  #e hizo asi para simular que los mensajes llegan a diferentes tiempos
  seed = Event(Message("INICIA", [t2, t3]), t1, 1, 1)
  experiment.init(seed)

  print ("el nodo 1 decide hacer brodcast en el tiempo {}".format(t1))
  print ("manda al nodo 2 en el tiempo {} y al nodo 3 en el tiempo {} \n".format(t2, t3))

  t1 = randint(1,3)
  t2 = randint(1,6)
  t3 = randint(1,6)
  while t2 == t3:
    t2 = randint(1,6)
    t3 = randint(1,6)

  seed = Event(Message("INICIA", [t2, t3]), t1, 2, 2)
  experiment.init(seed)

  print ("el nodo 1 decide hacer brodcast en el tiempo {}".format(t1))
  print ("manda al nodo 2 en el tiempo {} y al nodo 3 en el tiempo {} \n".format(t2, t3))

  t1 = randint(1,3)
  t2 = randint(1,6)
  t3 = randint(1,6)
  while t2 == t3:
    t2 = randint(1,6)
    t3 = randint(1,6)

  seed = Event(Message("INICIA", [t2, t3]), t1, 3, 3)
  experiment.init(seed)

  print ("el nodo 1 decide hacer brodcast en el tiempo {}".format(t1))
  print ("manda al nodo 2 en el tiempo {} y al nodo 3 en el tiempo {} \n".format(t2, t3))

  input ("presione enter para continuar \n")

  experiment.run()

print ("Numero de mensajes: {}".format(experiment.nMessages))
print ("Tiempo transcurrido: {}".format(experiment.nTime))
