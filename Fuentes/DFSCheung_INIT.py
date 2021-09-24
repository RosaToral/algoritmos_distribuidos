# Este archivo implementa la simulacion del algoritmo de
# recorrido en profundidad de Cheung

import sys
from event import Event
from model import Model
from process import Process
from simulator import Simulator
from simulation import Simulation

class AlgorithmDFS(Model):
  # Esta clase desciende de la clase Model e implementa los metodos
  # "init()" y "receive()", que en la clase madre se definen como abstractos

  def init(self):
    # Aqui se definen e inicializan los atributos particulares del algoritmo
    self.father = self.id
    self.visited = False
    self.unvisited = self.neighbors

  def go_explore_more(self):
    if len(self.unvisited) > 0:
      to_visit = self.unvisited[0]
      self.unvisited = self.unvisited[1:len(self.unvisited)]
      newevent = Event("DESCUBRE", self.clock + 1.0, to_visit, self.id)
      self.transmit(newevent)
    elif self.father != self.id:
      newevent = Event("REGRESA", self.clock + 1.0, self.father, self.id)
      self.transmit(newevent)
      print (self.id,'termino')
    else:
      print (self.id,'termino')


  def receive(self, event):
    # Aqui se definen las acciones concretas que deben ejecutarse cuando se
    # recibe un evento

    print ("T = ", self.clock, " Nodo ", self.id, " Recibo :", event.getName(), "desde", event.getSource())

    if  event.getName() == "INICIA":
        self.visited = True
        print ("RAIZ", self.id)
        self.go_explore_more()

    elif  event.getName() == "DESCUBRE":
      self.unvisited.remove(event.getSource())
      if self.visited == True:
        newevent = Event("RECHAZO", self.clock + 1.0, event.getSource(), self.id)
        self.transmit(newevent)
      else:
        self.visited = True
        self.father = event.getSource()
        print ("Soy ", self.id, " y mi padre es ", self.father)
        self.go_explore_more()

    elif  event.getName() == "REGRESA" or event.getName() == "RECHAZO":
      self.go_explore_more()


# ----------------------------------------------------------------------------------------
# "main()"
# ----------------------------------------------------------------------------------------
# construye una instancia de la clase Simulation recibiendo como parametros el nombre del 
# archivo que codifica la lista de adyacencias de la grafica y el tiempo max. de simulacion

if len(sys.argv) != 2:
    print ("Por favor dame el nombre del archivo con la grafica de comunicaciones")
    raise SystemExit(1)

experiment = Simulation(sys.argv[1], 100)

# asocia un pareja proceso/modelo con cada nodo de la grafica
for i in range(1,len(experiment.graph)+1):
    m = AlgorithmDFS()
    experiment.setModel(m, i)

# inserta un evento semilla en la agenda y arranca

seed = Event("INICIA", 0.0, 1, 1)
experiment.init(seed)
experiment.run()
print ("Mensajes enviados: {}".format(experiment.nMessages))
print ("Tiempo consumido: {}".format(experiment.nTime))

