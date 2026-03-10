inp = input("How many nodes: ")

while (inp < 1):
    inp = input("How many Nodes: ")

N = Node

for i in range(inp) - 1:
    N.connect # this function still needs to be implemented
    N.conn

# so the game lasts until the user quits
while (1):
    check = input("Which node to check (type -1 to exit): ")
    
    if check == 0:
        print(N.text)
    else if check == -1:
        break
    else:
        temp = N.find(check-1)
        print(temp.text) # this function also still needs to be implemented
    evil = input("Flag: Y/N")

    if (temp.isInfected() and evil == y):
        # Add points
    else:
        temp.propogate
        # other punishment?
