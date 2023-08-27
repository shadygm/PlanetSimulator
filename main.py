import pygame
import math
import tkinter as tk
from tkinter import simpledialog, colorchooser, ttk
import pygame_gui
pygame.init()

WIDTH, HEIGHT = 800, 800
SKIP = "SKIP"
WIN = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Solar System")

#make a global variable TIMESTEP
TIMESTEP = 3600*24
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
DARK_GREY = (80, 71, 88)
class Planet:
    AU = 149.6e6 * 1000
    G = 6.67428e-11
    SCALE = 250 / AU 

    def __init__(self, x, y, radius, color, mass):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.mass = mass

        self.orbit = []
        self.sun = False
        self.distance_to_sun = 0
        
        self.x_vel = 0
        self.y_vel = 0
    def draw(self, win):
        #get the width and height of the window when it is rescaled
        WIDTH = win.get_width()
        HEIGHT = win.get_height()
        x = self.x * self.SCALE + WIDTH/2
        y = self.y * self.SCALE + HEIGHT/2
        
        if len(self.orbit) > 2:    
          updated_points = []
          for point in self.orbit:
              x,y = point
              x = x * self.SCALE + WIDTH/2
              y = y * self.SCALE + HEIGHT/2
              updated_points.append((x,y))

          pygame.draw.lines(win, self.color, False, updated_points, 2)
          pygame.draw.circle(win, self.color, (x, y), self.radius)
          
    def attraction(self, other):
        other_x, other_y = other.x, other.y
        distance_x = other_x - self.x
        distance_y = other_y - self.y
        distance = math.sqrt(distance_x**2 + distance_y**2)

        if other.sun:
            self.distance_to_sun = distance
        
        force = self.G * self.mass * other.mass / (distance**2)

        theta = math.atan2(distance_y, distance_x)
        force_x = math.cos(theta) * force
        force_y = math.sin(theta) * force
        return force_x, force_y
    
    def update_position(self, planets):
        total_fx = total_fy = 0

        for planet in planets:
            if self == planet:
                continue
            fx, fy = self.attraction(planet)
            total_fx += fx
            total_fy += fy
        self.x_vel += total_fx / self.mass * TIMESTEP
        self.y_vel += total_fy / self.mass * TIMESTEP

        self.x += self.x_vel * TIMESTEP
        self.y += self.y_vel * TIMESTEP
        self.orbit.append((self.x, self.y))

def get_planet_info():
    root = tk.Tk()
    root.withdraw()
    try:
        x = float(simpledialog.askstring("Planet Info", "Enter the X coordinate of the planet(in AU): "))
        y = float(simpledialog.askstring("Planet Info", "Enter the Y coordinate of the planet(in AU): "))
        y_vel = float(simpledialog.askstring("Planet Info", "Enter the Y velocity of the planet(y_vel * 1000): "))
        
        coef = float(simpledialog.askstring("Planet Info", "Enter the mass coefficient: "))
        mag = float(simpledialog.askstring("Planet Info", "Enter the magnitude of exponent: "))
        mass = coef * 10**mag
        radius = mass / (1.9914e24)
        color_choice = colorchooser.askcolor(title="Select Planet Color")[0]
        color = pygame.Color(int(color_choice[0]), int(color_choice[1]), int(color_choice[2]))

        root.destroy()
    except:
        root.destroy()
        return SKIP, SKIP, SKIP, SKIP, SKIP, SKIP
    return x*Planet.AU, y*Planet.AU, y_vel*1000, radius, color, mass

def createPlanets():
    sun = Planet(0, 0, 30, YELLOW, 1.98892 * 10**30)
    sun.sun = True


    earth = Planet(-1 * Planet.AU, 0, 16, BLUE, 5.9742 * 10e24)
    earth.y_vel = 29.783 * 1000 

    mars = Planet(-1.524 * Planet.AU, 0, 12, RED, 6.39 * 10e23)
    mars.y_vel = 24.077 * 1000

    mercury = Planet(0.387 * Planet.AU, 0, 8, DARK_GREY, 3.30 * 10e23)
    mercury.y_vel = -47.4 * 1000

    venus = Planet(0.723 * Planet.AU, 0, 14, WHITE, 4.8685 * 10e24)
    venus.y_vel = -35.02 * 1000

    planets = [sun, earth, mars, mercury, venus]
    return planets



def main():
    run = True
    clock = pygame.time.Clock()

    manager = pygame_gui.UIManager((WIDTH, HEIGHT))
    planets = createPlanets()
    add_planet = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 10), (160, 30)), text="Add Planet", manager=manager)
    while run:
        clock.tick(60)
        time_delta = clock.tick(60)
        WIN.fill(BLACK)


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            manager.process_events(event)

            manager.update(time_delta)

            if add_planet.check_pressed():
                x, y, y_vel, radius, color, mass = get_planet_info()
                if x == SKIP:
                    break
                new_planet = Planet(x, y, radius, color, mass)
                new_planet.y_vel = y_vel
                planets.append(new_planet)

        for planet in planets:
            planet.update_position(planets)
            #check for collision between planets, if they collide remove the planet from the list
            for other in planets:
                if planet == other:
                    continue
                distance_x = other.x - planet.x
                distance_y = other.y - planet.y
                distance = math.sqrt(distance_x**2 + distance_y**2)
                if distance < planet.radius + other.radius:
                    planets.remove(planet)
                    break
            planet.draw(WIN)

        manager.draw_ui(WIN)
        pygame.display.update()  


    pygame.quit()



main()