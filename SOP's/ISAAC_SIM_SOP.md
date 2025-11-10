# Isaac Sim 5.0.0 - Standard Operating Procedure

## Table of Contents
1. [Launching Isaac Sim](#launching-isaac-sim)
2. [Importing a Robot from USD](#importing-a-robot-from-usd)
3. [Setting Up ROS2 Integration](#setting-up-ros2-integration)
4. [Troubleshooting & Diagnostics](#troubleshooting--diagnostics)
5. [Common Issues & Solutions](#common-issues--solutions)

---

## Launching Isaac Sim

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

### 3.1: Drag and drop ###
1. Find the usd of rossmasterx3 (e.g., `/home/george/Downloads/Rossmasterx3.usd`)
2. Drag and drop into `stage` in Isaac sim
### 3.2: GUI ###
1. **Create → Reference** or press `Ctrl+Shift+R`
2. Navigate to your robot's USD file location
3. Select the USD file (e.g., `/home/george/Downloads/Rossmasterx3.usd`)
4. Click **Open**

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

## Setting Up ROS2 Integration

### Enable ROS2 Bridge Extension

#### GUI Method:
1. **Window → Extensions**
2. Search: "ROS2 Bridge"
3. Enable: **omni.isaac.ros2_bridge**

#### Python Method:
```python
from omni.isaac.core.utils.extensions import enable_extension
enable_extension("omni.isaac.ros2_bridge")
```

### Setting Up Action Graphs for ROS2

#### Step 1: Open Action Graph Editor
**Window → Visual Scripting → Action Graph**

#### Step 2: Create New Action Graph
1. Click **New Action Graph**
2. Name it: `RobotActionGraph`
3. Set path: `/World/Robot/ActionGraph`

#### Step 3: Add Essential Nodes

**Basic ROS2 Publishing Setup:**

1. **On Playback Tick** (trigger node)
   - Already present in most graphs
   - Fires every simulation frame

2. **ROS2 Context** (required for all ROS2 nodes)
   - Path: `ROS2 → Context → ROS2 Context`
   - Domain ID: 0 (default)
   - Node Name: `isaac_sim_node`

3. **ROS2 Publish Laser Scan** (for LiDAR)
   - Path: `ROS2 → Publishers → ROS2 Publish Laser Scan`
   - Topic Name: `/scan`
   - Frame ID: `sim_camera` or `laser_frame`
   - **QoS Profile**:
     - Reliability: `BEST_EFFORT` (⚠️ IMPORTANT for SLAM)
     - Durability: `VOLATILE`
     - History: `KEEP_LAST`

4. **ROS2 Publish Odometry** (for robot motion)
   - Path: `ROS2 → Publishers → ROS2 Publish Odometry`
   - Topic Name: `/odom`
   - Frame ID (odom): `odom`
   - Frame ID (robot): `base_link` or `sim_camera`

5. **ROS2 Publish Transform Tree** (for TF tree)
   - Path: `ROS2 → Publishers → ROS2 Publish Transform Tree`
   - Target Prims: Path to robot root
   - Parent Frame: `odom`

#### Step 4: Connect Nodes
1. Connect **On Playback Tick → execIn** to each ROS2 publisher
2. Connect **ROS2 Context → context** to each ROS2 node

#### Step 5: Configure QoS Settings (Critical!)

**For SLAM Compatibility:**
All sensor publishers (Laser Scan, Point Cloud) must use:
- **Reliability: BEST_EFFORT**
- **Durability: VOLATILE**
- **History: KEEP_LAST**

**Why?** SLAM Toolbox and other ROS2 SLAM nodes require BEST_EFFORT QoS. Default RELIABLE setting causes subscription mismatches.

### Python Action Graph Setup

```python
import omni.graph.core as og

graph_path = "/World/Robot/ActionGraph"
keys = og.Controller.Keys

# Create action graph
og.Controller.edit(
    {"graph_path": graph_path, "evaluator_name": "execution"},
    {
        keys.CREATE_NODES: [
            ("OnPlaybackTick", "omni.graph.action.OnPlaybackTick"),
            ("ROS2Context", "omni.isaac.ros2_bridge.ROS2Context"),
            ("PublishScan", "omni.isaac.ros2_bridge.ROS2PublishLaserScan"),
            ("PublishOdom", "omni.isaac.ros2_bridge.ROS2PublishOdometry"),
            ("PublishTF", "omni.isaac.ros2_bridge.ROS2PublishTransformTree"),
        ],
        keys.SET_VALUES: [
            # ROS2 Context
            ("ROS2Context.inputs:domain_id", 0),
            ("ROS2Context.inputs:useDomainIDEnvVar", False),

            # Laser Scan Publisher
            ("PublishScan.inputs:topicName", "/scan"),
            ("PublishScan.inputs:frameId", "sim_camera"),
            ("PublishScan.inputs:qosProfile.reliability", 0),  # 0=BEST_EFFORT

            # Odometry Publisher
            ("PublishOdom.inputs:topicName", "/odom"),
            ("PublishOdom.inputs:odomFrameId", "odom"),
            ("PublishOdom.inputs:robotFrameId", "base_link"),

            # TF Publisher
            ("PublishTF.inputs:topicName", "/tf"),
            ("PublishTF.inputs:parentFrame", "odom"),
        ],
        keys.CONNECT: [
            ("OnPlaybackTick.outputs:tick", "PublishScan.inputs:execIn"),
            ("OnPlaybackTick.outputs:tick", "PublishOdom.inputs:execIn"),
            ("OnPlaybackTick.outputs:tick", "PublishTF.inputs:execIn"),
            ("ROS2Context.outputs:context", "PublishScan.inputs:context"),
            ("ROS2Context.outputs:context", "PublishOdom.inputs:context"),
            ("ROS2Context.outputs:context", "PublishTF.inputs:context"),
        ],
    },
)
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

- **2025-11-07:** Initial SOP creation
  - Added launch procedures
  - Added USD import methods
  - Added ROS2 integration setup
  - Added troubleshooting from previous sessions
  - Documented QoS configuration issues
  - Included odometry setup procedures
