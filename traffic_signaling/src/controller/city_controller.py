import pygame
import math
from collections import deque
from time import sleep
from traffic_signaling.src.model.city import City
from traffic_signaling.src.model.schedule import Schedule
from traffic_signaling.src.view.city_viewer import CityViewer

BG_COLOR = (50, 220, 230)
BG_IMAGE = 'traffic_signaling/asset/img/grass.jpg'
MARGIN_OFFSET = 50


class CityController:
    def __init__(self, city: City, window, window_size) -> None:
        self.city = city
        self.city_viewer = CityViewer(city)
        self.schedule = None
        self.time = 0
        self.window = window
        self.window_size = window_size
        self.set_intersection_pos()

    def set_schedule(self, schedule: Schedule):
        self.schedule = schedule

    def set_intersection_pos(self) -> None:
        intersections_no = len(self.city.intersections)
        center = ((self.window_size[0] + 300) / 2, self.window_size[1] / 2)
        radius = self.window_size[1] / 2 - MARGIN_OFFSET
        angle = 0
        rotation_angle = (2 * math.pi) / intersections_no
        for _id, intersection in self.city.intersections.items():
            intersection.set_pos(center[0] + math.sin(angle)*radius,
                                 center[1] + math.cos(angle)*radius)

            angle += rotation_angle
        return

    def simulate(self):
        if self.schedule == None:
            print('ERROR: Schedule is missing')
            return 1

        street_queue = {street_id: deque()
                        for street_id in range(self.city.no_streets)}

        green_cycle_duration = {intersection_id: len(self.schedule.schedule[intersection_id])
                                for intersection_id in self.schedule.schedule}

        car_path = {}
        next_analysed_time = {}
        for car in self.city.cars:
            car_path[car.id] = deque(car.path)
            street_queue[car_path[car.id][0].id].append(car.id)
            next_analysed_time[car.id] = 0

        score = 0
        for current_time in range(self.city.duration + 1):
            crossed_intersections = []
            scheduled_removals = []
            green_lights_streets = []

            for id, intersection in self.schedule.schedule.items():
                green_lights_streets.append(
                    intersection[current_time % green_cycle_duration[id]])

            cars_position = {car_id: [car_path[car_id][0].id, max(next_analysed_time[car_id] - current_time, 0)]
                             for car_id in car_path}

            for car_id in car_path:
                if next_analysed_time[car_id] > current_time:
                    continue
                street = car_path[car_id][0]
                if street_queue[street.id][0] != car_id:
                    continue
                intersection_id = self.city.street_intersection[street.name]
                light_is_green = self.schedule.schedule[intersection_id][current_time %
                                                                         green_cycle_duration[intersection_id]] == street.name
                if not light_is_green or intersection_id in crossed_intersections:
                    continue

                crossed_intersections.append(intersection_id)
                street_queue[street.id].popleft()
                car_path[car_id].popleft()

                if len(car_path[car_id]) == 0:
                    scheduled_removals.append(car_id)
                    score += self.city.car_value + self.city.duration - next_time
                else:
                    next_street = car_path[car_id][0]
                    next_time = current_time + next_street.length
                    street_queue[next_street.id].append(car_id)
                    next_analysed_time[car_id] = next_time
            for car_id in scheduled_removals:
                del car_path[car_id]

            self.draw(green_lights_streets, cars_position, current_time, score)

            sleep(1)

    def draw(self, green_lights, cars_position, current_time, score):
        bg = pygame.transform.scale(
            pygame.image.load(BG_IMAGE), self.window_size)
        self.window.blit(bg, (0, 0))

        self.city_viewer.draw(self.window, green_lights, cars_position)

        self.city_viewer.draw_infos(self.window, current_time, score)

        pygame.display.flip()