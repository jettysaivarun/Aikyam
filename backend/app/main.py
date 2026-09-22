from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
import math


# ============================================================
# APP
# ============================================================

app = FastAPI(
    title="AIKYAM",
    description="Climate-aware passive shelter design optimizer",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# MATERIAL DATABASE
# ============================================================

MATERIALS = {

    # --------------------------------------------------------
    # WALL MATERIALS
    # --------------------------------------------------------

    "Mud": {
        "type": "wall",
        "k": 0.60,
        "cp": 840,
        "density": 1700,
        "cost": 850,
        "co2": 0.08,
        "availability": 0.95,
        "durability": 0.70,
    },

    "Adobe": {
        "type": "wall",
        "k": 0.45,
        "cp": 840,
        "density": 1600,
        "cost": 1100,
        "co2": 0.10,
        "availability": 0.90,
        "durability": 0.75,
    },

    "Brick": {
        "type": "wall",
        "k": 0.72,
        "cp": 840,
        "density": 1820,
        "cost": 1200,
        "co2": 0.22,
        "availability": 0.98,
        "durability": 0.95,
    },

    "Concrete": {
        "type": "wall",
        "k": 1.70,
        "cp": 880,
        "density": 2400,
        "cost": 1450,
        "co2": 0.32,
        "availability": 0.99,
        "durability": 0.98,
    },

    "Stone": {
        "type": "wall",
        "k": 1.80,
        "cp": 790,
        "density": 2600,
        "cost": 1800,
        "co2": 0.18,
        "availability": 0.80,
        "durability": 0.98,
    },

    "Compressed Earth Block": {
        "type": "wall",
        "k": 0.55,
        "cp": 900,
        "density": 1900,
        "cost": 1050,
        "co2": 0.07,
        "availability": 0.85,
        "durability": 0.85,
    },

    "Hemp-Lime": {
        "type": "wall",
        "k": 0.09,
        "cp": 1500,
        "density": 300,
        "cost": 2300,
        "co2": -0.10,
        "availability": 0.55,
        "durability": 0.70,
    },

    "Straw Bale": {
        "type": "wall",
        "k": 0.06,
        "cp": 1300,
        "density": 120,
        "cost": 1600,
        "co2": -0.15,
        "availability": 0.60,
        "durability": 0.65,
    },

    "Insulated Earth Wall": {
        "type": "wall",
        "k": 0.18,
        "cp": 1100,
        "density": 1000,
        "cost": 1750,
        "co2": 0.03,
        "availability": 0.78,
        "durability": 0.85,
    },


    # --------------------------------------------------------
    # ROOF MATERIALS
    # --------------------------------------------------------

    "Metal Sheet": {
        "type": "roof",
        "k": 0.50,
        "cp": 500,
        "density": 7800,
        "cost": 850,
        "co2": 0.35,
        "availability": 0.98,
        "durability": 0.90,
    },

    "Clay Tile": {
        "type": "roof",
        "k": 0.80,
        "cp": 840,
        "density": 1800,
        "cost": 1100,
        "co2": 0.18,
        "availability": 0.90,
        "durability": 0.90,
    },

    "Concrete Slab": {
        "type": "roof",
        "k": 1.70,
        "cp": 880,
        "density": 2400,
        "cost": 1500,
        "co2": 0.32,
        "availability": 0.99,
        "durability": 0.98,
    },

    "Bamboo Roof": {
        "type": "roof",
        "k": 0.15,
        "cp": 1600,
        "density": 700,
        "cost": 1250,
        "co2": 0.02,
        "availability": 0.82,
        "durability": 0.75,
    },

    "Insulated Panel": {
        "type": "roof",
        "k": 0.035,
        "cp": 1400,
        "density": 120,
        "cost": 2200,
        "co2": 0.12,
        "availability": 0.75,
        "durability": 0.90,
    },

    "Aerogel": {
        "type": "roof",
        "k": 0.014,
        "cp": 1000,
        "density": 150,
        "cost": 3500,
        "co2": 0.08,
        "availability": 0.55,
        "durability": 0.90,
    },

    "Thatch": {
        "type": "roof",
        "k": 0.09,
        "cp": 1500,
        "density": 250,
        "cost": 900,
        "co2": -0.05,
        "availability": 0.88,
        "durability": 0.60,
    },


    # --------------------------------------------------------
    # FLOOR MATERIALS
    # --------------------------------------------------------

    "Wood": {
        "type": "floor",
        "k": 0.13,
        "cp": 1700,
        "density": 550,
        "cost": 1400,
        "co2": 0.08,
        "availability": 0.92,
        "durability": 0.80,
    },

    "Bamboo": {
        "type": "floor",
        "k": 0.16,
        "cp": 1500,
        "density": 700,
        "cost": 1250,
        "co2": 0.03,
        "availability": 0.88,
        "durability": 0.78,
    },

    "Earth": {
        "type": "floor",
        "k": 0.60,
        "cp": 840,
        "density": 1700,
        "cost": 700,
        "co2": 0.04,
        "availability": 0.98,
        "durability": 0.65,
    },

    "Stone Floor": {
        "type": "floor",
        "k": 1.80,
        "cp": 790,
        "density": 2600,
        "cost": 1500,
        "co2": 0.18,
        "availability": 0.90,
        "durability": 0.98,
    },

    "Concrete Floor": {
        "type": "floor",
        "k": 1.70,
        "cp": 880,
        "density": 2400,
        "cost": 1350,
        "co2": 0.30,
        "availability": 0.99,
        "durability": 0.98,
    },

    "Cork": {
        "type": "floor",
        "k": 0.04,
        "cp": 1800,
        "density": 240,
        "cost": 1800,
        "co2": -0.05,
        "availability": 0.60,
        "durability": 0.75,
    },
}


WALLS = [
    name for name, data in MATERIALS.items()
    if data["type"] == "wall"
]

ROOFS = [
    name for name, data in MATERIALS.items()
    if data["type"] == "roof"
]

FLOORS = [
    name for name, data in MATERIALS.items()
    if data["type"] == "floor"
]


# ============================================================
# CLIMATE DATABASE
# ============================================================

CLIMATES = {

    "cold": {
        "name": "Cold / High Altitude",
        "base_temp": 5,
        "temp_amplitude": 8,
        "solar_peak": 650,
        "humidity": 45,
        "ideal_min": 18,
        "ideal_max": 25,
    },

    "hot": {
        "name": "Hot-Arid",
        "base_temp": 28,
        "temp_amplitude": 12,
        "solar_peak": 850,
        "humidity": 30,
        "ideal_min": 22,
        "ideal_max": 28,
    },

    "humid": {
        "name": "Warm-Humid",
        "base_temp": 29,
        "temp_amplitude": 5,
        "solar_peak": 700,
        "humidity": 75,
        "ideal_min": 23,
        "ideal_max": 28,
    },

    "temperate": {
        "name": "Temperate",
        "base_temp": 22,
        "temp_amplitude": 7,
        "solar_peak": 650,
        "humidity": 55,
        "ideal_min": 20,
        "ideal_max": 26,
    },
}


# ============================================================
# LOCATION DATABASE
# ============================================================

LOCATIONS = {

    "Leh": "cold",
    "Srinagar": "cold",

    "Delhi": "hot",
    "Jaipur": "hot",
    "Hyderabad": "hot",
    "Vijayawada": "hot",

    "Chennai": "humid",
    "Kochi": "humid",

    "Bengaluru": "temperate",
}


# ============================================================
# PYDANTIC MODELS
# ============================================================

class Dimensions(BaseModel):
    width: float = Field(gt=0)
    length: float = Field(gt=0)
    height: float = Field(gt=0)


class DesignRequest(BaseModel):

    location: Optional[str] = "Leh"
    climate: Optional[str] = "cold"

    dimensions: Dimensions

    budget: float = Field(
        default=50000,
        ge=10000,
        le=500000
    )

    glazing_area: float = Field(
        default=2.0,
        ge=0
    )

    wall_material: str
    roof_material: str
    floor_material: str

    wall_thickness: float = Field(
        default=0.25,
        gt=0
    )

    roof_thickness: float = Field(
        default=0.12,
        gt=0
    )

    floor_thickness: float = Field(
        default=0.10,
        gt=0
    )


class OptimizeRequest(BaseModel):

    location: Optional[str] = "Leh"
    climate: Optional[str] = "cold"

    dimensions: Dimensions

    budget: float = Field(
        default=50000,
        ge=10000,
        le=500000
    )

    glazing_area: float = Field(
        default=2.0,
        ge=0
    )

    wall_thickness: float = Field(
        default=0.25,
        gt=0
    )

    roof_thickness: float = Field(
        default=0.12,
        gt=0
    )

    floor_thickness: float = Field(
        default=0.10,
        gt=0
    )


class CompareRequest(BaseModel):

    current: DesignRequest
    optimized: DesignRequest


# ============================================================
# HELPERS
# ============================================================

def get_material(name: str) -> Dict:
    if name not in MATERIALS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown material: {name}"
        )

    return MATERIALS[name]


def get_climate(
    climate: Optional[str],
    location: Optional[str]
) -> Dict:

    if location and location in LOCATIONS:
        climate = LOCATIONS[location]

    if climate not in CLIMATES:
        climate = "temperate"

    return CLIMATES[climate]


def calculate_u_value(
    material_name: str,
    thickness: float
) -> float:

    material_data = get_material(material_name)

    k = material_data["k"]

    # Interior + exterior surface resistances
    r_surface = 0.17

    resistance = (
        r_surface +
        thickness / k +
        r_surface
    )

    return 1 / resistance


def calculate_areas(
    dimensions: Dimensions,
    glazing_area: float
) -> Dict[str, float]:

    width = dimensions.width
    length = dimensions.length
    height = dimensions.height

    floor_area = width * length

    wall_area = (
        2 * (width + length) * height
    )

    roof_area = floor_area

    glazing = min(
        glazing_area,
        wall_area * 0.5
    )

    opaque_wall_area = max(
        wall_area - glazing,
        0
    )

    return {
        "floor_area": floor_area,
        "roof_area": roof_area,
        "wall_area": wall_area,
        "glazing_area": glazing,
        "opaque_wall_area": opaque_wall_area,
    }


def calculate_material_cost(
    material_name: str,
    area: float
) -> float:

    material_data = get_material(material_name)

    return material_data["cost"] * area


def calculate_sustainability(
    wall: Dict,
    roof: Dict,
    floor: Dict
) -> float:

    avg_co2 = (
        wall["co2"] +
        roof["co2"] +
        floor["co2"]
    ) / 3

    avg_availability = (
        wall["availability"] +
        roof["availability"] +
        floor["availability"]
    ) / 3

    # Lower embodied carbon is better.
    carbon_score = max(
        0,
        min(
            100,
            70 - (avg_co2 * 100)
        )
    )

    availability_score = (
        avg_availability * 100
    )

    score = (
        carbon_score * 0.65 +
        availability_score * 0.35
    )

    return max(
        0,
        min(100, score)
    )


def calculate_comfort(
    indoor_temperatures: List[float],
    climate: Dict
) -> float:

    ideal_min = climate["ideal_min"]
    ideal_max = climate["ideal_max"]

    comfortable = 0

    for temp in indoor_temperatures:

        if ideal_min <= temp <= ideal_max:
            comfortable += 1

        else:
            distance = min(
                abs(temp - ideal_min),
                abs(temp - ideal_max)
            )

            if distance <= 2:
                comfortable += 0.5

    return (
        comfortable /
        len(indoor_temperatures)
    ) * 100


def calculate_stability(
    indoor_temperatures: List[float]
) -> float:

    minimum = min(indoor_temperatures)
    maximum = max(indoor_temperatures)

    variation = maximum - minimum

    score = 100 - (
        variation * 8
    )

    return max(
        0,
        min(100, score)
    )


def generate_hourly_profile(
    climate: Dict,
    avg_u: float,
    thermal_mass: float
):

    ambient = []
    indoor = []
    solar = []
    heat_loss = []

    base_temp = climate["base_temp"]
    amplitude = climate["temp_amplitude"]
    solar_peak = climate["solar_peak"]

    # Thermal damping factor
    damping = 1 / (
        1 + avg_u * 3
    )

    # Thermal mass effect
    mass_factor = min(
        0.85,
        thermal_mass / 500000
    )

    for hour in range(24):

        angle = (
            2 * math.pi *
            (hour - 8) /
            24
        )

        outdoor_temp = (
            base_temp +
            amplitude *
            math.sin(angle)
        )

        # Solar radiation during daytime
        solar_factor = max(
            0,
            math.sin(
                math.pi *
                (hour - 6) /
                12
            )
        )

        solar_gain = (
            solar_peak *
            solar_factor
        )

        # Indoor temperature
        target = (
            base_temp +
            amplitude *
            damping *
            math.sin(angle - 0.25)
        )

        # Thermal mass reduces rapid changes
        target = (
            target * (1 - mass_factor) +
            base_temp * mass_factor
        )

        # Small solar influence
        target += (
            solar_gain / 1000
        ) * (
            1 - damping
        )

        heat = abs(
            outdoor_temp - target
        ) * avg_u * 100

        ambient.append(
            round(outdoor_temp, 2)
        )

        indoor.append(
            round(target, 2)
        )

        solar.append(
            round(solar_gain, 2)
        )

        heat_loss.append(
            round(heat, 2)
        )

    return {
        "hours": list(range(24)),
        "ambient_temperature": ambient,
        "indoor_temperature": indoor,
        "solar_gain": solar,
        "heat_loss": heat_loss,
    }


# ============================================================
# MAIN SIMULATION ENGINE
# ============================================================

def simulate_design(
    request: DesignRequest
) -> Dict:

    wall = get_material(
        request.wall_material
    )

    roof = get_material(
        request.roof_material
    )

    floor = get_material(
        request.floor_material
    )

    if wall["type"] != "wall":
        raise HTTPException(
            status_code=400,
            detail="Selected wall material is not a wall material."
        )

    if roof["type"] != "roof":
        raise HTTPException(
            status_code=400,
            detail="Selected roof material is not a roof material."
        )

    if floor["type"] != "floor":
        raise HTTPException(
            status_code=400,
            detail="Selected floor material is not a floor material."
        )

    climate = get_climate(
        request.climate,
        request.location
    )

    areas = calculate_areas(
        request.dimensions,
        request.glazing_area
    )

    # --------------------------------------------------------
    # U VALUES
    # --------------------------------------------------------

    wall_u = calculate_u_value(
        request.wall_material,
        request.wall_thickness
    )

    roof_u = calculate_u_value(
        request.roof_material,
        request.roof_thickness
    )

    floor_u = calculate_u_value(
        request.floor_material,
        request.floor_thickness
    )

    # --------------------------------------------------------
    # THERMAL MASS
    # --------------------------------------------------------

    wall_mass = (
        areas["opaque_wall_area"] *
        request.wall_thickness *
        wall["density"] *
        wall["cp"]
    )

    roof_mass = (
        areas["roof_area"] *
        request.roof_thickness *
        roof["density"] *
        roof["cp"]
    )

    floor_mass = (
        areas["floor_area"] *
        request.floor_thickness *
        floor["density"] *
        floor["cp"]
    )

    thermal_mass = (
        wall_mass +
        roof_mass +
        floor_mass
    )

    # --------------------------------------------------------
    # WEIGHTED U VALUE
    # --------------------------------------------------------

    total_area = (
        areas["opaque_wall_area"] +
        areas["roof_area"] +
        areas["floor_area"]
    )

    avg_u = (
        wall_u * areas["opaque_wall_area"] +
        roof_u * areas["roof_area"] +
        floor_u * areas["floor_area"]
    ) / max(total_area, 1)

    # --------------------------------------------------------
    # 24 HOUR SIMULATION
    # --------------------------------------------------------

    profile = generate_hourly_profile(
        climate,
        avg_u,
        thermal_mass
    )

    indoor_temps = profile[
        "indoor_temperature"
    ]

    # --------------------------------------------------------
    # THERMAL SCORE
    # --------------------------------------------------------

    u_value_score = (
        100 /
        (1 + 0.75 * avg_u)
    )

    stability_score = calculate_stability(
        indoor_temps
    )

    thermal_score = (
        u_value_score * 0.75 +
        stability_score * 0.25
    )

    thermal_score = max(
        0,
        min(100, thermal_score)
    )

    # --------------------------------------------------------
    # COMFORT
    # --------------------------------------------------------

    comfort_score = calculate_comfort(
        indoor_temps,
        climate
    )

    # --------------------------------------------------------
    # COST
    # --------------------------------------------------------

    wall_cost = calculate_material_cost(
        request.wall_material,
        areas["opaque_wall_area"]
    )

    roof_cost = calculate_material_cost(
        request.roof_material,
        areas["roof_area"]
    )

    floor_cost = calculate_material_cost(
        request.floor_material,
        areas["floor_area"]
    )

    # Window/glazing allowance
    glazing_cost = (
        areas["glazing_area"] * 2500
    )

    estimated_cost = (
        wall_cost +
        roof_cost +
        floor_cost +
        glazing_cost
    )

    # Cost score
    budget = request.budget

    if estimated_cost <= budget:

        remaining = budget - estimated_cost

        cost_score = (
            100 -
            (
                estimated_cost /
                budget
            ) * 35
        )

        cost_score = max(
            65,
            min(100, cost_score)
        )

    else:

        over_budget = (
            estimated_cost - budget
        )

        cost_score = max(
            0,
            100 -
            (
                over_budget /
                budget
            ) * 100
        )

    # --------------------------------------------------------
    # SUSTAINABILITY
    # --------------------------------------------------------

    sustainability_score = calculate_sustainability(
        wall,
        roof,
        floor
    )

    # --------------------------------------------------------
    # AVAILABILITY
    # --------------------------------------------------------

    availability_score = (
        (
            wall["availability"] +
            roof["availability"] +
            floor["availability"]
        ) / 3
    ) * 100

    # --------------------------------------------------------
    # DURABILITY
    # --------------------------------------------------------

    durability_score = (
        (
            wall["durability"] +
            roof["durability"] +
            floor["durability"]
        ) / 3
    ) * 100

    # --------------------------------------------------------
    # OVERALL SCORE
    # --------------------------------------------------------

    overall_score = (
        thermal_score * 0.40 +
        comfort_score * 0.25 +
        cost_score * 0.15 +
        sustainability_score * 0.10 +
        availability_score * 0.10
    )

    overall_score = max(
        0,
        min(100, overall_score)
    )

    # --------------------------------------------------------
    # FEASIBILITY
    # --------------------------------------------------------

    within_budget = (
        estimated_cost <= budget
    )

    thermally_acceptable = (
        thermal_score >= 35
    )

    comfort_acceptable = (
        comfort_score >= 25
    )

    feasible = (
        within_budget and
        thermally_acceptable and
        comfort_acceptable
    )

    # --------------------------------------------------------
    # CO2
    # --------------------------------------------------------

    total_embodied_co2 = (
        wall["co2"] *
        areas["opaque_wall_area"] *
        request.wall_thickness *
        wall["density"]
        +
        roof["co2"] *
        areas["roof_area"] *
        request.roof_thickness *
        roof["density"]
        +
        floor["co2"] *
        areas["floor_area"] *
        request.floor_thickness *
        floor["density"]
    )

    # --------------------------------------------------------
    # REASONS
    # --------------------------------------------------------

    reasons = []

    if thermal_score >= 70:
        reasons.append(
            "Strong thermal insulation and temperature stability."
        )
    elif thermal_score >= 50:
        reasons.append(
            "Moderate thermal performance."
        )
    else:
        reasons.append(
            "Thermal performance can be improved with better insulation."
        )

    if comfort_score >= 70:
        reasons.append(
            "Indoor temperatures remain comfortable for most of the day."
        )
    elif comfort_score >= 40:
        reasons.append(
            "Indoor temperatures provide moderate thermal comfort."
        )
    else:
        reasons.append(
            "Indoor comfort is limited under the selected climate."
        )

    if sustainability_score >= 75:
        reasons.append(
            "Low-carbon and locally available materials improve sustainability."
        )
    elif sustainability_score >= 50:
        reasons.append(
            "The material combination provides moderate sustainability."
        )

    if estimated_cost <= budget:
        reasons.append(
            "The design remains within the specified budget."
        )
    else:
        reasons.append(
            "The design exceeds the specified budget."
        )

    return {

        "design": {
            "location": request.location,
            "climate": request.climate,
            "wall_material": request.wall_material,
            "roof_material": request.roof_material,
            "floor_material": request.floor_material,
            "wall_thickness": request.wall_thickness,
            "roof_thickness": request.roof_thickness,
            "floor_thickness": request.floor_thickness,
        },

        "dimensions": {
            "width": request.dimensions.width,
            "length": request.dimensions.length,
            "height": request.dimensions.height,
            "floor_area": round(
                areas["floor_area"],
                2
            ),
            "roof_area": round(
                areas["roof_area"],
                2
            ),
            "wall_area": round(
                areas["wall_area"],
                2
            ),
            "glazing_area": round(
                areas["glazing_area"],
                2
            ),
        },

        "u_values": {
            "wall": round(
                wall_u,
                4
            ),
            "roof": round(
                roof_u,
                4
            ),
            "floor": round(
                floor_u,
                4
            ),
            "average": round(
                avg_u,
                4
            ),
        },

        "scores": {
            "thermal": round(
                thermal_score,
                2
            ),
            "comfort": round(
                comfort_score,
                2
            ),
            "cost": round(
                cost_score,
                2
            ),
            "sustainability": round(
                sustainability_score,
                2
            ),
            "availability": round(
                availability_score,
                2
            ),
            "durability": round(
                durability_score,
                2
            ),
            "overall": round(
                overall_score,
                2
            ),
        },

        "cost": {
            "wall": round(
                wall_cost,
                2
            ),
            "roof": round(
                roof_cost,
                2
            ),
            "floor": round(
                floor_cost,
                2
            ),
            "glazing": round(
                glazing_cost,
                2
            ),
            "total": round(
                estimated_cost,
                2
            ),
            "budget": round(
                budget,
                2
            ),
            "remaining": round(
                budget - estimated_cost,
                2
            ),
        },

        "environment": {
            "embodied_co2": round(
                total_embodied_co2,
                2
            ),
            "sustainability_score": round(
                sustainability_score,
                2
            ),
        },

        "thermal_mass": round(
            thermal_mass,
            2
        ),

        "feasibility": {
            "feasible": feasible,
            "within_budget": within_budget,
            "thermal_acceptable": thermally_acceptable,
            "comfort_acceptable": comfort_acceptable,
        },

        "reasons": reasons,

        "simulation": profile,

        "climate": {
            "name": climate["name"],
            "base_temperature": climate["base_temp"],
            "temperature_amplitude": climate["temp_amplitude"],
            "solar_peak": climate["solar_peak"],
            "humidity": climate["humidity"],
            "ideal_min": climate["ideal_min"],
            "ideal_max": climate["ideal_max"],
        },
    }


# ============================================================
# OPTIMIZATION
# ============================================================

def optimization_score(
    result: Dict,
    budget: float
) -> float:

    scores = result["scores"]

    thermal = scores["thermal"]
    comfort = scores["comfort"]
    cost = scores["cost"]
    sustainability = scores["sustainability"]
    availability = scores["availability"]

    total_cost = result["cost"]["total"]

    # Base multi-objective score
    score = (
        thermal * 0.40 +
        comfort * 0.25 +
        cost * 0.15 +
        sustainability * 0.10 +
        availability * 0.10
    )

    # Strong penalties for poor thermal performance
    if thermal < 35:
        score -= (
            35 - thermal
        ) * 2.0

    if comfort < 25:
        score -= (
            25 - comfort
        ) * 1.5

    # Budget penalty
    if total_cost > budget:

        excess_ratio = (
            total_cost - budget
        ) / budget

        score -= (
            excess_ratio * 100
        )

    return score


def make_design_request(
    request: OptimizeRequest,
    wall: str,
    roof: str,
    floor: str
) -> DesignRequest:

    climate = request.climate

    if request.location in LOCATIONS:
        climate = LOCATIONS[
            request.location
        ]

    return DesignRequest(
        location=request.location,
        climate=climate,
        dimensions=request.dimensions,
        budget=request.budget,
        glazing_area=request.glazing_area,
        wall_material=wall,
        roof_material=roof,
        floor_material=floor,
        wall_thickness=request.wall_thickness,
        roof_thickness=request.roof_thickness,
        floor_thickness=request.floor_thickness,
    )


def optimize_design(
    request: OptimizeRequest
) -> Dict:

    all_designs = []

    # --------------------------------------------------------
    # Evaluate every possible combination
    # --------------------------------------------------------

    for wall in WALLS:

        for roof in ROOFS:

            for floor in FLOORS:

                design_request = make_design_request(
                    request,
                    wall,
                    roof,
                    floor
                )

                try:

                    result = simulate_design(
                        design_request
                    )

                    score = optimization_score(
                        result,
                        request.budget
                    )

                    result["_optimization_score"] = score

                    all_designs.append(
                        result
                    )

                except Exception:
                    continue

    if not all_designs:
        raise HTTPException(
            status_code=500,
            detail="No valid design combinations found."
        )

    # --------------------------------------------------------
    # Feasible designs
    # --------------------------------------------------------

    feasible_designs = [
        design
        for design in all_designs
        if design["feasibility"]["feasible"]
    ]

    # Sort feasible designs first
    feasible_designs.sort(
        key=lambda x: x["_optimization_score"],
        reverse=True
    )

    all_designs.sort(
        key=lambda x: x["_optimization_score"],
        reverse=True
    )

    if feasible_designs:

        recommended = feasible_designs[0]

        alternatives = feasible_designs[1:4]

        optimization_status = "feasible"

    else:

        # If no design meets every constraint,
        # select the strongest overall design.
        recommended = all_designs[0]

        alternatives = all_designs[1:4]

        optimization_status = (
            "best_available"
        )

    # --------------------------------------------------------
    # Clean private fields
    # --------------------------------------------------------

    def clean_design(design):

        cleaned = dict(design)

        cleaned.pop(
            "_optimization_score",
            None
        )

        return cleaned

    recommended = clean_design(
        recommended
    )

    alternatives = [
        clean_design(item)
        for item in alternatives
    ]

    # --------------------------------------------------------
    # Reasoning
    # --------------------------------------------------------

    reasons = []

    rec_scores = recommended["scores"]

    if rec_scores["thermal"] >= 70:

        reasons.append(
            "The selected material combination provides strong thermal resistance."
        )

    elif rec_scores["thermal"] >= 50:

        reasons.append(
            "The selected design provides moderate thermal performance."
        )

    else:

        reasons.append(
            "The optimizer selected the strongest available thermal configuration."
        )

    if rec_scores["comfort"] >= 70:

        reasons.append(
            "The simulated indoor temperature stays comfortable for most hours."
        )

    elif rec_scores["comfort"] >= 40:

        reasons.append(
            "The design achieves moderate thermal comfort."
        )

    else:

        reasons.append(
            "Thermal comfort remains challenging under the selected climate."
        )

    if recommended["cost"]["total"] <= request.budget:

        reasons.append(
            "The recommended design stays within the requested budget."
        )

    else:

        reasons.append(
            "No fully feasible design was found within the requested budget."
        )

    if rec_scores["sustainability"] >= 70:

        reasons.append(
            "The material combination provides a strong sustainability profile."
        )

    if rec_scores["availability"] >= 80:

        reasons.append(
            "The selected materials have relatively good availability."
        )

    # --------------------------------------------------------
    # Return
    # --------------------------------------------------------

    return {

        "optimization_status":
            optimization_status,

        "evaluated_designs":
            len(all_designs),

        "feasible_designs":
            len(feasible_designs),

        "recommended_design":
            recommended,

        "alternatives":
            alternatives,

        "reasoning":
            reasons,

        "weights": {
            "thermal": 0.40,
            "comfort": 0.25,
            "cost": 0.15,
            "sustainability": 0.10,
            "availability": 0.10,
        },

        "constraints": {
            "budget": request.budget,
            "minimum_thermal_score": 35,
            "minimum_comfort_score": 25,
        },

        "assumptions": [
            "Simplified steady-state U-value model.",
            "24-hour deterministic climate profile.",
            "Material prices are approximate estimates.",
            "Embodied carbon values are approximate.",
            "Actual performance depends on construction quality, ventilation, shading and local weather.",
        ],
    }


# ============================================================
# API ROUTES
# ============================================================

@app.get("/")
def root():

    return {
        "message": "AIKYAM backend is running",
        "version": app.version,
    }


# ------------------------------------------------------------
# MATERIALS
# ------------------------------------------------------------

@app.get("/materials")
def get_materials():

    return {
        "materials": MATERIALS
    }


# ------------------------------------------------------------
# CLIMATES
# ------------------------------------------------------------

@app.get("/climates")
def get_climates():

    return {
        "climates": CLIMATES
    }


# ------------------------------------------------------------
# LOCATIONS
# ------------------------------------------------------------

@app.get("/locations")
def get_locations():

    return {
        "locations": LOCATIONS
    }


# ------------------------------------------------------------
# U VALUE
# ------------------------------------------------------------

@app.get("/u-value")
def get_u_value(
    material: str,
    thickness: float
):

    if thickness <= 0:
        raise HTTPException(
            status_code=400,
            detail="Thickness must be greater than zero."
        )

    value = calculate_u_value(
        material,
        thickness
    )

    return {
        "material": material,
        "thickness": thickness,
        "u_value": round(value, 4),
    }


# ------------------------------------------------------------
# SIMULATE
# ------------------------------------------------------------

@app.post("/simulate")
def simulate(
    request: DesignRequest
):

    return simulate_design(
        request
    )


# ------------------------------------------------------------
# OPTIMIZE
# ------------------------------------------------------------

@app.post("/optimize")
def optimize(
    request: OptimizeRequest
):

    return optimize_design(
        request
    )


# ------------------------------------------------------------
# COMPARE
# ------------------------------------------------------------

@app.post("/compare")
def compare(
    request: CompareRequest
):

    current = simulate_design(
        request.current
    )

    optimized = simulate_design(
        request.optimized
    )

    current_scores = current["scores"]
    optimized_scores = optimized["scores"]

    current_cost = current["cost"]["total"]
    optimized_cost = optimized["cost"]["total"]

    return {

        "current": current,

        "optimized": optimized,

        "improvement": {

            "thermal": round(
                optimized_scores["thermal"] -
                current_scores["thermal"],
                2
            ),

            "comfort": round(
                optimized_scores["comfort"] -
                current_scores["comfort"],
                2
            ),

            "sustainability": round(
                optimized_scores["sustainability"] -
                current_scores["sustainability"],
                2
            ),

            "overall": round(
                optimized_scores["overall"] -
                current_scores["overall"],
                2
            ),

            "cost_difference": round(
                optimized_cost -
                current_cost,
                2
            ),
        },
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health():

    return {
        "status": "healthy",
        "service": "AIKYAM",
        "version": app.version,
    }