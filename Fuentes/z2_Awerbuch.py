#
#      TORAL MALDONADO ROSA GUADALUPE
#               2153045948

# PRACTICA 2 Algoritmo 1: RECORRIDO DE NODOS
#               DFSAwerbuch

#         ALGORITMOS DISTRIBUIDOS

'''
  Se trabaja con 5 nodos
  Hace una busqueda primero en profundidad.
  Lo que hace es que un nodo avise a sus vecinos que ya fue agregado
  al arbol para que no vuelvan a enviarle mensajes de descubrimiento
  Se espera a que los vecinos contesten de enterado para poder continuar con el recorrido.
  Se envia un mensaje de descubre desde un nodo i a un nodo j
  para agregar al nodo j al arbol.
  El nodo j manda un mensaje a todos sus vecinos para indicar que ya fue visitado.
  Los vecinos avisan de vuelta que estan enterados.
  El nodo j manda un regresa al nodo i para indicar que ya se agrego al arbol.
  Si el nodo j se manda el regresa a si mismo es para continuar con el recorrido.
  TAREA: formar un arbol
'''

import sys
from event import Event
from model import Model
from process import Process
from simulator import Simulator
from simulation import Simulation

class Awerbuch(Model):
  # Hereda de la clase model e implementa de los metodos abstractos "init()" y "receive()"

  def init(self):
    '''
      Inicializacion de las variables del algoritmo.
    '''
    self.father = self.id #el padre. Al proncipio es el mismo
    self.unvisited = self.neighbors.copy() #lista de vecinos no visitados
    self.flags = dict.fromkeys(self.neighbors, '') #banderas de vecinos que saben que ya fui visitado

    print ("Inicio funciones {}".format(self.id))
    self.printData()

  def printData(self):
    '''
      Metodo auxiliar para imprimir los datos en el tiempo
    '''
    print ("\t Mi padre es: {}".format(self.father))
    print ("\t Vecinos no visitados: {}".format(self.unvisited))
    print ("\t Banderas de mis vecinos: {}".format(self.flags))
    #input ("\t Presione enter para continuar:\n ")

  def receive(self, event):
    '''
      Acciones de cada proceso. Se definen todas las acciones y los mnsajes que se mandan.
      Los mensajes que se mandan son del tipo STRING y son:
      DESCUBRE: el mensaje que se envia para agregar un nodo al recorrido
      REGRESA: mensaje que se manda al padre para indicar que yano tiene a mas vecinos
      VISITADO: mensaje que se envia a los vecinos para avisarles que ya fue visitado
      ACK: mensaje que se envia de los vecinos al padre para avisar que ya saben que fueron visitados
    '''
    if event.getName() == "DESCUBRE":
      print ("[ {} ]: recibi DESCUBRE en t={} del nodo {}".format(self.id, self.clock, event.getSource()))
      print ("\t Ya me visitaron")
      self.father = event.getSource()

      for n in self.neighbors:
        if n != self.father:
          newevent = Event("VISITADO", self.clock + 1.0, n, self.id)
          self.transmit(newevent)
          self.flags[n] = True

      if self.neighbors == [event.getSource()]:
        print ("\t Solo tengo de vecino a {} \n".format(event.getSource()))
        newevent = Event("REGRESA", self.clock + 1.0, event.getSource(), self.id)
        self.transmit(newevent)

      self.printData()


    elif event.getName() == "VISITADO":
      print ("[ {} ]: recibi VISITADO en t={} del nodo {}".format(self.id, self.clock, event.getSource()))
      print ("\t Nodo {} te confirmo que me llego el mensaje \n".format(event.getSource()))

      newevent = Event("ACK", self.clock + 1.0, event.getSource(), self.id) #se le manda al servidor
      self.transmit(newevent)
      self.unvisited.remove(event.getSource())
      self.printData()

    elif event.getName() == "ACK":
      print ("[ {} ]: recibi ACK en t={} del nodo {}".format(self.id, self.clock, event.getSource()))
      self.flags[event.getSource()] = False

      if True not in self.flags.values():
        print ("\t Me mandare un REGRESA")
        newevent = Event("REGRESA", self.clock + 0.0001, self.id, self.id)
        self.transmit(newevent)
      self.printData()

    else: #si event.getName() = REGRESA, entonces
      print ("[ {} ]: recibi REGRESA en t={} del nodo {}".format(self.id, self.clock, event.getSource()))

      if len(self.unvisited) > 0:
        newevent = Event("DESCUBRE", self.clock + 1.0, self.unvisited[0], self.id)
        self.transmit(newevent)
        del self.unvisited[0]
      elif self.father != self.id:
        newevent = Event("REGRESA", self.clock + 1.0, self.father, self.id)
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
    m = Awerbuch()
    experiment.setModel(m, i)

  #tiempos aleatorios. Se escojen en un rango menor al tiempo maximo
  #para evitar que un nodo pida el mapa en los tiempos ultimos tiempos
  #ya que puede suceder que la simulacion se detenga antes de enviar
  #el mapa o de liberarlo

  #se hacen dos solicitudes para arrancar el simulador
  seed = Event("DESCUBRE", -1.0, 1, 1) #solicitudes de dos nodos en diferentes tiempos
  experiment.init(seed)
  experiment.run()

print ("Numero de mensajes: {}".format(experiment.nMessages))
print ("Tiempo transcurrido: {}".format(experiment.nTime))
