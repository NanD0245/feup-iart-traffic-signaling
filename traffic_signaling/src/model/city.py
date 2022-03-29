from .car import Car
from .street import Street
from .intersection import Intersection, TrafficLight


class City:
    def __init__(self):
        self.cars = dict()
        self.streets = set()
        self.intersections = dict()
        self.duration = 0
        self.bonus = 0

    def from_input(input_file: str):
        with open(input_file) as f:
            lines = f.readlines()
        city = City()
        duration, _, no_streets, no_cars, bonus = lines[0].split(
            ' ')
        city.bonus = int(bonus)
        city.duration = int(duration)

        # add streets
        for line in lines[1:1+int(no_streets)]:
            line = line.strip('\n').split(' ')
            start_intersection = Intersection(int(line[0]))
            end_intersection = Intersection(int(line[1]))
            street = Street(line[2], int(line[3]))
            city.streets.add(street)

            # add start intersection
            if start_intersection.id in city.intersections:
                city.intersections[start_intersection.id].outgoing_streets.add(
                    street)
            else:
                start_intersection.outgoing_streets.add(street)
                city.intersections[start_intersection.id] = start_intersection

            # add end intersection
            if end_intersection.id in city.intersections:
                city.intersections[end_intersection.id].incoming_streets[street] = TrafficLight.RED
            else:
                end_intersection.incoming_streets[street] = TrafficLight.RED
                city.intersections[end_intersection.id] = end_intersection

        # add cars
        current_car: int = 0
        for line in lines[1+int(no_streets):1+int(no_streets)+int(no_cars)]:
            line = line.strip('\n').split(' ')
            path = []
            for name in line[1:]:
                path.append([s for s in city.streets if s.name == name][0])
            car = Car(path[1:])
            city.cars[current_car] = car
            current_car += 1
        return city

    def __str__(self):
        s = ""
        s += "Duration: " + str(self.duration) + "\n"
        s += "--------\n"
        for street in self.streets:
            s += str(street.name) + " has L=" + str(street.length) + "\n"
        s += "--------\n"
        for car_no in self.cars:
            s += "Car " + str(car_no) + " path: " + \
                str([st.name for st in self.cars[car_no].path]) + "\n"
        s += "--------\n"
        for intersection_id in self.intersections:
            s += "Intersection " + str(intersection_id) + " connects " + str(
                [(st.name, self.intersections[intersection_id].incoming_streets[st]) for st in self.intersections[intersection_id].incoming_streets]) + " to "\
                + str([st.name for st in self.intersections[intersection_id].outgoing_streets]) + "\n"
        return s
