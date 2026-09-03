import './App.css'
import { useState } from "react";
import MapView from "./components/MapView";
function App() {
  const [routeSegments, setRouteSegments] = useState<
  {
    id: string;
    coordinates: { lat: number; lng: number }[];
    risk_score: number;
    blocked: boolean;
  }[]
>([]);

const [isPlanning, setIsPlanning] = useState(false);
const [routeError, setRouteError] = useState("");
const handlePlanRoute = async () => {
  setIsPlanning(true);
  setRouteError("");

  try {
    const response = await fetch(
      "http://127.0.0.1:8000/api/routes/calculate",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          vehicle_id: "V001",
          destination: "E",
        }),
      }
    );

    if (!response.ok) {
      throw new Error(`Route request failed: ${response.status}`);
    }

    const data = await response.json();

    setRouteSegments(data.segments ?? []);
  } catch (error) {
    console.error(error);
    setRouteError("Unable to calculate route.");
  } finally {
    setIsPlanning(false);
  }
};
  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">V</div>
          <div>
            <h1>VECTRA</h1>
            <span>Operations</span>
          </div>
        </div>

        <nav className="nav">
          <button className="nav-item active">Overview</button>
          <button className="nav-item">Route Planner</button>
          <button className="nav-item">Live Tracking</button>
          <button className="nav-item">Incidents</button>
          <button className="nav-item">Alerts</button>
          <button className="nav-item">Analytics</button>
        </nav>

        <div className="sidebar-footer">
          <div className="status-dot" />
          <span>System Operational</span>
        </div>
      </aside>

      <main className="main">
        <header className="topbar">
          <div>
            <p className="eyebrow">TRANSPORT OPERATIONS</p>
            <h2>Command Center</h2>
          </div>

          <div className="topbar-actions">
            <select defaultValue="North East Region">
              <option>North East Region</option>
            </select>

            <select defaultValue="All Districts">
              <option>All Districts</option>
            </select>

            <button className="icon-button">🔔</button>

            <div className="user">
              <div className="avatar">K</div>
              <div>
                <strong>Operator</strong>
                <span>Operations Admin</span>
              </div>
            </div>
          </div>
        </header>

        <section className="content">
          <div className="stats-row">
            <div className="stat-card">
              <span>Active Vehicles</span>
              <strong>18</strong>
              <small>2 delayed</small>
            </div>

            <div className="stat-card">
              <span>Active Incidents</span>
              <strong>07</strong>
              <small>3 high priority</small>
            </div>

            <div className="stat-card">
              <span>High-Risk Corridors</span>
              <strong>04</strong>
              <small>Needs attention</small>
            </div>

            <div className="stat-card">
              <span>Deliveries Today</span>
              <strong>126</strong>
              <small>91% on schedule</small>
            </div>
          </div>

          <div className="dashboard-grid">
            <section className="panel map-panel">
              <div className="panel-header">
                <div>
                  <span className="panel-label">LIVE GIS</span>
                  <h3>Network Overview</h3>
                </div>

                <div className="map-legend">
                  <span><i className="legend safe" /> Safe</span>
                  <span><i className="legend moderate" /> Moderate</span>
                  <span><i className="legend high" /> High Risk</span>
                </div>
              </div>

           <div className="map-placeholder">
  <MapView routeSegments={routeSegments} />
</div>
            </section>

            <section className="panel planner-panel">
              <div className="panel-header">
                <div>
                  <span className="panel-label">TRIP PLANNER</span>
                  <h3>Plan New Trip</h3>
                </div>
              </div>

              <div className="form-group">
                <label>Origin</label>
                <input defaultValue="Guwahati, Assam" />
              </div>

              <div className="form-group">
                <label>Destination</label>
                <input defaultValue="Kohima, Nagaland" />
              </div>

              <div className="form-group">
                <label>Planned Departure</label>
                <input type="datetime-local" />
              </div>

              <button
  className="primary-button"
  onClick={handlePlanRoute}
  disabled={isPlanning}
>
  {isPlanning ? "Planning..." : "Plan Route"}
</button>

{routeError && (
  <p className="route-error">
    {routeError}
  </p>
)}

              <div className="recommendation">
                <span>RECOMMENDED ACTION</span>
                <h4>Monitor NH-13 before dispatch</h4>
                <p>
                  Current conditions indicate elevated landslide risk
                  along one corridor.
                </p>
              </div>
            </section>
          </div>

          <div className="bottom-grid">
            <section className="panel">
              <div className="panel-header">
                <div>
                  <span className="panel-label">ROUTE OPTIONS</span>
                  <h3>Route Comparison</h3>
                </div>
              </div>

              <div className="route-cards">
                <div className="route-card recommended">
                  <div>
                    <span>ROUTE A</span>
                    <strong>Recommended</strong>
                  </div>
                  <h4>6h 45m</h4>
                  <p>265 km · Low Risk</p>
                </div>

                <div className="route-card">
                  <div>
                    <span>ROUTE B</span>
                    <strong>Moderate Risk</strong>
                  </div>
                  <h4>7h 30m</h4>
                  <p>298 km · Flood warning</p>
                </div>

                <div className="route-card danger">
                  <div>
                    <span>ROUTE C</span>
                    <strong>High Risk</strong>
                  </div>
                  <h4>8h 10m</h4>
                  <p>310 km · Landslide risk</p>
                </div>
              </div>
            </section>

            <section className="panel">
              <div className="panel-header">
                <div>
                  <span className="panel-label">LIVE FLEET</span>
                  <h3>Vehicle Status</h3>
                </div>
              </div>

              <div className="vehicle-list">
                <div className="vehicle-row">
                  <span>AS01 AB 1234</span>
                  <span className="vehicle-route">Guw → Koh</span>
                  <span className="pill safe-pill">On Route</span>
                </div>

                <div className="vehicle-row">
                  <span>NL07 CD 5678</span>
                  <span className="vehicle-route">Dim → Koh</span>
                  <span className="pill safe-pill">On Route</span>
                </div>

                <div className="vehicle-row">
                  <span>MN01 EF 9012</span>
                  <span className="vehicle-route">Imp → Guw</span>
                  <span className="pill danger-pill">Delayed</span>
                </div>
              </div>
            </section>
          </div>

          <div className="bottom-grid">
            <section className="panel">
              <div className="panel-header">
                <div>
                  <span className="panel-label">ALERT FEED</span>
                  <h3>Operational Alerts</h3>
                </div>
              </div>

              <div className="alert-list">
                <div className="alert-item">
                  <span className="alert-icon danger-icon">!</span>
                  <div>
                    <strong>High Risk Corridor</strong>
                    <p>Landslide activity reported near NH-13.</p>
                  </div>
                </div>

                <div className="alert-item">
                  <span className="alert-icon warning-icon">!</span>
                  <div>
                    <strong>Route Degradation</strong>
                    <p>Heavy rainfall detected near NH-127B.</p>
                  </div>
                </div>

                <div className="alert-item">
                  <span className="alert-icon info-icon">i</span>
                  <div>
                    <strong>Weather Advisory</strong>
                    <p>Rainfall warning active for the region.</p>
                  </div>
                </div>
              </div>
            </section>

            <section className="panel">
              <div className="panel-header">
                <div>
                  <span className="panel-label">REGIONAL VIEW</span>
                  <h3>District Connectivity</h3>
                </div>
              </div>

              <div className="district-list">
                <div><span>Kamrup</span><b className="good">Good</b></div>
                <div><span>Dibrugarh</span><b className="moderate">Moderate</b></div>
                <div><span>Kohima</span><b className="poor">Poor</b></div>
                <div><span>Champhai</span><b className="good">Good</b></div>
              </div>
            </section>
          </div>
        </section>
      </main>
    </div>
  );
}

export default App
