import pygame
import math
import array

class vec2:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        
    def __eq__(self, other):
        if isinstance(other, vec2):
            return self.x == other.x and self.y == other.y
        return False
        
    def __hash__(self):
        return hash(self.x) ^ hash(self.y)

class Grid2D:
    def __init__(self, width, height, default=0, fill=True):
        self.Width = width
        self.Height = height
        self.Buffer = array.array('H')
        if fill:
            self.Buffer.extend([default] * width * height)
            
    def Get(self, coord):
        if coord.x >= 0 and coord.x < self.Width and coord.y >= 0 and coord.y < self.Height:
            return self.Buffer[coord.y * self.Width + coord.x]
        return 0
        
    def Set(self, coord, value):
        self.Buffer[coord.y * self.Width + coord.x] = value
        
    def Copy(self):
        gridCopy = Grid2D(self.Width, self.Height, fill=False)
        gridCopy.Buffer.extend(self.Buffer)
        return gridCopy

SelectedMode = 2
StartPos = None
EndPos = None
                
Grid = Grid2D(50, 50)

tileColors = [
    None,                # 0 : Empty
    (0, 0, 0),           # 1 : Obstacle
    (255, 0, 0),         # 2 : Start
    (0, 255, 0),         # 3 : End
    
    (255, 165, 0),       # 4 : Evaluated
    (0, 0, 255),         # 5 : To Evaluate
    (255, 0, 255)        # 6 : Path
]

def GreedyMeshStart(grid):
    for y in range(grid.Height):
        for x in range(grid.Width):
            if grid.Get(vec2(x, y)) != 0:
                return vec2(x, y)
                
    return None
        
def DrawGrid(grid, surface):
    tileWidth = 400 / grid.Width
    tileHeight = 400 / grid.Height
    
    surface.fill((255, 255, 255))
    
    meshState = grid.Copy()
    
    startCoord = GreedyMeshStart(meshState)
    while startCoord != None:
        tileType = meshState.Get(startCoord)
        
        endCoord = startCoord
        while meshState.Get(vec2(endCoord.x + 1, endCoord.y)) == tileType:
            endCoord = vec2(endCoord.x + 1, endCoord.y)
            
        expandingY = True
        while expandingY:
            for x in range(startCoord.x, endCoord.x + 1):
                if meshState.Get(vec2(x, endCoord.y + 1)) != tileType:
                    expandingY = False
                    break
            
            if expandingY:
                endCoord = vec2(endCoord.x, endCoord.y + 1)
                
        for y in range(startCoord.y, endCoord.y + 1):
            for x in range(startCoord.x, endCoord.x + 1):
                meshState.Set(vec2(x, y), 0)
                
        startX = startCoord.x * tileWidth
        startY = startCoord.y * tileHeight
        width = (endCoord.x + 1 - startCoord.x) * tileWidth
        height = (endCoord.y + 1 - startCoord.y) * tileHeight
        pygame.draw.rect(surface, tileColors[tileType], pygame.Rect(startX, startY, width, height))
        
        startCoord = GreedyMeshStart(meshState)
    
    #for y in range(grid.Height):
    #    for x in range(grid.Width):
    #        color = tileColors[grid.Get(vec2(x, y))]
    #        if color != None:
    #            grid.Group.add(Rect(x * tileWidth, y * tileHeight, tileWidth, tileHeight, fill=color))
        
def Paint(mouseX, mouseY):
    global Grid
    global SelectedMode
    global StartPos
    global EndPos

    gridX = math.floor(mouseX / (400 / Grid.Width))
    gridY = math.floor(mouseY / (400 / Grid.Height))
    
    coord = vec2(gridX, gridY)
    
    if SelectedMode == 0 or SelectedMode == 1:
        Grid.Set(coord, SelectedMode)
    if SelectedMode == 2:
        if StartPos != None:
            Grid.Set(StartPos, 0)
        Grid.Set(coord, 2)
        StartPos = coord
    if SelectedMode == 3:
        if EndPos != None:
            Grid.Set(EndPos, 0)
        Grid.Set(coord, 3)
        EndPos = coord

def onMousePress(x, y):
    Paint(x, y)
    
def onMouseDrag(x, y):
    Paint(x, y)
    
    
def AStarReconstructPath(cameFrom, current):
    totalPath = [current]
    while current in cameFrom.keys():
        current = cameFrom[current]
        totalPath.append(current)
    totalPath.reverse()
    return totalPath

def Manhattan(p1, p2):
    return abs(p1.x - p2.x) + abs(p1.y - p2.y)

def AStarHeuristic(node):
    global EndPos
    return Manhattan(EndPos, node)

openSet = []
closedSet = []
cameFrom = {}
gScore = {}
fScore = {}
Running = False
Complete = False
Path = []

def AStar():
    global openSet
    global closedSet
    global cameFrom
    global gScore
    global fScore
    global Running
    global Complete
    global Path
    global StartPos

    openSet = [StartPos]
    closedSet = []
    
    cameFrom = {}
    
    gScore = {}
    gScore[StartPos] = 0
    
    fScore = {}
    fScore[StartPos] = AStarHeuristic(StartPos)
    
    Running = True
    
def AStarStep():
    global openSet
    global closedSet
    global cameFrom
    global gScore
    global fScore
    global Running
    global Complete
    global Path
    global EndPos

    if not len(openSet) > 0:
        Running = False
        Complete = True
        return
    
    current = openSet[0]
    for node in openSet:
        if fScore.get(node, math.inf) < fScore.get(current, math.inf):
            current = node
            
    openSet.remove(current)
    closedSet.append(current)
    Grid.Set(current, 4)
    
    if current.x == EndPos.x and current.y == EndPos.y:
        Running = False
        Complete = True
        Path = AStarReconstructPath(cameFrom, current)
        return
    
    neighbors = [
#        vec2(current.x - 1, current.y - 1),
        vec2(current.x,     current.y - 1),
#        vec2(current.x + 1, current.y - 1),
        vec2(current.x + 1, current.y),
#        vec2(current.x + 1, current.y + 1),
        vec2(current.x,     current.y + 1),
#        vec2(current.x - 1, current.y + 1),
        vec2(current.x - 1, current.y),
    ]
    
    for neighbor in neighbors:
        if (neighbor.x < 0 or neighbor.x >= Grid.Width or 
            neighbor.y < 0 or neighbor.y >= Grid.Height or 
            Grid.Get(neighbor) == 1 or
            neighbor in closedSet):
            continue
        
        tentativeGScore = gScore.get(current, math.inf) + Manhattan(current, neighbor)
        if tentativeGScore < gScore.get(neighbor, math.inf):
            cameFrom[neighbor] = current
            gScore[neighbor] = tentativeGScore
            fScore[neighbor] = tentativeGScore + AStarHeuristic(neighbor)
            if neighbor not in openSet:
                openSet.append(neighbor)
                Grid.Set(neighbor, 5)

def onStep(surface):
    global Running
    global Complete
    global StartPos
    global EndPos
    global Grid
    global Path

    if Running:
        AStarStep()
        AStarStep()
        AStarStep()
    if Complete:
        Complete = False
        for location in Path:
            Grid.Set(location, 6)
    
    if StartPos != None:
        Grid.Set(StartPos, 2)
    if EndPos != None:
        Grid.Set(EndPos, 3)
    DrawGrid(Grid, surface)
    
def onKeyPress(key):
    global StartPos
    global EndPos
    global SelectedMode

    if key == 'r':
        if StartPos != None and EndPos != None:
            AStar()
            
    if key == 'c':
        for y in range(Grid.Height):
            for x in range(Grid.Width):
                coord = vec2(x, y)
                if Grid.Get(coord) > 3:
                    Grid.Set(coord, 0)

    if key == '0':
        SelectedMode = 0
    elif key == '1':
        SelectedMode = 1
    elif key == '2':
        SelectedMode = 2
    elif key == '3':
        SelectedMode = 3