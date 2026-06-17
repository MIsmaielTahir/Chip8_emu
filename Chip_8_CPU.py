import pygame
import sys
import random
import time
from threading import Thread
from pygame.event import Event
from time import sleep


class CPU:
    def __init__(CPU):
    
    #Memory:
        CPU.MEMORY = [0]* 4096
        CPU.VIDEOMEMORY = [0]* (64*32) #0 means black, 1 means white
        CPU.STACK = [0]*16 #Used to store the address that the interpreter should return when finished with a subroutine. Up to 16 nested subroutines.
        CPU.START_ADDRESS = 0x200
        CPU.FONTSET_START_ADDRESS = 0x50
        


    #Registers:
    #General purpose registers
        CPU.V=[0] * 16 #16 8 bit registers V[0] through to V[0xF] in hex, final V[0xF] register is used as a flag for some instructions and is not general purpose

        CPU.I=0 #Index register, used for memory addresses



        CPU.DELAY=0 #internal delay - decremented at 60hz
        CPU.SOUND=0 #sound timer - decremented at 60hz


        

    #Inaccessible counters to general programs

        CPU.PC = 0x200 #PROGRAM COUNTER

    #fontset:
        CPU.fontset = [0xF0, 0x90, 0x90, 0x90, 0xF0, #0
                        0x20, 0x60, 0x20, 0x20, 0x70, #1
                        0xF0, 0x10, 0xF0, 0x80, 0xF0, #2
                        0xF0, 0x10, 0xF0, 0x10, 0xF0, #3
                        0x90, 0x90, 0xF0, 0x10, 0x10, #4
                        0xF0, 0x80, 0xF0, 0x10, 0xF0, #5
                        0xF0, 0x80, 0xF0, 0x90, 0xF0, #6
                        0xF0, 0x10, 0x20, 0x40, 0x40, #7
                        0xF0, 0x90, 0xF0, 0x90, 0xF0, #8
                        0xF0, 0x90, 0xF0, 0x10, 0xF0, #9
                        0xF0, 0x90, 0xF0, 0x90, 0x90, #A
                        0xE0, 0x90, 0xE0, 0x90, 0xE0, #B
                        0xF0, 0x80, 0x80, 0x80, 0xF0, #C
                        0xE0, 0x90, 0x90, 0x90, 0xE0, #D
                        0xF0, 0x80, 0xF0, 0x80, 0xF0, #E
                        0xF0, 0x80, 0xF0, 0x80, 0x80] #F
        for i in range(80):
            CPU.MEMORY[CPU.FONTSET_START_ADDRESS + i] = CPU.fontset[i]

    #Drawflag- used to specify when to update screen: =1 means it needs to be updated. Clearflag indicates screen needs to be cleared.
        CPU.drawflag = 0
        CPU.clearflag = 0

    #keypress - current pressed key
        CPU.keys_pressed = [0]*16

        

    #change a byte
    def set_byte(CPU,index:int, val:int):
        CPU.MEMORY[index]=val

    #get byte value
    def get_byte(CPU, index:int):
        return CPU.MEMORY[index]

    #get a specific character
    def get_char(CPU, char: int):
        return CPU.FONTSET_START_ADDRESS + char * 5


    #write into video memory
    def VMwrite(CPU, x, y, newval):
        if (x<64 and y<32 and x >= 0 and y >= 0):
            pos=(x+(y*64))#cooridinates to VM array position
            if (CPU.VIDEOMEMORY[pos]==1 and int(newval)==1): #sprite collision
                CPU.V[0xF]= 1 
            CPU.VIDEOMEMORY[pos]^= int(newval)

        

    #loading roms
    def open_rom(CPU, file_name):
        try:
            with open("roms/" + file_name, "rb") as f:
                file_bytes = f.read()
                for i in range(len(file_bytes)):
                    CPU.MEMORY[0x200+i] = int(file_bytes[i])
        except:
            print("SYNTAX: python3 Chip_8_Main.py <FILE>")
            print("EXAMPLE: python3 Chip_8_Main.py INVADERS")
            
            pygame.quit()
            sys.exit()

    def dec_timer(CPU):
        while True:
            if CPU.DELAY > 0:
                CPU.DELAY -= 1

            if CPU.SOUND > 0:
                CPU.SOUND -= 1
            sleep(1 / 60)
    


    def fetch(CPU):
        return ((CPU.get_byte(CPU.PC) << 8) | CPU.get_byte(CPU.PC + 1))


    def cpucycle(CPU):
        #fetch-decode-execute
        opcode = CPU.fetch()
        lookup = opcode & 0xF000
        x= (opcode & 0x0F00)>>8
        y= (opcode & 0x00F0)>>4

        #OPCODES LOOPUP

        #clear screen
        if (opcode == 0x00E0):
            CPU.VIDEOMEMORY = [0]* (64*32)
            CPU.clearflag =1

            
        #return from subroutine
        elif(opcode == 0x00EE):
            CPU.PC = CPU.STACK.pop()


        #(0x1nnn)jump to location 0x0nnn
        elif(lookup == 0x1000):
            CPU.PC = (opcode & 0x0FFF) -2
            
        #(0x2nnn)call subroutine at nnn
        elif(lookup == 0x2000):
            CPU.STACK.append(CPU.PC)
            CPU.PC=(opcode & 0x0FFF)-2#-2 since we have +2 at end of function


            
        #(0x3xkk) skip next instruction if V[x]==kk
        elif(lookup == 0x3000):
            if(CPU.V[x]==(opcode& 0x00FF)):
                CPU.PC+=2
                
        #(0x4xkk) skip next instruction if V[x]!=kk
        elif(lookup == 0x4000):
            if(CPU.V[x]!=(opcode& 0x00FF)):
                CPU.PC+=2

        #(0x5xy0) skip next instruction if V[x]=V[y]
        elif(lookup == 0x5000):
            if(CPU.V[x]==CPU.V[y]):
                CPU.PC+=2
                
        #(0x6xkk) Set V[x] = kk.
        elif(lookup == 0x6000):
            new = (opcode& 0x00FF)
            CPU.V[x]= new

        #(0x7xkk) Set V[x] = V[x] + kk
        elif(lookup == 0x7000):
            CPU.V[x] = (CPU.V[x] + (opcode & 0x00FF)) & 0xFF
            

        elif(lookup==0x8000):

            #(8xy0) Set V[x] = V[x]
            if((opcode & 0x000F)==0):
                CPU.V[x]= CPU.V[y]
                
            #(8xy1) Set V[x] = V[x] OR V[y]
            elif((opcode & 0x000F)==1):
                CPU.V[x]= (CPU.V[x] | CPU.V[y])

            #(8xy2) Set V[x] = V[x] AND V[y]   
            elif((opcode & 0x000F)==2):
                CPU.V[x]= (CPU.V[x] & CPU.V[y])       

            #(8xy3) Set V[x] = V[x] XOR V[y]
            elif((opcode & 0x000F)==3):
                CPU.V[x]= (CPU.V[x] ^ CPU.V[y])
                
            #(8xy4) Set V[x] = V[x] + V[y], if new V[x]>255, V[0xF]=1.
            elif((opcode & 0x000F)==4):
                z = (CPU.V[x] + CPU.V[y])
                CPU.V[x]= (z & 0xFF) #only keep smallest 8 bits
                if (z>0xFF):
                    CPU.V[0x0F]=1
                else:
                    CPU.V[0x0F]=0
                    
            #(8xy5) Set V[x] = V[x] - V[y], if old V[x]>V[y], V[0xF]=1.
            elif((opcode & 0x000F)==5):
                flag = 0
                if (CPU.V[x]>CPU.V[y]):
                    flag =1
                CPU.V[x]=((CPU.V[x]-CPU.V[y])& 0xFF)#ensuring compatibility
                CPU.V[0xF]=flag
                
            #(8xy6) If the least significant bit of V[x] is 1, then V[0xF]=1. Then V[x] is divided by 2
            elif((opcode & 0x000F)==6):
                if((CPU.V[x]&0b1)==1):
                    CPU.V[0xF]=1
                else:
                    CPU.V[0xF]=0
                CPU.V[x]=(CPU.V[x] >> 1)

            #(8xy7) Set V[x] = V[y] - V[x], if old V[x]>V[y], V[0xF]=1.
            elif((opcode & 0x000F)==7):
                flag = 0
                if (CPU.V[x]<CPU.V[y]):
                    flag =1
                CPU.V[x]=((CPU.V[x]-CPU.V[y])& 0xFF)#ensuring compatibility
                CPU.V[0xF]=flag

            #(8xyE) If the most significant bit of V[x] is 1, then V[0xF]=1. Then V[x] is mutliplied by 2                
            elif((opcode & 0x000F)==0xE):
                flag = 0
                if((CPU.V[x]&0x80)!=0):
                    flag=1
                CPU.V[x]=((CPU.V[x] << 1)& 0xFF)
                CPU.V[0xF]=flag

        #(0x9xy0) skip next instruction if V[x] != V[y]        
        elif (lookup == 0x9000):
            if(CPU.V[x]!= CPU.V[y]):
                CPU.PC +=2
            
            
        #(0xAnnn) set index register to nnn
        elif (lookup == 0xA000):
            CPU.I=opcode & 0x0FFF
        
        #(0xBnnn) jump to location nnn + V[0]
        elif (lookup == 0xB000):
            CPU.PC = ((opcode &0x0FFF)+CPU.V[0]) -2

        #(0xCxkk) Set V[x] to a random byte AND kk
        elif (lookup == 0xC000):
            kk= (opcode & 0x00FF)
            CPU.V[x] = ((random.randint(0,255))&kk)

        #(Dxyn) display n-byte sprite starting at memory location I at (V[x], V[y]), set V[F] for collision
        elif(lookup == 0xD000):
            n = (opcode & 0x000F)
            CPU.V[0xF] = 0
            for i in range(n):
                sprite_byte = CPU.MEMORY[CPU.I + i]
                for j in range(8):
                    bit = (sprite_byte >> (7 - j)) & 0x01
                    CPU.VMwrite((CPU.V[x] + j), (CPU.V[y] + i), bit)
            CPU.drawflag = 1
            
        #(0xEx9E) skip next instruction if key with the value of V[x] is pressed
        elif((opcode & 0xF0FF)== 0xE09E):
            if(CPU.keys_pressed[CPU.V[x]]==1):
                CPU.PC+=2

        #(0xExA1) skip next instruction if key with the value of V[x] is not pressed
        elif((opcode & 0xF0FF)== 0xE0A1):
            if(CPU.keys_pressed[CPU.V[x]]!=1):
                CPU.PC+=2

        #(0xFx07) set V[x] delay timer value
        elif((opcode & 0xF0FF)== 0xF007):
            CPU.V[x]=CPU.DELAY

        #(0xFx0A) wait for key press and store the value of the key in V[x]
        elif((opcode & 0xF0FF) == 0xF00A):
            found = False
            for i in range(16):
                if CPU.keys_pressed[i] == 1:
                    CPU.V[x] = i
                    found = True
                    break
            if not found:
                CPU.PC -= 2

        #(0xFx15) set CPU delay timer value
        elif((opcode & 0xF0FF)== 0xF015):
            CPU.DELAY=CPU.V[x]

        #(0xFx18) set sound timer to V[x]
        elif((opcode & 0xF0FF)== 0xF018):
            CPU.SOUND=CPU.V[x]
                     
        #(0xFx1E) Add V[x] to index register
        elif((opcode & 0xF0FF)== 0xF01E):
            CPU.I=CPU.V[x]+CPU.I

        #(0xFx29) Set I = location of sprite for digit Vx.
        elif((opcode & 0xF0FF)== 0xF029):
            CPU.I = CPU.FONTSET_START_ADDRESS + (CPU.V[x] * 5)
            
        #(0xFx33) Store BCD representation of Vx in memory locations I, I+1, and I+2.
        elif((opcode & 0xF0FF)== 0xF033):
            BCD = int(CPU.V[x])
            CPU.MEMORY[CPU.I]   = BCD // 100
            CPU.MEMORY[CPU.I+1] = (BCD % 100) // 10
            CPU.MEMORY[CPU.I+2] = BCD % 10

        #(0xFx55) Store registers V0 through Vx in memory starting at location I.
        elif((opcode & 0xF0FF)== 0xF055):
            k = int(x)
            for i in range (k+1):
                CPU.MEMORY[CPU.I+i]=(CPU.V[i])          


        #(0xFx65) Read registers V0 through Vx from memory starting at location I.
        elif((opcode & 0xF0FF)== 0xF065):
            for i in range (x+1):
                (CPU.V[i])=CPU.MEMORY[CPU.I+i]


        CPU.PC+=2




