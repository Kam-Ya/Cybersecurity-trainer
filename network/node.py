import random

class Node:
    
    __infected: bool
    __conections

    text

    def __init__(self):
        self.__infected = False
        self.text = "I am a Node!"

    def prop(self):
        randInt = random.randint(0, len(self.__connections))

        if (self.__connections[randInt].isInfected() == False):
            connections[randInt].infect()

    def infect(self):
        self.__infected = True
        self.text = "I am an Evil Node"

    def isInfected(send):
        return self.__infected
