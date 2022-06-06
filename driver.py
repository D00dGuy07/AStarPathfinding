import pygame
import pathfind

pygame.init()

surface = pygame.display.set_mode((400, 400))
clock = pygame.time.Clock()

mousePressed = False

shouldClose = False
while not shouldClose:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            shouldClose = True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_0:
                pathfind.onKeyPress('0')
            elif event.key == pygame.K_1:
                pathfind.onKeyPress('1')
            elif event.key == pygame.K_2:
                pathfind.onKeyPress('2')
            elif event.key == pygame.K_3:
                pathfind.onKeyPress('3')
            elif event.key == pygame.K_r:
                pathfind.onKeyPress('r')
            elif event.key == pygame.K_c:
                pathfind.onKeyPress('c')
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mousePressed = True

            mousePos = pygame.mouse.get_pos()
            pathfind.onMousePress(mousePos[0], mousePos[1])
        elif event.type == pygame.MOUSEBUTTONUP:
            mousePressed = False
        elif event.type == pygame.MOUSEMOTION:
            if mousePressed:
                mousePos = pygame.mouse.get_pos()
                pathfind.onMouseDrag(mousePos[0], mousePos[1])

    pathfind.onStep(surface)

    pygame.display.flip()
    clock.tick(60)