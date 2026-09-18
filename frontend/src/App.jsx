import { useEffect, useState } from "react";
import { getMaterials, simulate } from "./api";
import "./App.css";

function App() {
  const [materials, setMaterials] = useState({});
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const [form, setForm] = useState({
    climate: "cold",

    width: 4,
    length: 5,
    height: 2.5,

    wall_material: "Mud",
    roof_material: "Aerogel",
    floor_material: "Wood",

    wall_thickness: 0.25,
    roof_thickness: 0.12,
    floor_thickness: 0.10,

    glazing_area: 2
  });


  // Load materials from FastAPI
  useEffect(() => {
    getMaterials()
      .then((data) => {
        setMaterials(data.materials);
      })
      .catch((error) => {
        console.error(error);
      });
  }, []);


  // Handle input changes
  function handleChange(event) {
    const { name, value } = event.target;

    setForm((previous) => ({
      ...previous,
      [name]: value
    }));
  }


  // Run simulation
  async function handleSimulation() {
    setLoading(true);

    try {
      const data = {
        climate: form.climate,

        width: Number(form.width),
        length: Number(form.length),
        height: Number(form.height),

        wall_material: form.wall_material,
        roof_material: form.roof_material,
        floor_material: form.floor_material,

        wall_thickness: Number(form.wall_thickness),
        roof_thickness: Number(form.roof_thickness),
        floor_thickness: Number(form.floor_thickness),

        glazing_area: Number(form.glazing_area)
      };

      const response = await simulate(data);

      setResult(response);

    } catch (error) {
      console.error(error);
      alert("Simulation failed");
    }

    setLoading(false);
  }


  return (
    <div className="App">

      <h1>AIKYAM</h1>

      <p>
        Passive Shelter Thermal Design Prototype
      </p>


      {/* ================= CLIMATE ================= */}

      <h2>Climate</h2>

      <select
        name="climate"
        value={form.climate}
        onChange={handleChange}
      >
        <option value="cold">
          Cold / High Altitude
        </option>

        <option value="hot">
          Hot-Arid
        </option>

        <option value="temperate">
          Temperate
        </option>
      </select>


      {/* ================= GEOMETRY ================= */}

      <h2>Shelter Geometry</h2>

      <label>
        Width (m)
      </label>

      <input
        type="number"
        name="width"
        value={form.width}
        onChange={handleChange}
      />


      <br />

      <label>
        Length (m)
      </label>

      <input
        type="number"
        name="length"
        value={form.length}
        onChange={handleChange}
      />


      <br />

      <label>
        Height (m)
      </label>

      <input
        type="number"
        name="height"
        value={form.height}
        onChange={handleChange}
      />


      <br />

      <label>
        Glazing Area (m²)
      </label>

      <input
        type="number"
        name="glazing_area"
        value={form.glazing_area}
        onChange={handleChange}
      />


      {/* ================= MATERIALS ================= */}

      <h2>Materials</h2>


      <label>
        Wall Material
      </label>

      <select
        name="wall_material"
        value={form.wall_material}
        onChange={handleChange}
      >

        {Object.keys(materials).map((material) => (
          <option
            key={material}
            value={material}
          >
            {material}
          </option>
        ))}

      </select>


      <br />
      <br />


      <label>
        Roof Material
      </label>

      <select
        name="roof_material"
        value={form.roof_material}
        onChange={handleChange}
      >

        {Object.keys(materials).map((material) => (
          <option
            key={material}
            value={material}
          >
            {material}
          </option>
        ))}

      </select>


      <br />
      <br />


      <label>
        Floor Material
      </label>

      <select
        name="floor_material"
        value={form.floor_material}
        onChange={handleChange}
      >

        {Object.keys(materials).map((material) => (
          <option
            key={material}
            value={material}
          >
            {material}
          </option>
        ))}

      </select>


      {/* ================= THICKNESS ================= */}

      <h2>Material Thickness</h2>


      <label>
        Wall Thickness (m)
      </label>

      <input
        type="number"
        step="0.01"
        name="wall_thickness"
        value={form.wall_thickness}
        onChange={handleChange}
      />


      <br />


      <label>
        Roof Thickness (m)
      </label>

      <input
        type="number"
        step="0.01"
        name="roof_thickness"
        value={form.roof_thickness}
        onChange={handleChange}
      />


      <br />


      <label>
        Floor Thickness (m)
      </label>

      <input
        type="number"
        step="0.01"
        name="floor_thickness"
        value={form.floor_thickness}
        onChange={handleChange}
      />


      {/* ================= SIMULATION ================= */}

      <br />
      <br />

      <button
        onClick={handleSimulation}
        disabled={loading}
      >

        {loading
          ? "Running Simulation..."
          : "Run Thermal Simulation"}

      </button>


      {/* ================= RESULTS ================= */}

      {result && (

        <div>

          <h2>Simulation Results</h2>


          <h3>U-Values</h3>

          <p>
            Wall U-value:
            {" "}
            {result.wall_u?.toFixed(3)}
            {" "}
            W/m²K
          </p>

          <p>
            Roof U-value:
            {" "}
            {result.roof_u?.toFixed(3)}
            {" "}
            W/m²K
          </p>

          <p>
            Floor U-value:
            {" "}
            {result.floor_u?.toFixed(3)}
            {" "}
            W/m²K
          </p>

          <p>
            Average U-value:
            {" "}
            {result.average_u?.toFixed(3)}
            {" "}
            W/m²K
          </p>


          <h3>24 Hour Temperature</h3>

          <p>
            Ambient:
            {" "}
            {result.ambient?.join(", ")}
          </p>

          <p>
            Indoor:
            {" "}
            {result.indoor?.join(", ")}
          </p>


          <h3>Solar Gain</h3>

          <p>
            {result.solar?.join(", ")}
          </p>

        </div>

      )}

    </div>
  );
}

export default App;