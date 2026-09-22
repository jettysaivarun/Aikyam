import { useEffect, useMemo, useState } from "react";

import {
  Activity,
  ArrowRight,
  CheckCircle2,
  Download,
  Home,
  Leaf,
  Loader2,
  MapPin,
  RefreshCw,
  ShieldCheck,
  Sparkles,
  Thermometer,
  Wallet,
  Zap,
} from "lucide-react";

import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import {
  compare,
  getClimates,
  getLocations,
  getMaterials,
  optimize,
  simulate,
} from "./api";

import "./App.css";


/* =========================================================
   INITIAL FORM
========================================================= */

const initialForm = {
  location: "Leh",
  climate: "cold",

  width: 4,
  length: 5,
  height: 2.5,

  budget: 50000,

  glazing_area: 2,

  wall_material: "Mud",
  roof_material: "Aerogel",
  floor_material: "Wood",

  wall_thickness: 0.25,
  roof_thickness: 0.12,
  floor_thickness: 0.10,
};


/* =========================================================
   HELPERS
========================================================= */

const money = (value) =>
  `₹${Math.round(value || 0).toLocaleString("en-IN")}`;

const pct = (value) =>
  `${value > 0 ? "+" : ""}${Number(value || 0).toFixed(1)}%`;


/* =========================================================
   METRIC CARD
========================================================= */

function Metric({
  icon: Icon,
  label,
  value,
  sub,
}) {
  return (
    <div className="metric-card">

      <div className="metric-icon">
        <Icon size={18} />
      </div>

      <div>
        <span>{label}</span>

        <strong>{value}</strong>

        {sub && (
          <small>{sub}</small>
        )}
      </div>

    </div>
  );
}


/* =========================================================
   DESIGN CARD
========================================================= */

function DesignCard({
  design,
  recommended = false,
  onUse,
}) {

  const feasible = design.feasible;

  return (
    <article
      className={`design-card ${
        recommended ? "recommended" : ""
      }`}
    >

      {recommended && (
        <div className="recommend-badge">
          <Sparkles size={13} />
          AIKYAM optimized design
        </div>
      )}

      <div className="design-title">

        <div>

          <span>
            Design configuration
          </span>

          <h3>
            {design.materials.wall}
            {" + "}
            {design.materials.roof}
            {" + "}
            {design.materials.floor}
          </h3>

        </div>

        <div className="score">

          <b>
            {design.overall_score}
          </b>

          <small>
            /100
          </small>

        </div>

      </div>


      <div className="material-pills">

        <span>
          Wall · {design.materials.wall}
        </span>

        <span>
          Roof · {design.materials.roof}
        </span>

        <span>
          Floor · {design.materials.floor}
        </span>

      </div>


      <div className="mini-grid">

        <div>
          <small>Thermal</small>
          <b>
            {design.thermal_score}
          </b>
        </div>

        <div>
          <small>Comfort</small>
          <b>
            {design.comfort_score}%
          </b>
        </div>

        <div>
          <small>Sustainability</small>
          <b>
            {design.sustainability_score}
          </b>
        </div>

        <div>
          <small>Cost</small>
          <b>
            {money(design.cost)}
          </b>
        </div>

      </div>


      <div
        className={`feasibility ${
          feasible
            ? "feasible"
            : "fallback"
        }`}
      >

        {feasible ? (
          <>
            <CheckCircle2 size={15} />
            Feasible within selected constraints
          </>
        ) : (
          <>
            <ShieldCheck size={15} />
            Fallback configuration
          </>
        )}

      </div>


      {onUse && (
        <button
          className="secondary-btn"
          onClick={() =>
            onUse(design)
          }
        >
          <RefreshCw size={15} />
          Use this design
        </button>
      )}

    </article>
  );
}


/* =========================================================
   MAIN APP
========================================================= */

function App() {

  const [materials, setMaterials] =
    useState({});

  const [groups, setGroups] =
    useState({
      walls: [],
      roofs: [],
      floors: [],
    });

  const [climates, setClimates] =
    useState({});

  const [locations, setLocations] =
    useState({});

  const [form, setForm] =
    useState(initialForm);

  const [result, setResult] =
    useState(null);

  const [simulation, setSimulation] =
    useState(null);

  const [comparison, setComparison] =
    useState(null);

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState("");


  /* =======================================================
     LOAD INITIAL DATA
  ======================================================= */

  useEffect(() => {

    Promise.all([
      getMaterials(),
      getClimates(),
      getLocations(),
    ])

      .then(
        ([
          materialData,
          climateData,
          locationData,
        ]) => {

          setMaterials(
            materialData.materials
          );

          setGroups({
            walls: materialData.walls,
            roofs: materialData.roofs,
            floors: materialData.floors,
          });

          setClimates(
            climateData.climates
          );

          setLocations(
            locationData.locations
          );
        }
      )

      .catch((e) => {
        setError(e.message);
      });

  }, []);


  /* =======================================================
     CHART DATA
  ======================================================= */

  const chartData = useMemo(() => {

    if (
      !simulation?.simulation?.hours
    ) {
      return [];
    }

    return simulation.simulation.hours.map(
      (hour, index) => ({
        hour,

        ambient:
          simulation.simulation
            .ambient[index],

        indoor:
          simulation.simulation
            .indoor[index],

        solar:
          simulation.simulation
            .solar[index],

        heatLoss:
          simulation.simulation
            .heat_loss[index],
      })
    );

  }, [simulation]);


  /* =======================================================
     FORM UPDATE
  ======================================================= */

  function update(
    name,
    value,
  ) {

    setForm((current) => {

      const next = {
        ...current,
        [name]: value,
      };

      if (
        name === "location"
        && locations[value]
      ) {

        next.location = value;

        next.climate =
          locations[value];
      }

      return next;
    });
  }


  /* =======================================================
     BUILD API PAYLOAD
  ======================================================= */

  function payload(
    overrides = {},
  ) {

    const current = {
      ...form,
      ...overrides,
    };

    return {

      climate:
        current.climate,

      location:
        current.location,

      budget:
        Number(current.budget),

      glazing_area:
        Number(
          current.glazing_area
        ),

      dimensions: {

        width:
          Number(current.width),

        length:
          Number(current.length),

        height:
          Number(current.height),

      },

      wall_material:
        current.wall_material,

      roof_material:
        current.roof_material,

      floor_material:
        current.floor_material,

      wall_thickness:
        Number(
          current.wall_thickness
        ),

      roof_thickness:
        Number(
          current.roof_thickness
        ),

      floor_thickness:
        Number(
          current.floor_thickness
        ),
    };
  }


  /* =======================================================
     OPTIMIZATION
  ======================================================= */

  async function runOptimization() {

    setLoading(true);
    setError("");
    setComparison(null);

    try {

      const optimized =
        await optimize(
          payload()
        );

      setResult(
        optimized
      );

      setSimulation(
        optimized.recommended_design
      );


      const recommended =
        optimized.recommended_design;


      const optimizedPayload =
        payload({
          wall_material:
            recommended.materials.wall,

          roof_material:
            recommended.materials.roof,

          floor_material:
            recommended.materials.floor,
        });


      const cmp =
        await compare({
          current:
            payload(),

          optimized:
            optimizedPayload,
        });


      setComparison(
        cmp
      );

    } catch (e) {

      setError(
        e.message
      );

    } finally {

      setLoading(false);

    }
  }


  /* =======================================================
     CURRENT DESIGN SIMULATION
  ======================================================= */

  async function runSimulation() {

    setLoading(true);
    setError("");

    try {

      const simulationResult =
        await simulate(
          payload()
        );

      setSimulation(
        simulationResult
      );

      setResult(null);
      setComparison(null);

    } catch (e) {

      setError(
        e.message
      );

    } finally {

      setLoading(false);

    }
  }


  /* =======================================================
     USE RECOMMENDED DESIGN
  ======================================================= */

  function useDesign(
    design,
  ) {

    setForm(
      (current) => ({
        ...current,

        wall_material:
          design.materials.wall,

        roof_material:
          design.materials.roof,

        floor_material:
          design.materials.floor,
      })
    );

    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  }


  /* =======================================================
     PRINT REPORT
  ======================================================= */

  function printReport() {

    window.print();

  }


  const recommended =
    result?.recommended_design;


  const budget =
    Number(form.budget);


  const budgetDifference =
    recommended
      ? budget - recommended.cost
      : 0;


  /* =======================================================
     RENDER
  ======================================================= */

  return (

    <div className="app-shell">

      {/* ===================================================
          HEADER
      =================================================== */}

      <header className="topbar">

        <div className="brand">

          <div className="brand-mark">
            <Home size={21} />
          </div>

          <div>
            <b>AIKYAM</b>

            <span>
              Passive Shelter Intelligence
            </span>
          </div>

        </div>


        <div className="status">

          <span className="dot" />

          Optimization engine online

        </div>

      </header>


      <main>

        {/* =================================================
            HERO
        ================================================= */}

        <section className="hero">

          <div className="eyebrow">

            <Sparkles size={14} />

            CLIMATE-AWARE DESIGN ENGINE

          </div>


          <h1>

            Design a shelter that
            <br />

            <em>
              works with its climate.
            </em>

          </h1>


          <p>

            AIKYAM evaluates thermal
            performance, cost, comfort and
            sustainability across multiple
            material configurations to find
            feasible passive-shelter designs.

          </p>

        </section>


        {/* =================================================
            ERROR
        ================================================= */}

        {error && (

          <div className="error">

            <ShieldCheck size={17} />

            {error}

          </div>

        )}


        {/* =================================================
            WORKSPACE
        ================================================= */}

        <section className="workspace">


          {/* ===============================================
              LEFT CONTROL PANEL
          =============================================== */}

          <aside className="control-panel">

            <div className="panel-heading">

              <span>
                01 / DESIGN INPUT
              </span>

              <h2>
                Define your shelter
              </h2>

            </div>


            {/* LOCATION */}

            <div className="field">

              <label>

                <MapPin size={14} />

                Location

              </label>

              <select
                value={form.location}
                onChange={(e) =>
                  update(
                    "location",
                    e.target.value
                  )
                }
              >

                {Object.keys(
                  locations
                ).map((location) => (

                  <option
                    key={location}
                    value={location}
                  >
                    {location}
                  </option>

                ))}

              </select>

            </div>


            {/* CLIMATE */}

            <div className="field">

              <label>
                Climate
              </label>

              <select
                value={form.climate}
                onChange={(e) =>
                  update(
                    "climate",
                    e.target.value
                  )
                }
              >

                {Object.entries(
                  climates
                ).map(
                  ([key, climate]) => (

                    <option
                      key={key}
                      value={key}
                    >
                      {climate.name}
                    </option>

                  )
                )}

              </select>

            </div>


            {/* DIMENSIONS */}

            <div className="field-grid">

              <div className="field">

                <label>
                  Width <small>m</small>
                </label>

                <input
                  type="number"
                  min="0.5"
                  step="0.1"
                  value={form.width}
                  onChange={(e) =>
                    update(
                      "width",
                      e.target.value
                    )
                  }
                />

              </div>


              <div className="field">

                <label>
                  Length <small>m</small>
                </label>

                <input
                  type="number"
                  min="0.5"
                  step="0.1"
                  value={form.length}
                  onChange={(e) =>
                    update(
                      "length",
                      e.target.value
                    )
                  }
                />

              </div>


              <div className="field">

                <label>
                  Height <small>m</small>
                </label>

                <input
                  type="number"
                  min="0.5"
                  step="0.1"
                  value={form.height}
                  onChange={(e) =>
                    update(
                      "height",
                      e.target.value
                    )
                  }
                />

              </div>


              <div className="field">

                <label>
                  Glazing <small>m²</small>
                </label>

                <input
                  type="number"
                  min="0"
                  step="0.5"
                  value={
                    form.glazing_area
                  }
                  onChange={(e) =>
                    update(
                      "glazing_area",
                      e.target.value
                    )
                  }
                />

              </div>

            </div>


            {/* BUDGET */}

            <div className="budget-box">

              <Wallet size={18} />

              <div>

                <label>
                  Design budget
                </label>

                <input
                  type="number"
                  min="10000"
                  max="500000"
                  step="1000"
                  value={form.budget}
                  onChange={(e) => {

                    const value =
                      Number(
                        e.target.value
                      );

                    if (
                      value >= 0
                      &&
                      value <= 500000
                    ) {

                      update(
                        "budget",
                        value
                      );

                    }

                  }}
                />

              </div>

              <span>
                INR
              </span>

            </div>


            <div className="budget-hint">

              <span>
                Recommended prototype range
              </span>

              <strong>
                ₹10,000 – ₹5,00,000
              </strong>

            </div>


            {/* MATERIALS */}

            <div className="panel-heading compact">

              <span>
                02 / MATERIALS
              </span>

              <h2>
                Choose constraints
              </h2>

            </div>


            {[
              [
                "wall_material",
                "Wall",
                groups.walls,
              ],

              [
                "roof_material",
                "Roof",
                groups.roofs,
              ],

              [
                "floor_material",
                "Floor",
                groups.floors,
              ],

            ].map(
              ([
                name,
                label,
                options,
              ]) => (

                <div
                  className="field"
                  key={name}
                >

                  <label>
                    {label} material
                  </label>

                  <select
                    value={form[name]}
                    onChange={(e) =>
                      update(
                        name,
                        e.target.value
                      )
                    }
                  >

                    {options.map(
                      (option) => (

                        <option
                          key={option}
                          value={option}
                        >
                          {option}
                        </option>

                      )
                    )}

                  </select>

                </div>

              )
            )}


            {/* OPTIMIZE */}

            <button
              className="primary-btn"
              onClick={
                runOptimization
              }
              disabled={loading}
            >

              {loading ? (

                <>
                  <Loader2
                    className="spin"
                    size={18}
                  />

                  Evaluating designs…

                </>

              ) : (

                <>
                  <Sparkles size={18} />

                  Optimize my shelter

                  <ArrowRight
                    size={17}
                  />

                </>

              )}

            </button>


            {/* SIMULATE */}

            <button
              className="ghost-btn"
              onClick={
                runSimulation
              }
              disabled={loading}
            >

              <Activity size={16} />

              Simulate current design

            </button>

          </aside>


          {/* ===============================================
              RESULTS
          =============================================== */}

          <section className="results">


            {/* EMPTY */}

            {!result &&
              !simulation && (

                <div className="empty-state">

                  <div className="empty-icon">

                    <Home size={34} />

                  </div>

                  <h2>
                    Your design workspace
                  </h2>

                  <p>

                    Enter your shelter
                    parameters and run the
                    optimization engine.
                    AIKYAM will evaluate
                    material combinations
                    and show thermal
                    trade-offs.

                  </p>


                  <div className="flow">

                    <span>
                      Inputs
                    </span>

                    <ArrowRight />

                    <span>
                      Simulation
                    </span>

                    <ArrowRight />

                    <span>
                      Optimization
                    </span>

                    <ArrowRight />

                    <span>
                      Design
                    </span>

                  </div>

                </div>

              )}


            {/* =============================================
                OPTIMIZATION RESULT
            ============================================= */}

            {result && recommended && (

              <>

                <div className="result-header">

                  <div>

                    <div className="eyebrow">

                      OPTIMIZATION COMPLETE ·{" "}

                      {result.evaluated_designs}

                      {" "}CONFIGURATIONS

                    </div>

                    <h2>
                      Recommended shelter system
                    </h2>

                  </div>


                  <button
                    className="report-btn"
                    onClick={
                      printReport
                    }
                  >

                    <Download size={16} />

                    Design report

                  </button>

                </div>


                {/* STATUS */}

                <div
                  className={`optimization-status ${
                    result.optimization_status ===
                    "feasible"
                      ? "status-good"
                      : "status-warning"
                  }`}
                >

                  {result.optimization_status ===
                  "feasible" ? (

                    <>
                      <CheckCircle2
                        size={16}
                      />

                      {result.feasible_designs}
                      {" "}feasible designs found
                    </>

                  ) : (

                    <>
                      <ShieldCheck
                        size={16}
                      />

                      No design satisfied every
                      constraint. Showing the
                      strongest fallback.
                    </>

                  )}

                </div>


                {/* METRICS */}

                <div className="metrics">

                  <Metric
                    icon={Zap}
                    label="Overall performance"
                    value={`${recommended.overall_score}/100`}
                    sub="multi-objective score"
                  />


                  <Metric
                    icon={Thermometer}
                    label="Thermal"
                    value={`${recommended.thermal_score}/100`}
                    sub={`${recommended.comfort_hours} comfortable hours`}
                  />


                  <Metric
                    icon={Leaf}
                    label="Sustainability"
                    value={`${recommended.sustainability_score}/100`}
                    sub={`${Math.round(recommended.embodied_co2)} kg CO₂e estimate`}
                  />


                  <Metric
                    icon={Wallet}
                    label="Estimated cost"
                    value={money(recommended.cost)}
                    sub={
                      recommended.cost <=
                      budget
                        ? `${money(
                            budgetDifference
                          )} remaining`
                        : `${money(
                            Math.abs(
                              budgetDifference
                            )
                          )} over budget`
                    }
                  />

                </div>


                {/* RECOMMENDED DESIGN */}

                <DesignCard
                  design={
                    recommended
                  }
                  recommended
                  onUse={
                    useDesign
                  }
                />


                {/* WHY */}

                <div className="reason-card">

                  <h3>
                    Why AIKYAM selected this
                  </h3>

                  <div className="reasons">

                    {result.reasoning.map(
                      (reason, index) => (

                        <div
                          key={index}
                        >

                          <CheckCircle2
                            size={16}
                          />

                          <span>
                            {reason}
                          </span>

                        </div>

                      )
                    )}

                  </div>

                </div>


                {/* ALTERNATIVES */}

                <div className="section-title">

                  <span>
                    ALTERNATIVES
                  </span>

                  <h3>
                    Other feasible configurations
                  </h3>

                </div>


                <div className="alternatives">

                  {result.alternatives.map(
                    (design, index) => (

                      <DesignCard
                        key={index}
                        design={design}
                        onUse={
                          useDesign
                        }
                      />

                    )
                  )}

                </div>

              </>

            )}


            {/* =============================================
                THERMAL SIMULATION
            ============================================= */}

            {simulation && (

              <>

                <div className="section-title">

                  <span>
                    THERMAL SIMULATION
                  </span>

                  <h3>
                    24-hour performance profile
                  </h3>

                </div>


                {/* TEMPERATURE */}

                <div className="chart-card">

                  <div className="chart-head">

                    <div>

                      <b>
                        Indoor vs ambient temperature
                      </b>

                      <small>
                        Deterministic prototype thermal model
                      </small>

                    </div>


                    <div className="legend">

                      <span className="indoor-dot" />

                      Indoor

                      <span className="ambient-dot" />

                      Ambient

                    </div>

                  </div>


                  <div className="chart">

                    <ResponsiveContainer
                      width="100%"
                      height={280}
                    >

                      <LineChart
                        data={chartData}
                      >

                        <CartesianGrid
                          strokeDasharray="3 3"
                          stroke="rgba(255,255,255,.06)"
                        />

                        <XAxis
                          dataKey="hour"
                          stroke="#6d7788"
                          tickLine={false}
                        />

                        <YAxis
                          stroke="#6d7788"
                          tickLine={false}
                        />

                        <Tooltip
                          contentStyle={{
                            background:
                              "#101722",
                            border:
                              "1px solid rgba(255,255,255,.1)",
                            borderRadius: 10,
                          }}
                        />

                        <Line
                          type="monotone"
                          dataKey="indoor"
                          stroke="#56e0c2"
                          strokeWidth={3}
                          dot={false}
                          name="Indoor"
                        />

                        <Line
                          type="monotone"
                          dataKey="ambient"
                          stroke="#ff9d62"
                          strokeWidth={2}
                          dot={false}
                          name="Ambient"
                        />

                      </LineChart>

                    </ResponsiveContainer>

                  </div>

                </div>


                {/* SOLAR */}

                <div className="chart-card">

                  <div className="chart-head">

                    <div>

                      <b>
                        Solar gain
                      </b>

                      <small>
                        Estimated hourly solar contribution
                      </small>

                    </div>

                  </div>


                  <div className="chart">

                    <ResponsiveContainer
                      width="100%"
                      height={230}
                    >

                      <LineChart
                        data={chartData}
                      >

                        <CartesianGrid
                          strokeDasharray="3 3"
                          stroke="rgba(255,255,255,.06)"
                        />

                        <XAxis
                          dataKey="hour"
                          stroke="#6d7788"
                          tickLine={false}
                        />

                        <YAxis
                          stroke="#6d7788"
                          tickLine={false}
                        />

                        <Tooltip
                          contentStyle={{
                            background:
                              "#101722",
                            border:
                              "1px solid rgba(255,255,255,.1)",
                            borderRadius: 10,
                          }}
                        />

                        <Line
                          type="monotone"
                          dataKey="solar"
                          stroke="#ffb35c"
                          strokeWidth={3}
                          dot={false}
                          name="Solar gain"
                        />

                      </LineChart>

                    </ResponsiveContainer>

                  </div>

                </div>


                {/* U VALUES */}

                <div className="u-grid">

                  <div>

                    <span>
                      Wall U-value
                    </span>

                    <b>
                      {simulation.wall_u}
                    </b>

                    <small>
                      W/m²K
                    </small>

                  </div>


                  <div>

                    <span>
                      Roof U-value
                    </span>

                    <b>
                      {simulation.roof_u}
                    </b>

                    <small>
                      W/m²K
                    </small>

                  </div>


                  <div>

                    <span>
                      Floor U-value
                    </span>

                    <b>
                      {simulation.floor_u}
                    </b>

                    <small>
                      W/m²K
                    </small>

                  </div>


                  <div>

                    <span>
                      Avg. envelope U
                    </span>

                    <b>
                      {simulation.average_u}
                    </b>

                    <small>
                      W/m²K
                    </small>

                  </div>

                </div>

              </>

            )}


            {/* =============================================
                COMPARISON
            ============================================= */}

            {comparison && (

              <section className="compare-section">

                <div className="section-title">

                  <span>
                    DESIGN COMPARISON
                  </span>

                  <h3>
                    Current vs AIKYAM optimized
                  </h3>

                </div>


                <div className="compare-table">

                  <div className="compare-head">

                    <span>
                      Metric
                    </span>

                    <b>
                      Current
                    </b>

                    <b>
                      Optimized
                    </b>

                    <span>
                      Change
                    </span>

                  </div>


                  {[
                    [
                      "thermal_score",
                      "Thermal score",
                      "",
                    ],

                    [
                      "comfort_score",
                      "Comfort score",
                      "%",
                    ],

                    [
                      "cost",
                      "Estimated cost",
                      "money",
                    ],

                    [
                      "heat_loss_peak",
                      "Peak heat loss",
                      "",
                    ],

                    [
                      "sustainability_score",
                      "Sustainability",
                      "",
                    ],

                    [
                      "average_u",
                      "Average U-value",
                      "",
                    ],

                  ].map(
                    ([
                      key,
                      label,
                      type,
                    ]) => (

                      <div
                        className="compare-row"
                        key={key}
                      >

                        <span>
                          {label}
                        </span>


                        <b>

                          {type === "money"
                            ? money(
                                comparison
                                  .current[
                                    key
                                  ]
                              )
                            : `${comparison.current[key]}${type}`}

                        </b>


                        <b>

                          {type === "money"
                            ? money(
                                comparison
                                  .optimized[
                                    key
                                  ]
                              )
                            : `${comparison.optimized[key]}${type}`}

                        </b>


                        <strong>

                          {pct(
                            comparison
                              .improvements[
                                key
                              ]
                          )}

                        </strong>

                      </div>

                    )
                  )}

                </div>

              </section>

            )}


            {/* =============================================
                ASSUMPTIONS
            ============================================= */}

            {(result || simulation) && (

              <div className="assumptions">

                <ShieldCheck size={17} />

                <div>

                  <b>
                    Prototype model assumptions
                  </b>

                  <p>

                    Material properties, costs
                    and sustainability values are
                    reference assumptions.
                    Thermal behavior is a
                    simplified 24-hour simulation
                    intended for design exploration,
                    not certified architectural or
                    engineering analysis.

                  </p>

                </div>

              </div>

            )}

          </section>

        </section>

      </main>


      <footer>

        <span>
          AIKYAM · SIH Prototype
        </span>

        <span>
          Climate-aware · Cost-aware ·
          Sustainability-aware
        </span>

      </footer>

    </div>
  );
}


export default App;