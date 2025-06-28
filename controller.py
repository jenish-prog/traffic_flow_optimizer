# controller.py
import traci
import sumolib
import os

# Set SUMO_HOME
SUMO_HOME = "C:/Program Files (x86)/Eclipse/Sumo"  # Update if your path is different
sumo_binary = os.path.join(SUMO_HOME, "bin", "sumo-gui.exe")

# Path to your copied scenario
config_file = r"D:\Traffic flow Optimizer\traffic_flow_optimizer\sumo_simulation\sumo_sim\osm.sumocfg"  # Update based on your folder

# Start SUMO with TraCI
traci.start([sumo_binary, "-c", config_file])

step = 0

while step < 500:
    traci.simulationStep()

    # Example: Get all traffic lights
    tls_ids = traci.trafficlight.getIDList()

    for tls in tls_ids:
        print(f"Traffic light {tls} current phase: {traci.trafficlight.getPhase(tls)}")

        # Example: Force phase change
        if step % 100 == 0:
            traci.trafficlight.setPhase(tls, (traci.trafficlight.getPhase(tls) + 1) % 4)

    step += 1

traci.close()
print("Simulation done.")
