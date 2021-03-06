import pygame
from math import atan2, degrees, radians, cos, sin, dist
from model.city import City

INTERSECTION_COLOR = (255, 196, 77)
INTERSECTION_SIZE = 45
NODES_FONT_SIZE = 25
FONT_SIZE = 35
TEXT_COLOR = (240, 240, 240)
ID_COLOR = (0, 150, 255)
BLOCKSIZE = 40
CAR_LEN = 40
CAR_WIDTH = 30
GREEN = (0, 255, 0)
RED = (255, 0, 0)
LIGHT_OFFSET = 70
CAR_OFFSET = 1.8

ROAD_IMAGE = 'traffic_signaling/asset/img/road.png'
CAR_IMAGE = 'traffic_signaling/asset/img/car.png'
GREEN_LIGHT_IMAGE = 'traffic_signaling/asset/img/green.png'
RED_LIGHT_IMAGE = 'traffic_signaling/asset/img/red.png'


class CityViewer:
    def __init__(self, city: City) -> None:
        """
        Constructor of CityViewer class

        Properties:
            city (City): city with all the intersections of the problem
            streets (list): list of all streets that belong to the city
        """
        self.city = city
        self.streets = self.get_streets()

    def get_streets(self):
        """
        Obtains all the streets (name, lenght, start/end intersection, etc) from the city

        Returns:
            list with all streets that belong to the city
        """
        streets = []
        for id1, intersection1 in self.city.intersections.items():
            for outcoming in intersection1.outgoing_streets:
                st = False
                for id2, intersection2 in self.city.intersections.items():
                    for incoming in intersection2.incoming_streets:
                        if (outcoming.id == incoming.id):
                            streets.append(
                                (outcoming.id, id1, id2, outcoming.name, outcoming.length))
                            st = True
                            break
                    if st:
                        break
        return streets

    def draw(self, window, green_lights_streets, cars_position) -> None:
        """
        Draw the city state starting by drawing each street as well the cars that are going through them.
        Finally the intersections are drawn with the indication of the rescpective id

        Parameters:
            window (Surface): pygame window for display
            green_lights_streets (list): list of all the green lights of the city in the current state
            cars_position (list): list of the position of each car in the current state
        """
        for street in self.streets:
            green = street[3] in green_lights_streets
            self.draw_street(window, street, green)

            for id, info in cars_position.items():
                if info[0] == street[0]:
                    self.draw_car(window, street, info[1])

        font = pygame.font.SysFont(None, NODES_FONT_SIZE)

        for id, intersection in self.city.intersections.items():
            self.draw_intersection(window, id, intersection, font)

    def draw_street(self, window, street, green):
        """
        Draws a street starting by calculating the slope of the street and its distance to
        connect the two intersections 

        Parameters:
            window (Surface): pygame window for display
            street (tuple): tuple with the necessary information about the street
            green (boolean): true if the light is green, false otherwise (light is red)
        """
        start_intersect_pos = self.city.intersections[street[1]].get_pos()
        end_intersect_pos = self.city.intersections[street[2]].get_pos()

        angle = degrees(atan2(end_intersect_pos[1] - start_intersect_pos[1],
                              end_intersect_pos[0] - start_intersect_pos[0]))

        road_block, green_block, red_block = self.load_blocks(angle)

        pos = start_intersect_pos

        distance = dist(pos, end_intersect_pos)

        while (dist(pos, end_intersect_pos) <= distance):
            distance = dist(pos, end_intersect_pos)
            if green and distance < LIGHT_OFFSET:
                rotated_center = (green_block.get_rect(
                    center=(pos[0], pos[1])))
                window.blit(green_block, rotated_center)
            elif not green and distance < LIGHT_OFFSET:
                rotated_center = (red_block.get_rect(
                    center=(pos[0], pos[1])))
                window.blit(red_block, rotated_center)
            else:
                rotated_center = (road_block.get_rect(
                    center=(pos[0], pos[1])))
                window.blit(road_block, rotated_center)

            pos = (pos[0] + round(BLOCKSIZE*cos(radians(angle))),
                   pos[1] + round(BLOCKSIZE*sin(radians(angle))))

    def draw_car(self, window, street, l):
        """
        Draws a car in the right position of the street 

        Parameters:
            window (Surface): pygame window for display
            street (tuple): tuple with the necessary information about the street
            l (integer): lenght of the street already driven by the car
        """
        start_intersect_pos = self.city.intersections[street[1]].get_pos()
        end_intersect_pos = self.city.intersections[street[2]].get_pos()

        angle = atan2(end_intersect_pos[1] - start_intersect_pos[1],
                      end_intersect_pos[0] - start_intersect_pos[0])

        distance = dist(start_intersect_pos, end_intersect_pos) / street[4]

        if l == 0:
            pos = (start_intersect_pos[0] + round(street[4] * distance * cos(angle) - CAR_OFFSET * BLOCKSIZE * cos(angle)),
                   start_intersect_pos[1] + round(street[4] * distance * sin(angle) - CAR_OFFSET * BLOCKSIZE * sin(angle)))
        else:
            pos = (start_intersect_pos[0] + round((street[4] - l) * distance * cos(angle) - 0.5 * distance * cos(angle)),
                   start_intersect_pos[1] + round((street[4] - l) * distance * sin(angle) - 0.5 * distance * sin(angle)))

        car = self.load_car(angle)

        rotated_center = (car.get_rect(
            center=(pos[0], pos[1])))
        window.blit(car, rotated_center)

    def draw_intersection(self, window, id, intersection, font):
        """
        Draw intersection in the window

        Parameters:
            window (Surface): pygame window for display
            id (integer): id of the intersection
            intersection (Intersection): intersection to get the screen position to draw
            font (Font): pygame Font object to write into a surface
        """
        pygame.draw.circle(window, INTERSECTION_COLOR,
                           intersection.get_pos(), INTERSECTION_SIZE)
        img = font.render(str(id), True, ID_COLOR)
        pos = intersection.get_pos()
        window.blit(img, (pos[0] - 5, pos[1] - 7))

    def draw_infos(self, window, current_time, score):
        """
        Draw informations of the current state in the window

        Parameters:
            window (Surface): pygame window for display
            current_time (integer): time of the current state
            score (integer): score of the current state
        """
        window_width, window_height = window.get_size()
        font = pygame.font.SysFont(None, FONT_SIZE)
        self.draw_time(font, window, window_width, current_time)
        self.draw_streets_info(font, window)
        self.draw_score(font, window, window_width, window_height, score)

    def draw_time(self, font, window, window_width, current_time):
        """
        Draw time of the current state in the window

        Parameters:
            font (Font): pygame Font object to write into a surface
            window (Surface): pygame window for display
            window_width (integer): width of the pygame window
            current_time (integer): time of the current state
        """
        img = font.render("Time Limit = " +
                          str(self.city.duration), True, TEXT_COLOR)
        window.blit(img, (window_width - img.get_size()[0] - 50, 40))

        img = font.render("Current Time = " +
                          str(current_time), True, TEXT_COLOR)
        window.blit(img, (window_width - img.get_size()[0] - 50, 70))

    def draw_streets_info(self, font, window):
        """
        Draw streets informations of the current state in the window

        Parameters:
            font (Font): pygame Font object to write into a surface
            window (Surface): pygame window for display
        """
        img = font.render("Start - End - Name - Time",
                          True, TEXT_COLOR)
        window.blit(img, (50, 40))

        height = 100
        for street in self.streets:
            img = font.render(str(street[1]) + " - " + str(street[2]) + " - " + street[3] + " - " + str(street[4]),
                              True, TEXT_COLOR)
            window.blit(img, (50, height))
            height += 30

    def draw_score(self, font, window, window_width, window_height, score):
        """
        Draw score of the current state in the window

        Parameters:
            font (Font): pygame Font object to write into a surface
            window (Surface): pygame window for display
            window_width (integer): width of the pygame window
            window_height (integer): height of the pygame window
            score (integer): score of the current state
        """
        img = font.render("Current Score = " +
                          str(score), True, TEXT_COLOR)
        window.blit(img, (window_width - img.get_size()[0] - 50,
                          window_height - img.get_size()[1] - 40))

    def load_blocks(self, angle):
        """
        Load blocks for pygame (street, red and green image) and scale and rotate each image according to the angle of the street

        Parameters:
            angle (float): angle of the street

        Return:
            tuple with each block (street, red and green block)
        """
        green_block = pygame.image.load(GREEN_LIGHT_IMAGE).convert_alpha()
        green_block = pygame.transform.scale(
            green_block, (BLOCKSIZE, BLOCKSIZE))

        red_block = pygame.image.load(RED_LIGHT_IMAGE).convert_alpha()
        red_block = pygame.transform.scale(
            red_block, (BLOCKSIZE, BLOCKSIZE))

        road_block = pygame.image.load(ROAD_IMAGE).convert_alpha()
        road_block = pygame.transform.scale(
            road_block, (BLOCKSIZE, BLOCKSIZE))

        return (pygame.transform.rotate(road_block, -angle),
                pygame.transform.rotate(green_block, -angle),
                pygame.transform.rotate(red_block, -angle))

    def load_car(self, angle):
        """
        Load car image, scale and rotate the image according to the angle of the street

        Parameters:
            angle (float): angle of the street

        Return:
            car block to draw in the window
        """
        car = pygame.image.load(CAR_IMAGE).convert_alpha()
        car = pygame.transform.scale(
            car, (CAR_LEN, CAR_WIDTH))
        return pygame.transform.rotate(car, -degrees(angle))
