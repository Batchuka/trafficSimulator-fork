from .vehicle_generator import VehicleGenerator
from .geometry.quadratic_curve import QuadraticCurve
from .geometry.cubic_curve import CubicCurve
from .geometry.segment import Segment
from .geometry.straight_segment import StraightSegment
from .vehicle import Vehicle

# LIGHT
from .traffic_light import TrafficLight

# TABLE_POSITION
from .position_table import PositionTable


class Simulation:

    def __init__(self):
        self.segments = []
        self.vehicles = {}
        self.vehicle_generator = []
        
        # LIGHT
        self.lights = []

        # POSITION TABLE
        self.position_table = PositionTable(self)

        self.t = 0.0
        self.frame_count = 0
        self.dt = 1/60  


    def add_vehicle(self, veh):
        self.vehicles[veh.id] = veh
        if len(veh.path) > 0:
            self.segments[veh.path[0]].add_vehicle(veh)

    def add_segment(self, seg):
        self.segments.append(seg)

    def add_vehicle_generator(self, gen):
        self.vehicle_generator.append(gen)

    # LIGHT
    def add_light(self, light):
        self.lights.append(light)

    
    def create_vehicle(self, **kwargs):
        veh = Vehicle(kwargs)
        self.add_vehicle(veh)

    def create_segment(self, start, end):
        seg = StraightSegment(start, end)
        self.add_segment(seg)

    def create_quadratic_bezier_curve(self, start, control, end):
        cur = QuadraticCurve(start, control, end)
        self.add_segment(cur)

    def create_cubic_bezier_curve(self, start, control_1, control_2, end):
        cur = CubicCurve(start, control_1, control_2, end)
        self.add_segment(cur)

    def create_vehicle_generator(self, **kwargs):
        gen = VehicleGenerator(kwargs)
        self.add_vehicle_generator(gen)
    
    # LIGHT
    def create_traffic_light(self, position, green_time, red_time):
        lig = TrafficLight(position, green_time, red_time)
        self.add_light(lig)


    def run(self, steps):

        # # all IDs must be enabled for this to work
        # self.position_table.start_thread()

        for _ in range(steps):
            self.update()
            # self.position_table.update_distances()

    def update(self):

        # Update vehicles
        for segment in self.segments:
            if len(segment.vehicles) != 0:
                self.vehicles[segment.vehicles[0]].update(None, self.dt)
            for i in range(1, len(segment.vehicles)):
                self.vehicles[segment.vehicles[i]].update(self.vehicles[segment.vehicles[i-1]], self.dt)
        
        # Update traffic lights
        for light in self.lights:
            light.update(self.dt)

        # Check roads for out of bounds vehicle
        for segment in self.segments:
            # If road has no vehicles, continue
            if len(segment.vehicles) == 0: continue
            # If not
            vehicle_id = segment.vehicles[0]
            vehicle = self.vehicles[vehicle_id]
            # If first vehicle is out of road bounds
            if vehicle.x >= segment.get_length():
                # If vehicle has a next road
                if vehicle.current_road_index + 1 < len(vehicle.path):
                    # Update current road to next road
                    vehicle.current_road_index += 1
                    # Add it to the next road
                    next_road_index = vehicle.path[vehicle.current_road_index]
                    self.segments[next_road_index].vehicles.append(vehicle_id)
                # Reset vehicle properties
                vehicle.x = 0
                # In all cases, remove it from its road
                segment.vehicles.popleft()

        # Update vehicle generators
        for gen in self.vehicle_generator:
            gen.update(self)
        
        # Increment time
        self.t += self.dt
        self.frame_count += 1
