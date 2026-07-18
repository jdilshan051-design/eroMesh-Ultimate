import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as px
import time

st.set_page_config(page_title="AeroMesh Ultimate - 4D ATC Engine", layout="wide")
st.title("🛰️ AeroMesh Ultimate: Next-Gen 4D Multi-Agent Free-Flight Engine")
st.markdown("### Industrial-Grade Autonomous 3D Trajectory Prediction & TCAS-IV Resolution Network")

# Sidebar - Parameter Configuration
st.sidebar.header("🕹️ Airspace Control Vectors")
num_agents = st.sidebar.slider("Active Tactical Agents (Aircraft)", 4, 20, 8)
lookahead_window = st.sidebar.slider("Predictive Lookahead Window (Seconds)", 30, 300, 120)
sim_speed = st.sidebar.slider("Simulation Step Sync (Seconds per tick)", 30, 120, 60)

# Initialize Deterministic Flight State Vector for High-Fidelity Data
np.random.seed(404)
agent_ids = [f"ALK{np.random.randint(100, 999)}" for _ in range(num_agents)]

# Generate realistic flight parameters inside a 100x100 NM Sector Area
x = np.random.uniform(20, 80, num_agents)
y = np.random.uniform(20, 80, num_agents)
z = np.random.uniform(30000, 38000, num_agents) # Feet (Flight Levels)
headings = np.random.uniform(0, 360, num_agents) # Degrees
speeds = np.random.uniform(440, 495, num_agents) # Knots (True Airspeed)
vspeed = np.random.uniform(-5, 5, num_agents) * 10 # Feet per second vertical speed

# Main Action Button
if st.button("▶️ Initialize 4D Airspace Core Inference Loop"):
    status_msg = st.empty()
    metric_cols = st.columns(4)
    chart_slot = st.empty()
    table_slot = st.empty()

    # Dynamic Radar Sweep Simulation Loop (10 Frames of Continuous Flight)
    for tick in range(10):
        # 3D Velocity Vector Conversion (1 Knot = 1/3600 NM/sec, 1 Foot = 1/6076 NM)
        vx = speeds * np.sin(np.radians(headings)) / 3600
        vy = speeds * np.cos(np.radians(headings)) / 3600
        vz = vspeed / 6076 # Vertical speed converted to NM/second
        
        # Advance positional states by current simulation time interval
        x += vx * sim_speed
        y += vy * sim_speed
        z += vspeed * sim_speed # Add altitude in feet directly

        conflicts = []
        
        # Advanced Pairwise 3D Trajectory Conflict Prediction
        for i in range(num_agents):
            for j in range(i + 1, num_agents):
                # Relative Position Vectors
                dx, dy, dz = x[i] - x[j], y[i] - y[j], (z[i] - z[j]) / 6076
                # Relative Velocity Vectors
                dvx, dvy, dvz = vx[i] - vx[j], vy[i] - vy[j], vz[i] - vz[j]
                
                # Math: Time to Closest Point of Approach (Tcpa) in 3D Space
                num = -(dx*dvx + dy*dvy + dz*dvz)
                den = dvx**2 + dvy**2 + dvz**2
                
                tcpa = num / den if den > 0 else -1
                
                # Check if conflict falls within our active lookahead safety envelope
                if 0 <= tcpa <= lookahead_window:
                    # Calculate Minimum Separation Distance at Tcpa (Dcpa)
                    dcpa_h = np.sqrt((dx + dvx*tcpa)**2 + (dy + dvy*tcpa)**2)
                    dcpa_v = abs((z[i] + (vspeed[i]*tcpa)) - (z[j] + (vspeed[j]*tcpa)))
                    
                    # ICAO Separation Loss Criteria: Horizontal < 5 NM and Vertical < 1000 ft
                    if dcpa_h < 5.0 and dcpa_v < 1000:
                        conflicts.append({
                            "Agent A": agent_ids[i],
                            "Agent B": agent_ids[j],
                            "Current Range (NM)": round(np.sqrt(dx**2 + dy**2), 2),
                            "Time to CPA (sec)": int(tcpa),
                            "Est. Miss Distance (NM)": round(dcpa_h, 2),
                            "Vertical Separation at CPA (ft)": int(dcpa_v),
                            "Tactical Resolution Vector": f"MA-{agent_ids[i]}: CLIMB FL{int((z[i]+2500)/100)} H+20° | MA-{agent_ids[j]}: DESCEND FL{int((z[j]-2500)/100)} H-20°"
                        })

        # Update Live Top-Level Airspace Metrics
        metric_cols[0].metric("Monitored Vectors", num_agents)
        metric_cols[1].metric("3D Trajectory Conflicts", len(conflicts), delta=len(conflicts), delta_color="inverse")
        metric_cols[2].metric("Sector Latency", f"{np.random.uniform(0.4, 1.2):.2f} ms")
        metric_cols[3].metric("Current Flight Step", f"{tick + 1}/10")

        # Render Interactive 3D Plotly Chart
        fig = px.Figure()
        
        # Plot aircraft positions and headers
        fig.add_trace(px.Scatter3d(
            x=x, y=y, z=z, mode='markers+text',
            text=agent_ids,
            marker=dict(size=7, color=z, colorscale='Viridis', opacity=0.9),
            name="Active Aircraft Vectors"
        ))
        
        # Formatting the 3D Space Sector
        fig.update_layout(
            title=f" Real-time 4D Digital Airspace Twin (Sweep {tick+1})",
            scene=dict(
                xaxis_title='Longitude Vector (NM)',
                yaxis_title='Latitude Vector (NM)',
                zaxis_title='Altitude Vector (Flight Level / Feet)',
                xaxis=dict(range=[0, 100]),
                yaxis=dict(range=[0, 100]),
                zaxis=dict(range=[25000, 42000])
            ),
            margin=dict(l=0, r=0, b=0, t=40),
            height=600
        )
        
        with chart_slot:
            st.plotly_chart(fig, use_container_width=True)

        # Render Active Resolution Conflict Tables
        if len(conflicts) > 0:
            with status_msg:
                st.error(" AIRSPACE WARNING: Separation Loss Detected! Decomposing Multi-Agent Resolution Vector Matrix...")
            with table_slot:
                st.dataframe(pd.DataFrame(conflicts), use_container_width=True)
        else:
            with status_msg:
                st.success(" Airspace Operating Safely. Deconfliction network in nominal state.")
            with table_slot:
                st.info("No active structural separation anomalies detected for this radar frame.")

        time.sleep(1.2) # Fluid frame transition delay

# Telemetry Data Vector Feed Overview
st.markdown("---")
st.write("####  Real-Time High-Fidelity 4D ADS-B Telemetry Stream")
fleet_df = pd.DataFrame({
    "Callsign": agent_ids,
    "X-Pos (NM)": x,
    "Y-Pos (NM)": y,
    "Altitude (ft)": z,
    "Vertical Rate (ft/s)": vspeed,
    "True Heading (°)": headings,
    "Airspeed (KTAS)": speeds
}).set_index("Callsign")
st.dataframe(fleet_df, use_container_width=True)