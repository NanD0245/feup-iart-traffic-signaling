from collections import deque
from .city import City


class Schedule:
    def __init__(self):
        self.schedule = dict()

    def from_input(input_file: str):
        with open(input_file) as f:
            lines = f.readlines()
        lines = [line.strip('\n').split(' ') for line in lines]

        schedule = Schedule()
        lines = lines[1:]
        i = 0
        l_size = len(lines)
        while i < l_size:
            intersection_id = int(lines[i][0])
            no_streets = int(lines[i+1][0])
            schedule.schedule[intersection_id] = [
                name for name, duration in lines[i+2:i+2+no_streets] for _ in range(int(duration))]
            i += no_streets + 2

        return schedule

    def evaluate(self, city: City):
        # setup simulation helpers
        street_queue = {street_id: deque()
                        for street_id in range(city.no_streets)}
        green_cycle_duration = {intersection_id: len(self.schedule[intersection_id])
                                for intersection_id in self.schedule}
        car_path = {}
        next_analysed_time = {}
        for car in city.cars:
            car_path[car.id] = deque(car.path)
            street_queue[car_path[car.id][0].id].append(car.id)
            next_analysed_time[car.id] = 0

        # run simulation
        score = 0
        for current_time in range(city.duration+1):
            crossed_intersections = []
            scheduled_removals = []
            for car_id in car_path:
                if next_analysed_time[car_id] > current_time:
                    continue
                street = car_path[car_id][0]
                if street_queue[car_path[car_id][0].id][0] != car_id:
                    continue
                intersection_id = city.street_intersection[street.name]
                light_is_green = self.schedule[intersection_id][current_time %
                                                                green_cycle_duration[intersection_id]] == street.name
                if not light_is_green or intersection_id in crossed_intersections:
                    continue
                crossed_intersections.append(intersection_id)
                street_queue[street.id].popleft()
                car_path[car_id].popleft()
                next_street = car_path[car_id][0]
                next_time = current_time + next_street.length
                if len(car_path[car_id]) == 1:
                    scheduled_removals.append(car_id)
                    if next_time <= city.duration:
                        score += city.car_value + city.duration - next_time
                else:
                    street_queue[next_street.id].append(car_id)
                    next_analysed_time[car_id] = next_time
            for car_id in scheduled_removals:
                del car_path[car_id]

        return score

    def __str__(self):
        s = ""
        for intersection_id in self.schedule:
            unique_streets = set(self.schedule[intersection_id])
            s += "On intersection " + str(intersection_id) + " the lights are green for " + str(
                len(unique_streets)) + " incoming streets:\n"
            for name in unique_streets:
                duration = len([1 for street in self.schedule[intersection_id] if street == name])
                s += "- " + name + " for " + str(duration) + " seconds\n"
        return s
