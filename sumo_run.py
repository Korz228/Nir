import traci
import time
import traci.constants as tc
import pytz
import datetime
from random import randrange
import pandas as pd
import linecache

# Класс для представления graphического объекта
class Graph:

    def __init__(self, edges, n):
        # выделяет память для списка смежности
        self.adjList = [[] for _ in range(n)]

        # добавляет ребра в ориентированный graph
        for (src, dest) in edges:
            # выделяет узел в списке смежности от src до dest
            self.adjList[src].append(dest)


# Функция печати представления списка смежности Graph
def printGraph(graph):
    for src in range(len(graph.adjList)):
        # вывести текущую вершину и все соседние с ней вершины
        for dest in graph.adjList[src]:
            print(f'({src} —> {dest}) ', end='')
        print()

sumoCmd = ["sumo-gui", "-c", "my_config_file.sumocfg"]
traci.start(sumoCmd)
edgeGraph = []
edgeGraphz = [0]*5
a=()
listPrediction=[]
times=[0]*20
timeedges=[None]*20
check=[None]*20
test=(150,200)
routs = {'route2':[[1,2],[2,3],[3,4],[4,5]],'route3':[[1,2],[2,4],[4,5]]}

#начало цикла генерации Sumo
while traci.simulation.getMinExpectedNumber() > 0:

        traci.simulationStep();
        vehicles=traci.vehicle.getIDList();
        #цикл шага каждого тс
        for i in range(0,len(vehicles)):
                #в данной проврке мы определяем новое зашедшее в симуляцию тс, устанавливаем ему время зарежки с которым он вошел в симуляцию, а также делаем предсказание времени если это возможно
                if times[i]== 0 :
                 rou = routs[traci.vehicle.getRouteID(vehicles[i])]
                 times[i] = traci.vehicle.getDeparture(vehicles[i])
                 if len(edgeGraphz) >= len(rou) and edgeGraphz[len(edgeGraphz)-1]!= 0:
                  prediction=0
                  for k in rou:
                    for l in range(0,len(edgeGraphz)):
                     if k in edgeGraphz[l]:
                      prediction=prediction + edgeGraphz[l][1]
                  print('Prediction : ',traci.vehicle.getRouteID(vehicles[i]), ' ', prediction,'s')

                x, y = traci.vehicle.getPosition(vehicles[i])
                coord = [x, y]
                lon, lat = traci.simulation.convertGeo(x, y)
                gpscoord = [lon, lat]

                edge = traci.vehicle.getRoadID(vehicles[i])
                 #проверка в каком состоянии ребра тс, если первый символ двоеточие, то это значит тс на перекрестке и нужно считать ребро с которого оно приехало
                if edge[0]!= ':':
                 for h in range(0,len(edge)):
                  #изначально ребро считывается в виде "1_2", делаем из него [1,2]
                  if edge[h]=='_':

                   x=int(edge[:h])
                   y=int(edge[(len(edge)-1):])
                   a=[x,y]
                   #если мы на ребре в первый раз, добавляем в наш граф ребро
                   if a not in edgeGraph:
                    edgeGraph.append(a)
                 #записываем для каждого тс последнее ребро на котором оно было до заезда на новое
                 timeedges[i]=a
                 #при пересечении некоторых перекретков параметр edge дважды возвращает одно значение при въезде и выезде, это проверка, чтобы только один раз считалось
                elif edge != check[i]:
                 #записываем результат именно так, чтобы был взвешанный граф без повторяющихся ребер
                 edgeGraphz[edgeGraph.index(timeedges[i])] = [timeedges[i],traci.vehicle.getLastActionTime(vehicles[i])-times[i]]
                 # в переменной times хранится время заезда на граф для каждого тс
                 times[i]=traci.vehicle.getLastActionTime(vehicles[i])

                 check[i]=edge
             #проверка на достижение конечной точки маршрута, сумо считает так, что необязательно заехать на вершину и опытным путем найден диапазон при котором авто выйдет из симуляции (9,4% от каждой конечной координаты)
                if abs(test[0]-lon)<abs(test[0]*9.4/100) and abs(test[1]-lat)<abs(test[1]*9.4/100):
                                  edgeGraphz[edgeGraph.index(timeedges[i])]= [timeedges[i],traci.vehicle.getLastActionTime(vehicles[i])-times[i]]
                                  print('vec ',[i],' time : ',traci.vehicle.getRouteID(vehicles[i]),' ' ,  traci.vehicle.getLastActionTime(vehicles[i])-traci.vehicle.getDeparture(vehicles[i]))
                                  timeedges.remove(timeedges[i])
                                  times.remove(times[i])
                                  check.remove(check[i])

traci.close()
edges=edgeGraph
n=5
 # построить graph из заданного списка ребер
graph = Graph(edges, n)
#print(edgeGraphz)
    # печатать графа
printGraph(graph)
 # печатать конечного взвешанногографа
print(edgeGraphz)










