# Isaac Sim 5.0.0 - Standard Operating Procedure

## Table of Contents
1. [Launching Isaac Sim](#launching-isaac-sim)
2. [Importing a Robot from USD](#importing-a-robot-from-usd)
3. [Adding Sensors and RViz Integration](#adding-sensors-and-rviz-integration)
4. [Troubleshooting & Diagnostics](#troubleshooting--diagnostics)
5. [Common Issues & Solutions](#common-issues--solutions)

---

## Launching Isaac Sim
### DO NOT INTERACT WITH ISAAC SIM WHILST LOADING ###
## This can cause the entire system to crash ##
### Method 1: Using Launch Script (Recommended)
```bash
./isaacsim5.0.0.sh
```

This script is located at `/home/george/isaacsim5.0.0.sh` and executes:
```bash
cd Downloads/IsaacSim-5.0.0/_build/linux-x86_64/release/ && ./isaac-sim.sh
```

### Method 2: Direct Launch
```bash
cd ~/Downloads/IsaacSim-5.0.0/_build/linux-x86_64/release/
./isaac-sim.sh
```

### Verify Isaac Sim Status
Use the status check script:
```bash
./check_isaac_sim_status.sh
```

---

## Importing a Robot from USD

### Method 1: GUI Import

#### Step 1: Open Isaac Sim
Launch Isaac Sim using the script above.

#### Step 2: Create or Open Scene
- **File → New** (for a new scene)
- **File → Open** (for existing scene)

#### Step 3: Import Robot USD
1. Navigate to your robot's USD file location (e.g., `/home/george/Downloads/example_holonomic_controller.usd`)
2. Drag the file into `Stage` on the right side menu
**Example Robot USD Paths:**
- Isaac Lab Robots: `~/Downloads/isaacsim/Assets/Isaac/4.2/Isaac/IsaacLab/Robots/`
  - Franka Panda: `FrankaEmika/panda_instanceable.usd`
  - UR10: `UniversalRobots/UR10/ur10_instanceable.usd`
  - ANYmal-D: `ANYbotics/ANYmal-D/anymal_d.usd`
  - Unitree Go2: `Unitree/Go2/go2.usd`
- Rossmaster X3: `~/Downloads/Rossmasterx3.usd`

#### Step 4: Position Robot
1. Select the imported robot in the **Stage** panel
2. Use the **Transform** tools to position:
   - **Move Tool**: Press `W` or click move icon
   - **Rotate Tool**: Press `E` or click rotate icon
   - **Scale Tool**: Press `R` or click scale icon

#### Step 5: Add Physics (if needed)
If your robot doesn't have physics:
1. Select robot root prim
2. **Isaac Sim → Robots → Add Robot Physics**
3. Configure:
   - **Articulation Root**: Enable
   - **Rigid Body**: Enable on all links
   - **Collision**: Enable collision meshes

### Method 2: Python Scripting

```python
from omni.isaac.core.utils.stage import add_reference_to_stage
from omni.isaac.core import World
import omni.usd

# Initialize world
world = World(stage_units_in_meters=1.0)

# Import robot from USD
robot_usd_path = "/home/george/Downloads/Rossmasterx3.usd"
robot_prim_path = "/World/Robot"

add_reference_to_stage(
    usd_path=robot_usd_path,
    prim_path=robot_prim_path
)

# Set robot position
from omni.isaac.core.utils.prims import get_prim_at_path
from pxr import Gf

robot_prim = get_prim_at_path(robot_prim_path)
xformable = UsdGeom.Xformable(robot_prim)

# Set position (x, y, z)
xformable.AddTranslateOp().Set(Gf.Vec3d(0.0, 0.0, 0.5))

# Set rotation (in degrees)
xformable.AddRotateXYZOp().Set(Gf.Vec3d(0.0, 0.0, 0.0))

world.reset()
```

### Method 3: Loading Pre-configured Environments

Isaac Sim includes pre-built environments:
```python
from omni.isaac.core.utils.stage import add_reference_to_stage

# Add warehouse environment
add_reference_to_stage(
    usd_path="/Isaac/Environments/Simple_Warehouse/warehouse.usd",
    prim_path="/World/Environment"
)

# Add robot to environment
add_reference_to_stage(
    usd_path="/Isaac/Robots/YahboomCar/yahboomcar.usd",
    prim_path="/World/yahboomcar"
)
```

---

## Adding Sensors and RViz Integration

### Prerequisites

**Enable ROS2 Bridge Extension:**
1. **Window → Extensions**
2. Search: "ROS2 Bridge"
3. Enable: **omni.isaac.ros2_bridge**

Or via Python:
```python
from omni.isaac.core.utils.extensions import enable_extension
enable_extension("omni.isaac.ros2_bridge")
```

---

### Adding Sensors to Your Robot

#### Method 1: Adding Lidar Sensor (GUI)

1. **Select Robot Prim** in Stage panel
2. **Create → Isaac → Sensors → Lidar → Rotating Lidar**
3. Position the sensor:
   - Select Lidar prim in hierarchy
   - Use Transform tools (W, E, R) to position
   - Typical position: On top of robot chassis

4. **Configure Lidar Properties:**
   - Min Range: `0.1` meters
   - Max Range: `10.0` meters
   - Horizontal FOV: `360.0` degrees
   - Vertical FOV: `30.0` degrees
   - Horizontal Resolution: `0.5` degrees
   - Vertical Resolution: `1.0` degrees
   - Rotation Rate: `20.0` Hz

#### Method 2: Adding Camera Sensor (GUI)

1. **Select Robot Prim**
2. **Create → Camera**
3. Position camera on robot
4. **Configure Camera Properties:**
   - Resolution: `1280x720` or `640x480`
   - Focal Length: `24.0`
   - Horizontal Aperture: `20.955`

#### Method 3: Adding Depth Camera (GUI)

1. **Select Robot Prim**
2. **Create → Isaac → Sensors → Camera → RGB-D Camera**
3. Position camera
4. **Configure Depth Properties:**
   - Near Clipping: `0.1`
   - Far Clipping: `10.0`

#### Method 4: Adding IMU Sensor (GUI)

1. **Select Robot Prim**
2. **Create → Isaac → Sensors → IMU Sensor**
3. Position at robot center of mass
4. Configure update rate and noise parameters

---

### Setting Up Action Graphs for Sensor Publishing

#### Step 1: Open Action Graph Editor
**Window → Visual Scripting → Action Graph**

#### Step 2: Create New Action Graph
1. Click **New Action Graph**
2. Name it: `SensorPublishingGraph`
3. Set path: `/World/Robot/SensorGraph`

#### Step 3: Add Core Nodes

**Required Nodes for Any ROS2 Publishing:**

1. **On Playback Tick** (trigger)
   - Automatically fires every simulation frame
   - Usually present by default

2. **ROS2 Context** (required for all ROS2 communication)
   - Path: `ROS2 → Context → ROS2 Context`
   - Domain ID: `0`
   - Node Name: `isaac_sim_node`

#### Step 4: Add Sensor-Specific Publishers

**For Lidar → RViz:**

1. **Add Node**: `ROS2 → Publishers → ROS2 Publish Laser Scan`
2. **Configure**:
   - Topic Name: `/scan`
   - Frame ID: `lidar_frame` or `base_link`
   - **QoS Profile** (CRITICAL):
     - Reliability: `BEST_EFFORT`
     - Durability: `VOLATILE`
     - History: `KEEP_LAST`
     - Depth: `10`

3. **Connect Lidar Prim**:
   - Select "Isaac Read Lidar Beam Node" if needed
   - Or directly connect lidar prim path to publisher

**For RGB Camera → RViz:**

1. **Add Node**: `ROS2 → Publishers → ROS2 Publish Camera Info`
2. **Add Node**: `ROS2 → Publishers → ROS2 Publish RGB`
3. **Configure Camera Info**:
   - Topic Name: `/camera/camera_info`
   - Frame ID: `camera_frame`
4. **Configure RGB Publisher**:
   - Topic Name: `/camera/image_raw`
   - Frame ID: `camera_frame`
   - Encoding: `rgb8`

**For Depth Camera → RViz:**

1. **Add Node**: `ROS2 → Publishers → ROS2 Publish Depth`
2. **Configure**:
   - Topic Name: `/camera/depth/image_raw`
   - Frame ID: `camera_depth_frame`

**For Point Cloud → RViz:**

1. **Add Node**: `ROS2 → Publishers → ROS2 Publish Point Cloud`
2. **Configure**:
   - Topic Name: `/points`
   - Frame ID: `lidar_frame`
   - QoS: `BEST_EFFORT`

**For IMU → RViz:**

1. **Add Node**: `ROS2 → Publishers → ROS2 Publish IMU`
2. **Configure**:
   - Topic Name: `/imu`
   - Frame ID: `imu_link`

**For Transform Tree (TF):**

1. **Add Node**: `ROS2 → Publishers → ROS2 Publish Transform Tree`
2. **Configure**:
   - Topic Name: `/tf`
   - Target Prims: `/World/Robot` (your robot root)
   - Parent Frame: `odom` or `world`

#### Step 5: Connect All Nodes

**Connection Pattern:**
```
On Playback Tick → execIn (for each publisher)
ROS2 Context → context (for each ROS2 node)
Sensor Prim → input (for each sensor publisher)
```

**Example Connections:**
1. `OnPlaybackTick.outputs:tick` → `PublishLaserScan.inputs:execIn`
2. `ROS2Context.outputs:context` → `PublishLaserScan.inputs:context`
3. `LidarPrim.outputs:data` → `PublishLaserScan.inputs:data` (if using read node)

#### Step 6: Save and Test
1. **File → Save**
2. Click **Play** in Isaac Sim
3. Verify topics are publishing:
   ```bash
   ros2 topic list
   ros2 topic hz /scan
   ros2 topic echo /scan --once
   ```

---

### Visualizing in RViz

#### Step 1: Launch RViz
```bash
rviz2
```

#### Step 2: Set Fixed Frame
1. In **Global Options**
2. Set **Fixed Frame**: `odom` or `base_link`

#### Step 3: Add Sensor Displays

**Add Laser Scan:**
1. Click **Add** button
2. Select **LaserScan**
3. Configure:
   - Topic: `/scan`
   - Size: `0.05`
   - Color: Red or Rainbow by intensity
   - Decay Time: `0`

**Add Camera Image:**
1. Click **Add**
2. Select **Image** or **Camera**
3. Topic: `/camera/image_raw`

**Add Point Cloud:**
1. Click **Add**
2. Select **PointCloud2**
3. Configure:
   - Topic: `/points`
   - Size: `0.01`
   - Style: Points or Flat Squares
   - Color Transformer: RGB8 or Intensity

**Add TF Tree:**
1. Click **Add**
2. Select **TF**
3. Shows all coordinate frames and relationships

**Add Robot Model (Optional):**
1. Click **Add**
2. Select **RobotModel**
3. Topic: `/robot_description`

#### Step 4: Troubleshooting RViz Display

**If sensors don't appear:**

1. **Check Topic Publishing:**
   ```bash
   ros2 topic list
   ros2 topic hz /scan
   ```

2. **Check Frame ID:**
   - RViz Status should show "OK" (green)
   - If red, check Fixed Frame matches sensor Frame ID
   - Verify TF tree has required transforms

3. **Check QoS Match:**
   ```bash
   ros2 topic info /scan -v
   ```
   Ensure publisher and subscriber QoS are compatible

4. **Check Data:**
   ```bash
   ros2 topic echo /scan --once
   ```
   Verify sensor is producing valid data

---

### Python Action Graph Setup Example

```python
import omni.graph.core as og

graph_path = "/World/Robot/SensorGraph"
keys = og.Controller.Keys

# Create action graph for Lidar + Camera + TF
og.Controller.edit(
    {"graph_path": graph_path, "evaluator_name": "execution"},
    {
        keys.CREATE_NODES: [
            ("OnPlaybackTick", "omni.graph.action.OnPlaybackTick"),
            ("ROS2Context", "omni.isaac.ros2_bridge.ROS2Context"),
            ("PublishScan", "omni.isaac.ros2_bridge.ROS2PublishLaserScan"),
            ("PublishCameraInfo", "omni.isaac.ros2_bridge.ROS2PublishCameraInfo"),
            ("PublishRGB", "omni.isaac.ros2_bridge.ROS2PublishRgb"),
            ("PublishTF", "omni.isaac.ros2_bridge.ROS2PublishTransformTree"),
        ],
        keys.SET_VALUES: [
            # ROS2 Context
            ("ROS2Context.inputs:domain_id", 0),

            # Laser Scan
            ("PublishScan.inputs:topicName", "/scan"),
            ("PublishScan.inputs:frameId", "lidar_frame"),
            ("PublishScan.inputs:qosProfile.reliability", 0),  # BEST_EFFORT

            # Camera Info
            ("PublishCameraInfo.inputs:topicName", "/camera/camera_info"),
            ("PublishCameraInfo.inputs:frameId", "camera_frame"),

            # RGB Image
            ("PublishRGB.inputs:topicName", "/camera/image_raw"),
            ("PublishRGB.inputs:frameId", "camera_frame"),

            # Transform Tree
            ("PublishTF.inputs:topicName", "/tf"),
            ("PublishTF.inputs:targetPrims", ["/World/Robot"]),
        ],
        keys.CONNECT: [
            # Execution connections
            ("OnPlaybackTick.outputs:tick", "PublishScan.inputs:execIn"),
            ("OnPlaybackTick.outputs:tick", "PublishCameraInfo.inputs:execIn"),
            ("OnPlaybackTick.outputs:tick", "PublishRGB.inputs:execIn"),
            ("OnPlaybackTick.outputs:tick", "PublishTF.inputs:execIn"),

            # Context connections
            ("ROS2Context.outputs:context", "PublishScan.inputs:context"),
            ("ROS2Context.outputs:context", "PublishCameraInfo.inputs:context"),
            ("ROS2Context.outputs:context", "PublishRGB.inputs:context"),
            ("ROS2Context.outputs:context", "PublishTF.inputs:context"),
        ],
    },
)
```

---

### QoS Settings Reference

**Critical for RViz Compatibility:**

| Sensor Type | Reliability | Durability | History |
|-------------|-------------|------------|---------|
| Lidar/Laser Scan | BEST_EFFORT | VOLATILE | KEEP_LAST |
| Camera (RGB/Depth) | BEST_EFFORT | VOLATILE | KEEP_LAST |
| Point Cloud | BEST_EFFORT | VOLATILE | KEEP_LAST |
| IMU | BEST_EFFORT | VOLATILE | KEEP_LAST |
| TF Tree | RELIABLE | VOLATILE | KEEP_LAST |
| Odometry | RELIABLE | VOLATILE | KEEP_LAST |

**QoS Values in Python:**
```python
# Reliability
0 = BEST_EFFORT   # For sensor data
1 = RELIABLE      # For commands/TF

# Durability
0 = VOLATILE
1 = TRANSIENT_LOCAL

# History
0 = KEEP_LAST
1 = KEEP_ALL
```

---

## Troubleshooting & Diagnostics

### Common Verification Commands

#### Check ROS2 Topics
```bash
# List all topics
ros2 topic list

# Check topic publishing rate
ros2 topic hz /scan
ros2 topic hz /odom

# Check topic data
ros2 topic echo /scan --once
ros2 topic echo /odom --once

# Check topic QoS settings (CRITICAL!)
ros2 topic info /scan -v
```

**Expected Output for /scan:**
```
QoS profile:
  Reliability: BEST_EFFORT  ← Must be BEST_EFFORT!
  Durability: VOLATILE
  History: KEEP_LAST
```

#### Check TF Tree
```bash
# View TF tree structure
ros2 run tf2_tools view_frames

# Check specific transform
ros2 run tf2_ros tf2_echo odom base_link

# Monitor TF publishing
ros2 topic hz /tf
```

#### Check ROS2 Nodes
```bash
# List active nodes
ros2 node list

# Check Isaac Sim node
ros2 node info /isaac_sim_node
```

### Diagnostic Script Template

Create a diagnostic script:
```bash
#!/bin/bash
echo "=== Isaac Sim ROS2 Diagnostics ==="
echo ""
echo "1. Checking ROS2 topics..."
ros2 topic list | grep -E "(scan|odom|tf)"
echo ""
echo "2. Checking /scan QoS..."
ros2 topic info /scan -v | grep -A 3 "QoS profile"
echo ""
echo "3. Checking publishing rates..."
timeout 2 ros2 topic hz /scan
timeout 2 ros2 topic hz /odom
echo ""
echo "4. Checking TF tree..."
ros2 topic echo /tf --once | grep frame_id
```

---

## Common Issues & Solutions

### Issue 1: SLAM Not Receiving Scans

**Symptoms:**
- SLAM Toolbox starts but no map appears
- `/scan` publishes but SLAM shows warnings

**Diagnosis:**
```bash
ros2 topic info /scan -v
ros2 topic info /slam_toolbox/scan_visualization -v
```

**Solution:**
Change QoS to BEST_EFFORT in Isaac Sim Action Graph:
1. Open Action Graph Editor
2. Select ROS2 Publish Laser Scan node
3. Properties → QoS Profile → Reliability: **BEST_EFFORT**
4. Save scene and restart simulation

**Reference:** See `ISAAC_SIM_SETUP.md` for detailed steps

---

### Issue 2: No Odometry Published

**Symptoms:**
- `/odom` topic doesn't exist
- SLAM tracking fails
- TF tree missing `odom → base_link`

**Diagnosis:**
```bash
ros2 topic list | grep odom
ros2 run tf2_tools view_frames
```

**Solutions:**

**Option A: Add Odometry Publisher in Action Graph**
1. Window → Visual Scripting → Action Graph
2. Add: ROS2 Publish Odometry node
3. Configure:
   - Topic: `/odom`
   - Odom Frame: `odom`
   - Robot Frame: `base_link` or `sim_camera`
4. Connect to On Playback Tick

**Option B: Use Differential Drive Controller**
If robot has wheels:
1. Isaac Sim → Create → Isaac → Wheeled Robots → Differential Controller
2. Configure wheel parameters
3. Auto-publishes odometry

**Option C: Use Python Bridge Script**
Create `odom_to_tf_bridge_sim_camera.py` (already exists in your directory)

**Reference:** See `ISAAC_SIM_ODOMETRY_SETUP.md`

---

### Issue 3: Frame Drops / Simulation Lag

**Symptoms:**
- Low FPS in Isaac Sim
- Jerky robot movement
- ROS2 topics publish at irregular rates

**Solutions:**

1. **Reduce Physics Timestep:**
   - Edit → Preferences → Physics
   - Increase timestep (e.g., 1/60 → 1/30)

2. **Disable Real-time Mode:**
   - Uncheck "Real-time" in simulation controls
   - Allows simulation to run as fast as possible

3. **Optimize Rendering:**
   - Window → Viewport → Settings
   - Reduce Anti-aliasing
   - Lower resolution

4. **Check GPU Usage:**
   ```bash
   nvidia-smi
   ```

5. **Ensure Stage Units Are Correct:**
   ```python
   world = World(stage_units_in_meters=1.0)
   ```
   Incorrect scaling causes physics instability

---

### Issue 4: Robot Not Responding to Commands

**Symptoms:**
- Publishing to `/cmd_vel` but robot doesn't move
- Joints not responding to control commands

**Diagnosis:**
```bash
# Check if cmd_vel is being received
ros2 topic echo /cmd_vel

# Check articulation state
ros2 topic list | grep articulation
```

**Solutions:**

1. **Add ROS2 Subscribe Twist:**
   - Action Graph → Add: ROS2 Subscribe Twist
   - Topic: `/cmd_vel`
   - Connect to differential drive or articulation controller

2. **Verify Physics:**
   - Check robot has Articulation Root component
   - Check joints have drives enabled
   - Check collision meshes are present

3. **Check Joint Limits:**
   - Window → Isaac → Articulation Inspector
   - Verify joint limits allow movement
   - Check effort/velocity limits

---

### Issue 5: Lidar Not Publishing Data

**Symptoms:**
- `/scan` topic exists but no data
- Laser scan messages are empty

**Solutions:**

1. **Check Lidar Prim:**
   - Stage panel → Find Lidar prim
   - Ensure it has "Lidar" or "Rotating Lidar" component

2. **Verify Action Graph:**
   - Check Lidar prim is connected to PublishLaserScan node
   - Check "enabled" checkbox is ON

3. **Check Lidar Range:**
   - Properties → Lidar Sensor
   - Min Range: 0.1 (or appropriate minimum)
   - Max Range: 10.0 (or appropriate maximum)

4. **Enable Lidar in Simulation:**
   - Isaac Sim → Sensors → Lidar
   - Ensure "High LOD" or "Low LOD" is enabled

---

### Issue 6: TF Tree Incomplete

**Symptoms:**
- Missing transforms between frames
- `tf2_ros tf2_echo` fails with "frame does not exist"

**Diagnosis:**
```bash
ros2 run tf2_tools view_frames
# Check output PDF for missing links
```

**Solutions:**

1. **Add Transform Tree Publisher:**
   - Action Graph → ROS2 Publish Transform Tree
   - Target Prims: Robot root prim path
   - Parent Frame: `odom` or `map`

2. **Check Robot Description:**
   ```bash
   ros2 topic echo /robot_description --once
   ```
   Ensure URDF includes all necessary links/joints

3. **Use Static TF Publishers:**
   ```bash
   ros2 run tf2_ros static_transform_publisher 0 0 0 0 0 0 odom base_link
   ```

---

## Best Practices

### 1. Scene Organization
- Use clear, hierarchical naming: `/World/Robot/Sensors/Lidar`
- Group related prims under a parent Xform
- Use descriptive names for action graphs

### 2. QoS Consistency
- Always use BEST_EFFORT for sensor data (Lidar, Camera, IMU)
- Use RELIABLE for command topics (cmd_vel, joint commands)
- Document QoS settings in scene notes

### 3. Performance Optimization
- Use instanced meshes for repeated objects
- Disable unnecessary rendering features
- Limit physics substeps
- Use LOD (Level of Detail) meshes

### 4. Version Control
- Save scene files with version numbers
- Keep backup copies before major changes
- Document changes in commit messages

### 5. Testing Workflow
1. Test in Isaac Sim first (verify topics publish)
2. Test with ROS2 diagnostics (check QoS, rates)
3. Test with SLAM (verify integration)
4. Test with full navigation stack

---

## Quick Reference

### Launch Commands
```bash
# Start Isaac Sim
./isaacsim5.0.0.sh

# Check status
./check_isaac_sim_status.sh

# Start SLAM
./slam.sh

# Stop SLAM
./stop_slam.sh
```

### Important File Paths
- **Isaac Sim Install:** `~/Downloads/IsaacSim-5.0.0/`
- **Assets:** `~/Downloads/isaacsim/Assets/Isaac/4.2/`
- **Robots:** `~/Downloads/isaacsim/Assets/Isaac/4.2/Isaac/IsaacLab/Robots/`
- **Environments:** `~/Downloads/isaacsim/Assets/Isaac/4.2/Isaac/Environments/`

### ROS2 QoS Values
```python
# Reliability
0 = BEST_EFFORT   # Use for sensors
1 = RELIABLE      # Use for commands

# Durability
0 = VOLATILE
1 = TRANSIENT_LOCAL

# History
0 = KEEP_LAST
1 = KEEP_ALL
```

---

## Additional Resources

- **Isaac Sim Documentation:** https://docs.omniverse.nvidia.com/isaacsim/
- **ROS2 Bridge Documentation:** Search for "omni.isaac.ros2_bridge" in Extensions
- **Action Graph Examples:** Isaac Sim → Examples → Action Graphs
- **Community Forum:** https://forums.developer.nvidia.com/c/omniverse/simulation/69

---

## Changelog

- **2025-11-10:** Updated sensor integration section
  - Replaced ROS2 integration section with sensor-focused content
  - Added detailed sensor addition procedures (Lidar, Camera, Depth, IMU)
  - Added comprehensive action graph setup for sensors
  - Added RViz integration and visualization guide
  - Added QoS settings reference table

- **2025-11-07:** Initial SOP creation
  - Added launch procedures
  - Added USD import methods
  - Added ROS2 integration setup
  - Added troubleshooting from previous sessions
  - Documented QoS configuration issues
  - Included odometry setup procedures
