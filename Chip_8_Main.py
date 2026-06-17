import pygame
import sys
import random
import time
from pygame.event import Event
import os
from threading import Thread
from time import sleep

import Chip_8_CPU

def key_press(CPU, event):
    keys = { 
        pygame.K_1: 0x1, pygame.K_2: 0x2, pygame.K_3: 0x3, pygame.K_4: 0xC,
        pygame.K_q: 0x4, pygame.K_w: 0x5, pygame.K_e: 0x6, pygame.K_r: 0xD,
        pygame.K_a: 0x7, pygame.K_s: 0x8, pygame.K_d: 0x9, pygame.K_f: 0xE,
        pygame.K_z: 0xA, pygame.K_x: 0x0, pygame.K_c: 0xB, pygame.K_v: 0xF 
        }
    
    if event.key in keys:
        key = keys[event.key]
        if event.type == pygame.KEYDOWN:
            CPU.keys_pressed[key] = 1
        elif event.type == pygame.KEYUP:
            CPU.keys_pressed[key] = 0



def exit(CPU):
    pygame.quit()
    sys.exit()
    

def pixel_draw(screen, x, y, VMbit):#drawing a pixel on the screen, and scaling up to match screen size, VMbit is the bit for this pixel in memory
    u=x*10
    v=y*10
    pygame.draw.rect(screen,(255,255,255),(u,v,10,10),0)
        
        

def frame_draw(CPU, screen):
    pygame.Surface.fill(screen, (0, 0, 0))

    i=0 #where is the pixel in video memory
    for y in range (32):
        for x in range (64):
            if (CPU.VIDEOMEMORY[i]==1):
                pixel_draw(screen, x,y, CPU.VIDEOMEMORY[i])
            i+=1

    CPU.drawflag=0 #no longer need to redraw

    


def main(file):
    #initialising
    pygame.init()
    pygame.display.set_caption("C8")
    screen = pygame.display.set_mode((64*10,32*10))#scale factor of 10 for visibility
    pygame.Surface.fill(screen, (0, 0, 0)) #initially all black screen
    pygame.display.update()
    cycles=0


    
    c8= Chip_8_CPU.CPU()
    c8.open_rom(file)
    thread = Thread(target=c8.dec_timer, daemon = True)
    thread.start()

    #main loop
    CLOCK_SPEED = 500
    last_time = time.time()


    while (True):

        now = time.time()
        elapsed = now - last_time
        last_time=now

        cycles_this_frame = max(1, int(elapsed * CLOCK_SPEED))
        for _ in range(cycles_this_frame):
            c8.cpucycle()

        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit(c8)
            elif (event.type == pygame.KEYDOWN or event.type == pygame.KEYUP):
                key_press(c8, event)

        if c8.drawflag ==1:
            frame_draw(c8, screen)
            pygame.display.update()

        if c8.clearflag ==1:
            pygame.Surface.fill(screen, (0, 0, 0))
            c8.clearflag=0
            pygame.display.update()
            
        sleep(1/60)
            

        #+1 for each cycle
        cycles +=1

    exit(c8)
        
                

if __name__ == "__main__":
    if len(sys.argv) == 2:
        main(sys.argv[1])
    else:
        print("USE SYNTAX: python3 Chip_8_Main.py <FILE>")

                
            
