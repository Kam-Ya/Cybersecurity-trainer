class Player:
    __points
    __mult

    def __init___(self, points, mult):
        self.__points = 0
        self.__mult = 0.75

    def getPoints(self):
        return self.__points;

    def setPoints(self, points):
        self.__points = points

    def getMult(self):
        return self.__mult

    def setMult(self, mult):
        self.__mult = mult

    def calcPoints(self, time):
        return time * self.__mult # uses time in milliseconds
