# 
# Implementa la simulacion de un PING/PONG
#
# Elaboro: Elizabeth Perez Cortes
#

import sys
from event import Event
from model import Model
from process import Process
from simulator import Simulator
from simulation import Simulation

class AlgorithmPingPong(Model):
  # Esta clase desciende de la clase Model e implementa los metodos 
  # "init()" y "receive()", que en la clase madre se definen como abstractos
  
  def init(self):
    # Aqui se definen e inicializan los atributos particulares del algoritmo
    print "Inicio funciones\n", self.id  
    self.sucesor = self.neighbors[0]
    print "Mis vecinos son:", self.sucesor
    print "Mi sucesor es:", self.sucesor

  def receive(self, event):
    # Aqui se definen las acciones concretas que deben ejecutarse cuando se
    # recibe un evento
    if event.getName() == "INICIA":
	print "[", self.id, "]: recibi INICIA en t=",self.clock," \n"
	newevent = Event("PING", self.clock + 1.0, self.sucesor, self.id)
	self.transmit(newevent)
	
    elif  event.getName() == "PING":
	print "[", self.id, "]: recibi PING en t=",self.clock," \n"
	newevent = Event("PONG", self.clock + 1.0, self.sucesor, self.id)
	self.transmit(newevent)
    else:      
	print "[", self.id, "]: recibi PONG en t=",self.clock," \n"
	newevent = Event("PING", self.clock + 1.0, self.sucesor, self.id)
	self.transmit(newevent)
	  

# ----------------------------------------------------------------------------------------
# "main()"
# ----------------------------------------------------------------------------------------
# construye una instancia de la clase Simulation recibiendo como parametros el nombre del 
# archivo que codifica la lista de adyacencias de la grafica y el tiempo max. de simulacion

if len(sys.argv) != 2:
    print "Por favor proporcione el nombre de la grafica de comunicaciones"
    raise SystemExit(1)

experiment = Simulation(sys.argv[1], 20)  

# asocia un pareja proceso/modelo con cada nodo de la grafica
for i in range(1,len(experiment.graph)+1):
    m = AlgorithmPingPong()
    experiment.setModel(m, i)

# inserta un evento semilla en la agenda y arranca

seed = Event("INICIA", 0.0, 1, 1)
experiment.init(seed)
experiment.run()


