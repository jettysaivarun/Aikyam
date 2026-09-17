from fastapi import FastAPI
from pydantic import BaseModel
import math
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="AIKYAM Thermal Prototype",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)




MATERIALS = {
    "Mud": {
        "k": 0.60,
        "cp": 840,
        "density": 1700
    },
    "Concrete": {
        "k": 1.70,
        "cp": 880,
        "density": 2400
    },
    "Brick": {
        "k": 0.72,
        "cp": 840,
        "density": 1800
    },
    "Wood": {
        "k": 0.13,
        "cp": 1700,
        "density": 550
    },
    "Aerogel": {
        "k": 0.014,
        "cp": 1000,
        "density": 150
    }
}


@app.get("/")
def root():
    return {
        "message": "AIKYAM backend is running"
    }


@app.get("/materials")
def get_materials():
    return {
        "materials": MATERIALS
    }

def calculate_u_value(material, thickness):
    r_si = 0.13
    r_se = 0.04

    resistance = (
        r_si
        + thickness / material["k"]
        + r_se
    )

    return 1 / resistance

@app.get("/u-value")
def get_u_value():
    material = MATERIALS["Mud"]

    u = calculate_u_value(
        material,
        0.25
    )

    return {
        "material": "Mud",
        "thickness": 0.25,
        "u_value": u
    }
    
class SimulationRequest(BaseModel):
    climate: str

    width: float
    length: float
    height: float

    wall_material: str
    roof_material: str
    floor_material: str

    wall_thickness: float
    roof_thickness: float
    floor_thickness: float

    glazing_area: float
    
def get_climate(climate):

    if climate == "cold":
        return {
            "name": "Cold / High Altitude",
            "ambient_min": -12,
            "ambient_max": 9,
            "solar_peak": 850
        }

    if climate == "hot":
        return {
            "name": "Hot-Arid",
            "ambient_min": 17,
            "ambient_max": 38,
            "solar_peak": 850
        }

    return {
        "name": "Temperate",
        "ambient_min": 12,
        "ambient_max": 28,
        "solar_peak": 700
    }

def run_thermal_simulation(request):

    climate = get_climate(request.climate)

    wall = MATERIALS[request.wall_material]
    roof = MATERIALS[request.roof_material]
    floor = MATERIALS[request.floor_material]

    floor_area = request.width * request.length

    wall_area = (
        2 *
        (request.width + request.length) *
        request.height
    )

    roof_area = floor_area

    effective_wall_area = max(
        0,
        wall_area - request.glazing_area
    )

    wall_u = calculate_u_value(
        wall,
        request.wall_thickness
    )

    roof_u = calculate_u_value(
        roof,
        request.roof_thickness
    )

    floor_u = calculate_u_value(
        floor,
        request.floor_thickness
    )

    total_area = (
        effective_wall_area
        + roof_area
        + floor_area
    )

    average_u = (
        wall_u * effective_wall_area
        + roof_u * roof_area
        + floor_u * floor_area
    ) / total_area

    ambient = []
    indoor = []
    solar = []

    indoor_temperature = (
        climate["ambient_min"]
        + climate["ambient_max"]
    ) / 2

    for hour in range(24):

        angle = (
            (hour - 15)
            * 2
            * math.pi
            / 24
        )

        ambient_temperature = (
            (
                climate["ambient_min"]
                + climate["ambient_max"]
            ) / 2
            +
            (
                climate["ambient_max"]
                - climate["ambient_min"]
            ) / 2
            * math.sin(angle)
        )

        sunlight = max(
            0,
            math.sin(
                (hour - 6) * math.pi / 12
            )
        )

        solar_power = (
            climate["solar_peak"]
            * sunlight
            * roof_area
            * 0.5
        )

        heat_loss = (
            average_u
            * total_area
            * (
                indoor_temperature
                - ambient_temperature
            )
        )

        indoor_temperature += (
            0.08
            * (
                ambient_temperature
                - indoor_temperature
            )
            +
            solar_power / 10000
        )

        ambient.append(
            round(ambient_temperature, 2)
        )

        indoor.append(
            round(indoor_temperature, 2)
        )

        solar.append(
            round(solar_power, 2)
        )

    return {
        "hours": list(range(24)),
        "ambient": ambient,
        "indoor": indoor,
        "solar": solar,
        "wall_u": wall_u,
        "roof_u": roof_u,
        "floor_u": floor_u,
        "average_u": average_u
    }
    
    
@app.post("/simulate")
def simulate(request: SimulationRequest):

    return run_thermal_simulation(request)


