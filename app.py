import streamlit as st
import numpy as np
import joblib
import pandas as pd
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Smart Irrigation System",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Red and Light Blue theme
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #dc3545, #add8e6);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f0f8ff;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        border: 1px solid #add8e6;
    }
    .sprinkler-on {
        background: #e6f3ff;
        color: #0066cc;
        padding: 0.5rem;
        border-radius: 5px;
        border-left: 4px solid #add8e6;
        text-align: center;
        margin: 0.2rem 0;
    }
    .sprinkler-off {
        background: #ffe6e6;
        color: #990000;
        padding: 0.5rem;
        border-radius: 5px;
        border-left: 4px solid #dc3545;
        text-align: center;
        margin: 0.2rem 0;
    }
    .sensor-bar {
        background: #f5f5f5;
        height: 20px;
        border-radius: 10px;
        overflow: hidden;
        margin: 5px 0;
    }
    .sensor-fill {
        height: 100%;
        background: linear-gradient(90deg, #dc3545, #add8e6);
        transition: width 0.3s ease;
    }
</style>
""", unsafe_allow_html=True)

# Load model
@st.cache_resource
def load_model():
    try:
        return joblib.load("Farm_Irrigation_System.pkl")
    except FileNotFoundError:
        st.error("⚠️ Model file 'Farm_Irrigation_System.pkl' not found.")
        return None
    except Exception as e:
        st.error(f"⚠️ Error loading model: {str(e)}")
        return None

model = load_model()

# Header
st.markdown("""
<div class="main-header">
    <h1>🌱 Smart Irrigation System</h1>
    <p>AI-Powered Farm Sprinkler Management</p>
</div>
""", unsafe_allow_html=True)

if model is None:
    st.stop()

# Sidebar
with st.sidebar:
    st.header("🎛️ Quick Settings")
    
    preset = st.selectbox(
        "Load Preset Configuration:",
        ["Custom", "Dry Season", "Wet Season", "Moderate Conditions", "Drought Alert"]
    )
    
    preset_values = {
        "Dry Season": [0.2] * 20,
        "Wet Season": [0.8] * 20,
        "Moderate Conditions": [0.5] * 20,
        "Drought Alert": [0.1] * 20
    }
    
    if st.button("🔄 Apply Preset"):
        if preset != "Custom":
            st.session_state.update({f"sensor_{i}": val for i, val in enumerate(preset_values[preset])})
            st.rerun()
    
    st.markdown("---")
    st.markdown("### 📊 System Info")
    st.info("• 20 Environmental Sensors\n• 20 Irrigation Zones\n• Real-time AI Predictions")

# Main section - Sensor Configuration
st.header("🌡️ Sensor Configuration")

# Initialize session state
if 'sensor_values' not in st.session_state:
    st.session_state.sensor_values = [0.5] * 20

# Display sensors in 4 columns
sensor_values = []
cols = st.columns(4)

for i in range(20):
    col_idx = i % 4
    with cols[col_idx]:
        val = st.slider(
            f"**Sensor {i}**",
            min_value=0.0,
            max_value=1.0,
            value=st.session_state.get(f"sensor_{i}", 0.5),
            step=0.01,
            key=f"sensor_{i}",
            help=f"Sensor {i} - Normalized value (0=Low, 1=High)"
        )
        sensor_values.append(val)

# Control buttons
st.markdown("---")
button_col1, button_col2 = st.columns([1, 1])

with button_col1:
    if st.button("🔄 Reset All", type="secondary"):
        for i in range(20):
            st.session_state[f"sensor_{i}"] = 0.5
        st.rerun()

with button_col2:
    if st.button("🎲 Randomize", type="secondary"):
        for i in range(20):
            st.session_state[f"sensor_{i}"] = np.random.random()
        st.rerun()

# Predict button
st.markdown("---")
predict_button = st.button("🚿 Predict Irrigation", type="primary", use_container_width=True)

# Bottom Section - Irrigation Prediction
if predict_button and len(sensor_values) == 20:
    st.markdown("---")
    st.header("🚿 Irrigation Predictions")
    
    with st.spinner("🤖 AI is analyzing sensor data..."):
        try:
            input_array = np.array(sensor_values).reshape(1, -1)
            prediction = model.predict(input_array)[0]
            
            # Store prediction in session state
            st.session_state['latest_prediction'] = prediction
            
            # Count active sprinklers
            active_count = sum(prediction)
            total_count = len(prediction)
            
            # Overall status metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <h3 style="margin: 0; color: #add8e6;">🚿 Active Sprinklers</h3>
                    <h2 style="margin: 5px 0; color: #333;">{active_count}/{total_count}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <h3 style="margin: 0; color: #add8e6;">💧 Active Zones</h3>
                    <h2 style="margin: 5px 0; color: #333;">{active_count} zones</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                percentage = (active_count/total_count)*100
                st.markdown(f"""
                <div class="metric-card">
                    <h3 style="margin: 0; color: #add8e6;">⚡ Coverage</h3>
                    <h2 style="margin: 5px 0; color: #333;">{percentage:.1f}%</h2>
                </div>
                """, unsafe_allow_html=True)
            
            # Zone status grid
            st.subheader("Sprinkler Zone Status")
            
            # Create 4x5 grid for sprinklers
            for row in range(4):
                cols = st.columns(5)
                for col in range(5):
                    sprinkler_idx = row * 5 + col
                    if sprinkler_idx < len(prediction):
                        status = prediction[sprinkler_idx]
                        with cols[col]:
                            if status == 1:
                                st.markdown(f"""
                                <div class="sprinkler-on">
                                    <strong>Zone {sprinkler_idx + 1}</strong><br>
                                    🔵 ON
                                </div>
                                """, unsafe_allow_html=True)
                            else:
                                st.markdown(f"""
                                <div class="sprinkler-off">
                                    <strong>Zone {sprinkler_idx + 1}</strong><br>
                                    🔴 OFF
                                </div>
                                """, unsafe_allow_html=True)
            
            # Farm layout view
            st.subheader("🗺️ Farm Layout View")
            
            st.markdown("**Irrigation Zone Map (4x5 Grid)**")
            grid_html = "<div style='font-family: monospace; font-size: 14px; line-height: 1.5;'>"
            
            for row in range(4):
                row_html = ""
                for col in range(5):
                    zone_idx = row * 5 + col
                    if zone_idx < len(prediction):
                        if prediction[zone_idx] == 1:
                            row_html += f"<span style='background: #e6f3ff; padding: 4px 8px; margin: 2px; border-radius: 4px; color: #0066cc; border: 1px solid #add8e6;'>Z{zone_idx+1:2d}🔵</span>"
                        else:
                            row_html += f"<span style='background: #ffe6e6; padding: 4px 8px; margin: 2px; border-radius: 4px; color: #990000; border: 1px solid #dc3545;'>Z{zone_idx+1:2d}🔴</span>"
                grid_html += f"<div style='margin: 5px 0;'>{row_html}</div>"
            
            grid_html += "</div>"
            st.markdown(grid_html, unsafe_allow_html=True)
            
            # Results table
            st.subheader("📋 Detailed Results")
            
            results_df = pd.DataFrame({
                'Zone': [f"Zone {i+1}" for i in range(len(prediction))],
                'Status': ['ON' if status == 1 else 'OFF' for status in prediction],
                'Sensor_Value': [f"{val:.3f}" for val in sensor_values[:len(prediction)]],
                'Row': [(i // 5) + 1 for i in range(len(prediction))],
                'Column': [(i % 5) + 1 for i in range(len(prediction))]
            })
            
            st.dataframe(results_df, use_container_width=True)
            
            # Export functionality
            st.subheader("📤 Export Results")
            
            results_df['Timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            csv = results_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Results as CSV",
                data=csv,
                file_name=f"irrigation_prediction_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
            
            # Prediction summary
            st.subheader("📈 Prediction Summary")
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Zone Status Count:**")
                status_counts = results_df['Status'].value_counts()
                for status, count in status_counts.items():
                    st.write(f"• {status}: {count} zones")
            
            with col2:
                st.write("**Sensor Statistics:**")
                sensor_vals = [float(x) for x in results_df['Sensor_Value']]
                st.write(f"• Average: {np.mean(sensor_vals):.3f}")
                st.write(f"• Max: {np.max(sensor_vals):.3f}")
                st.write(f"• Min: {np.min(sensor_vals):.3f}")
            
        except Exception as e:
            st.error(f"❌ Prediction failed: {str(e)}")
            st.info("Please check your model file and ensure all sensors have valid values.")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem 0;">
    <p>🌱 Smart Irrigation System v2.0 | Powered by AI | Built with Streamlit</p>
    <p><em>Optimizing water usage for sustainable agriculture</em></p>
</div>
""", unsafe_allow_html=True)
