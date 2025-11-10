# Standard Operating Procedure (SOP)
## Holonomic Robot SLAM Navigation System

**Version:** 1.0
**Last Updated:** 2025-11-07
**System:** ROS 2 Humble + Isaac Sim Integration

---

## Table of Contents
1. [System Overview](#system-overview)
2. [Prerequisites](#prerequisites)
3. [System Architecture](#system-architecture)
4. [Startup Procedure](#startup-procedure)
5. [Operating Instructions](#operating-instructions)
6. [Common Workflows](#common-workflows)
7. [Troubleshooting](#troubleshooting)
8. [Shutdown Procedure](#shutdown-procedure)
9. [Known Issues and Limitations](#known-issues-and-limitations)

---

## System Overview

This system provides **autonomous navigation for a holonomic (Mecanum wheel) robot** using SLAM (Simultaneous Localization and Mapping) for real-time map building and a proportional controller for path following.

### Key Capabilities
- **Real-time SLAM mapping** using lidar sensor data
- **Interactive path planning** via RViz2 graphical interface
- **Autonomous navigation** with holonomic (omnidirectional) movement
- **Live path editing** with 5-mode Interactive Path Tool
- **Multiple operational modes** for different use cases

### System Components
1. **Isaac Sim** - Physics simulation environment
2. **SLAM Toolbox** - Map building and localization
3. **Holonomic Controller** - Path following and motion control
4. **Interactive Path Tool** - RViz plugin for waypoint creation
5. **TF Bridge** - Coordinate frame transformation system

---

## Prerequisites

### Software Requirements
- **Operating System:** Ubuntu 22.04 LTS
- **ROS 2:** Humble Hawksbill
- **Isaac Sim:** Latest version with robot configured
- **Python:** 3.10+
- **Required ROS 2 Packages:**
  - `slam_toolbox`
  - `rviz2`
  - `tf2_ros`
  - `geometry_msgs`
  - `nav_msgs`
  - `sensor_msgs`

### Robot Configuration in Isaac Sim
Your robot **must** publish the following topics:
- `/odom` (nav_msgs/Odometry) - Robot position and velocity
- `/scan_lidar` (sensor_msgs/LaserScan) - Lidar scan data

**Required TF Frames:**
- `map` → `odom` → `sim_camera` (or your robot's base frame)

### Workspace Setup
Ensure the workspace is built:
```bash
cd /home/george/pointmovement
./build.sh
```

### File Verification
Verify these key files exist:
- `/home/george/odom_to_tf_bridge_sim_camera.py` - TF bridge script
- `/home/george/pointmovement/run_navigation.sh` - Unified launcher
- `/home/george/pointmovement/slam_rviz_config.rviz` - RViz configuration

---

## System Architecture

### Data Flow
```
Isaac Sim → /odom + /scan_lidar
    ↓
SLAM Toolbox → /map frame + /map topic
    ↓
Interactive Path Tool → /path topic (waypoints)
    ↓
Holonomic Controller → /cmd_vel (velocity commands)
    ↓
Isaac Sim (robot movement)
```

### Coordinate Frames
- **map**: Global reference frame (created by SLAM)
- **odom**: Odometry frame (drift-prone, from wheel encoders)
- **sim_camera**: Robot base frame (your robot's reference point)

### Key Topics
| Topic | Type | Purpose |
|-------|------|---------|
| `/odom` | nav_msgs/Odometry | Robot position/velocity from Isaac Sim |
| `/scan_lidar` | sensor_msgs/LaserScan | Lidar data for SLAM mapping |
| `/map` | nav_msgs/OccupancyGrid | 2D occupancy grid map |
| `/path` | nav_msgs/Path | Waypoints for robot to follow |
| `/cmd_vel` | geometry_msgs/Twist | Velocity commands to robot |
| `/path_markers` | visualization_msgs/MarkerArray | Path visualization |

---

## Startup Procedure

### Step 1: Start Isaac Sim
1. Launch Isaac Sim application
2. Load your robot scene/scenario
3. **Press PLAY** to start simulation
4. Verify robot is publishing data:
   ```bash
   ros2 topic hz /odom
   ros2 topic hz /scan_lidar
   ```
   Both should show publishing rates (e.g., 20-60 Hz)

### Step 2: Choose Operational Mode

The system supports **three operational modes**:

#### Mode 1: Full Navigation (RECOMMENDED)
**Use when:** You want autonomous path following with live mapping

```bash
cd /home/george/pointmovement
./run_navigation.sh
# or explicitly:
./run_navigation.sh --mode navigation
```

**What starts:**
- TF Bridge (odom → sim_camera transform)
- SLAM Toolbox (map building)
- Holonomic Controller (path following)
- RViz2 (visualization + path planning)

#### Mode 2: Mapping Only
**Use when:** You want to build a map without autonomous movement

```bash
./run_navigation.sh --mode mapping
```

**What starts:**
- TF Bridge
- SLAM Toolbox
- RViz2 (visualization + path planning)
- **No Controller** - Robot must be moved manually

#### Mode 3: RViz Only
**Use when:** SLAM is already running in another terminal

```bash
./run_navigation.sh --mode rviz
```

**What starts:**
- RViz2 only

### Step 3: Verify Startup
After launching, you should see:
```
========================================"
✅ Full Navigation System Started!
========================================"
Process IDs:
  TF Bridge:  12345
  SLAM:       12346
  Controller: 12347
  RViz2:      12348
```

**Check for warnings:**
- `⚠ WARNING: /odom not publishing` → Isaac Sim not playing
- `⚠ WARNING: /scan_lidar not publishing` → Lidar not configured
- `⚠ WARNING: Controller failed to start` → Workspace not sourced

**RViz Controls Available:**
- **Interactive Path Tool** - Click 'i' to activate waypoint placement
- **Path Editor Panel** - Right side panel with controls:
  - Linear/Angular Velocity sliders
  - Save/Load Path buttons
  - **Save Map button** - Export current SLAM map
  - Upload Map button - Load pre-existing maps

---

## Operating Instructions

### Using the Interactive Path Tool

#### Activating the Tool
1. In RViz, press **`i`** (lowercase) on your keyboard
2. Or click the **Interactive Path Tool** button in the toolbar
3. Tool should highlight/activate (you'll see cursor change)

#### 5 Operational Modes

The Interactive Path Tool has **5 modes** accessible via buttons in the Path Editor Panel (right side):

##### 1. Add Mode (Default)
- **Purpose:** Add new waypoints
- **Usage:** Left-click anywhere on the map to create a waypoint
- **Visual:** Waypoints appear as spheres with numbers
- **Auto-connect:** New waypoints automatically connect in sequence

##### 2. Move Mode
- **Purpose:** Reposition existing waypoints
- **Usage:** Left-click and drag a waypoint to new position
- **Live update:** Path recalculates as you drag
- **Use case:** Fine-tune path without recreating it

##### 3. Delete Mode
- **Purpose:** Remove individual waypoints
- **Usage:** Left-click on a waypoint to delete it
- **Auto-reconnect:** Path reconnects around deleted waypoint

##### 4. Connect Mode
- **Purpose:** Create custom connections between waypoints
- **Usage:**
  1. Left-click on first waypoint (becomes highlighted)
  2. Left-click on second waypoint
  3. Connection is created
- **Use case:** Create complex paths or loops

##### 5. Delete Connection Mode
- **Purpose:** Remove specific connections between waypoints
- **Usage:**
  1. Left-click on first waypoint of connection
  2. Left-click on second waypoint of connection
  3. Connection is removed
- **Use case:** Break loops or remove unwanted paths

#### Additional Controls
- **Right-click anywhere:** Clear all waypoints and stop robot
- **Auto-Loop checkbox:** Automatically connect last waypoint to first
- **Velocity slider:** Adjust robot speed (0.1 - 2.0 m/s)

### Robot Behavior (Navigation Mode)

**When waypoints are added:**
1. Robot receives waypoint list via `/path` topic
2. Controller calculates velocity commands
3. Robot autonomously moves to each waypoint in sequence
4. When reaching a waypoint, proceeds to next automatically

**Movement characteristics:**
- **Holonomic movement:** Can move in any direction without rotating
- **Strafing:** Can move sideways (left/right) directly
- **Position tolerance:** 0.1 meters (configurable)
- **Orientation tolerance:** 0.1 radians (configurable)

**To stop the robot:**
- Right-click in RViz to clear path
- Or press Ctrl+C in the launch terminal

---

## Common Workflows

### Workflow 1: Building and Saving a Map
**Objective:** Create and save a 2D map of the environment

1. Start in **mapping mode**:
   ```bash
   ./run_navigation.sh --mode mapping
   ```

2. Manually drive the robot around the environment:
   - Use Isaac Sim controls or teleop keyboard
   - Move slowly for better map quality
   - Ensure lidar can see walls/obstacles

3. Watch the map appear in RViz `/map` display

4. **Save the map using RViz (RECOMMENDED):**
   - In the Path Editor Panel (right side), click **"Save Map"** button
   - A file dialog will appear
   - Enter a name for your map (e.g., `my_warehouse_map`)
   - **Do NOT add file extensions** - they will be added automatically
   - Click "Save"
   - The system will create two files:
     - `my_warehouse_map.yaml` (map metadata)
     - `my_warehouse_map.pgm` (map image)
   - A confirmation dialog will appear when successful

5. **Alternative: Save via command line:**
   ```bash
   ros2 run nav2_map_server map_saver_cli -f my_map
   ```

### Workflow 2: Autonomous Navigation
**Objective:** Have robot follow a planned path

1. Start in **navigation mode** (default):
   ```bash
   ./run_navigation.sh
   ```

2. Wait for map to build (drive robot around if new environment)

3. Press **`i`** to activate Interactive Path Tool

4. Click on map to add waypoints:
   - Click near robot for first waypoint
   - Add subsequent waypoints to create path
   - Robot starts moving immediately

5. Observe autonomous navigation:
   - Robot follows waypoints in order
   - Uses holonomic movement (can strafe)
   - Completes path automatically

6. To stop: Right-click to clear path

### Workflow 3: Complex Path Planning
**Objective:** Create custom paths with loops and branches

1. Start system and add initial waypoints in **Add Mode**

2. Switch to **Connect Mode** to create custom connections:
   - Click waypoint 5, then waypoint 2 to create a shortcut
   - Create loops by connecting last to first

3. Switch to **Move Mode** to fine-tune positions:
   - Drag waypoints to better locations
   - Avoid obstacles or walls

4. Switch to **Delete Connection Mode** to remove unwanted paths:
   - Break loops if needed
   - Remove incorrect connections

5. Use **Delete Mode** to remove unnecessary waypoints

6. Test the path by watching robot navigate

### Workflow 4: Adjusting Robot Speed

1. Locate **Path Editor Panel** on right side of RViz

2. Find **Linear Velocity** slider

3. Adjust slider:
   - Left (slower): 0.1 m/s
   - Right (faster): 2.0 m/s
   - Default: 0.5 m/s

4. Speed applies to current and future movements

---

## Troubleshooting

### Issue 1: "frame [map] does not exist" Error

**Symptom:** RViz shows error about missing `map` frame

**Cause:** SLAM Toolbox not running (map frame is created dynamically)

**Solution:**
1. Ensure Isaac Sim is **PLAYING** (not paused)
2. Restart the system:
   ```bash
   ./run_navigation.sh
   ```
3. Wait 3-5 seconds for SLAM to initialize
4. Check if `/map` topic is publishing:
   ```bash
   ros2 topic echo /map --once
   ```

### Issue 2: Robot Won't Move

**Symptom:** Waypoints added but robot stays still

**Possible Causes & Solutions:**

**A. Controller not running**
```bash
ros2 node list | grep controller
```
Should show `/controller_node`. If not, restart in navigation mode.

**B. No odometry data**
```bash
ros2 topic hz /odom
```
Should show publishing rate. If not, check Isaac Sim is PLAYING.

**C. Path not published**
```bash
ros2 topic echo /path --once
```
Should show waypoints. If not, try clicking waypoints again.

**D. Velocity commands not reaching robot**
```bash
ros2 topic echo /cmd_vel
```
Should show non-zero velocities when waypoint is active.

### Issue 3: Robot Moves Wrong Direction

**Symptom:** Clicking left makes robot go right, or vice versa

**Cause:** This was a bug related to obstacle avoidance (now fixed)

**Solution:** Ensure you're using the latest controller:
```bash
cd /home/george/pointmovement
./build.sh
source install/setup.bash
./run_navigation.sh
```

**Verification:**
- Click to the LEFT of robot → robot should strafe LEFT
- Click to the RIGHT of robot → robot should strafe RIGHT

### Issue 4: RViz Plugin Not Appearing

**Symptom:** Interactive Path Tool not in toolbar

**Cause:** Plugin library not found or workspace not sourced

**Solution:**
1. Verify plugin library exists:
   ```bash
   ls -l /home/george/pointmovement/install/path_editor_rviz_plugin/lib/libpath_editor_rviz_plugin.so
   ```

2. Rebuild workspace:
   ```bash
   cd /home/george/pointmovement
   ./build.sh
   ```

3. Restart RViz:
   ```bash
   pkill -f rviz2
   ./run_navigation.sh --mode rviz
   ```

### Issue 5: SLAM Not Creating Map

**Symptom:** `/map` topic exists but no map appears

**Possible Causes & Solutions:**

**A. No lidar data**
```bash
ros2 topic echo /scan_lidar --once
```
Should show scan ranges. If not, check Isaac Sim lidar configuration.

**B. Robot not moving**
SLAM requires motion to build map. Drive robot around.

**C. Lidar range too short**
Check lidar max_range in Isaac Sim (should be 5-20 meters).

**D. Static environment needed**
SLAM works best with static obstacles (walls, furniture).

### Issue 6: System Crashes on Restart

**Symptom:** After PC restart, launching script fails

**Cause:** Stale processes from previous session

**Solution:**
1. Kill all ROS 2 processes:
   ```bash
   pkill -9 -f ros2
   pkill -9 -f slam_toolbox
   pkill -9 -f rviz2
   ```

2. Clean environment and restart:
   ```bash
   cd /home/george/pointmovement
   ./run_navigation.sh
   ```

### Issue 7: TF Transform Errors

**Symptom:** Error messages like "Lookup would require extrapolation into the past"

**Cause:** Time synchronization issues between nodes

**Solution:**
1. Ensure all nodes use `use_sim_time:=true`
2. Restart Isaac Sim (reset simulation time)
3. Restart navigation system
4. These messages are often transient during startup (can be ignored if system works)

### Issue 8: Cannot Save Map from RViz

**Symptom:** "Save Map" button shows error or does nothing

**Possible Causes & Solutions:**

**A. SLAM Toolbox not running**
- Error message: "SLAM Toolbox service not available - is SLAM running?"
- Solution: Ensure you started with `./run_navigation.sh` (not just RViz mode)
- Verify SLAM is running:
  ```bash
  ros2 node list | grep slam
  ```

**B. Service timeout**
- Error message: "Map save timeout - service took too long"
- Solution: Map is large and still saving. Wait and check the specified directory for files.

**C. Permission denied**
- Map fails to save to specified location
- Solution: Choose a directory where you have write permissions (e.g., home directory)

**D. File already exists**
- Solution: Use a different filename or delete the existing map files first

---

## Shutdown Procedure

### Clean Shutdown

**Method 1: From Launch Terminal**
1. Press **Ctrl+C** in the terminal running `run_navigation.sh`
2. Script will automatically kill all child processes
3. Wait for "Stopping all processes..." message

**Method 2: Manual Kill**
```bash
# Use PIDs shown at startup
kill <TF_BRIDGE_PID> <SLAM_PID> <CONTROLLER_PID> <RVIZ_PID>

# Or kill by process name
pkill -f slam_toolbox
pkill -f odom_to_tf
pkill -f holonomic_controller
pkill -f rviz2
```

### Emergency Shutdown

If system becomes unresponsive:
```bash
pkill -9 -f slam_toolbox
pkill -9 -f odom_to_tf
pkill -9 -f holonomic_controller
pkill -9 -f rviz2
```

### Stopping Isaac Sim

1. Click **STOP** button in Isaac Sim
2. Close Isaac Sim application
3. This will stop all topic publications

---

## Known Issues and Limitations

### 1. Obstacle Avoidance Disabled

**Status:** Intentionally disabled in current version

**Reason:** Obstacle avoidance was interfering with holonomic strafing movements, causing left/right inversion.

**Implication:** Robot will **not** automatically avoid obstacles in its path.

**Workaround:**
- Manually plan paths that avoid obstacles
- Use Interactive Path Tool to route around walls
- Monitor robot during autonomous operation

**Future:** May be re-enabled with coordinate frame fix.

### 2. Path Clearing Latency

**Symptom:** After right-clicking to clear path, robot may continue moving briefly

**Cause:** Controller processes a few more commands before receiving empty path message

**Workaround:** Wait 1-2 seconds after clearing path before adding new waypoints

### 3. SLAM Drift Over Time

**Symptom:** Map becomes misaligned after extended operation (30+ minutes)

**Cause:** Accumulated odometry error without loop closure

**Workaround:**
- Restart SLAM periodically
- Drive robot through previously mapped areas (helps loop closure)
- Use shorter navigation sessions

### 4. RViz Crashes with Large Maps

**Symptom:** RViz becomes unresponsive with very large maps (> 1000x1000 cells)

**Cause:** RViz rendering overhead

**Workaround:**
- Limit exploration area
- Increase `map_update_interval` parameter in launch script
- Reduce SLAM resolution (add `-p resolution:=0.1` to SLAM parameters)

### 5. Coordinate Frame Dependencies

**Critical:** System assumes `sim_camera` is the robot's base frame.

**If your robot uses a different frame:**
1. Edit `/home/george/odom_to_tf_bridge_sim_camera.py`
2. Change `child_frame_id = 'sim_camera'` to your frame name
3. Edit `run_navigation.sh`, change `-p base_frame:=sim_camera` to your frame
4. Rebuild and restart

### 6. No Multi-Robot Support

**Limitation:** System is designed for single-robot operation.

**For multi-robot:** Would require namespace separation and multiple controller instances.

---

## Support and Contact

For issues or questions:
1. Check this SOP first
2. Review logs in terminal where system was launched
3. Check ROS 2 topics and TF tree:
   ```bash
   ros2 topic list
   ros2 run tf2_tools view_frames
   ```
4. Refer to detailed documentation:
   - `README_SLAM.md` - SLAM integration guide
   - `INTERACTIVE_PATH_EDITOR.md` - Path editor details
   - `CLAUDE.md` - Developer documentation

---

## Understanding the Launch Scripts

This section explains how the navigation and SLAM launch scripts work, making it easier for future developers to maintain and modify them.

### Overview of Launch Scripts

The system includes three main launch scripts:

1. **`run_navigation.sh`** - Unified launcher with three modes (recommended)
2. **`slam_with_rviz.sh`** - SLAM + RViz only (legacy, but still functional)
3. **`launch_slam_rviz.sh`** - RViz only (when SLAM already running)

### Main Script: `run_navigation.sh`

This is the primary launch script that provides three operational modes:

#### Script Structure

**1. Mode Selection & Argument Parsing (Lines 22-71)**

The script accepts a `--mode` parameter with three values:
- `navigation` - Full system with autonomous control (DEFAULT)
- `mapping` - SLAM + RViz without controller (for map building)
- `rviz` - RViz only (assumes SLAM already running)

```bash
./run_navigation.sh                    # Full navigation (default)
./run_navigation.sh --mode mapping     # SLAM mapping only
./run_navigation.sh --mode rviz        # RViz only
```

**2. RViz-Only Mode Branch (Lines 76-124)**

If `--mode rviz` is selected, the script:
- Kills any existing RViz processes
- Sources the workspace to load custom plugins
- Launches RViz with the pre-configured SLAM config file
- Exits (doesn't continue to SLAM startup)

This mode is useful when you already have SLAM running in another terminal and just want to restart RViz.

**3. Process Cleanup (Lines 145-152)**

```bash
pkill -9 -f slam_toolbox
pkill -9 -f odom_to_tf
pkill -9 -f holonomic_controller
pkill -9 -f rviz2
```

**Why this matters:** Killing old processes prevents conflicts from stale nodes that may be using the same topic names or node names. The `-9` flag (`SIGKILL`) ensures processes are forcefully terminated.

**4. TF Bridge Startup (Lines 155-164)**

```bash
python3 /home/george/odom_to_tf_bridge_sim_camera.py --ros-args -p use_sim_time:=true &
```

**What it does:**
- Converts `/odom` topic (nav_msgs/Odometry) into TF transforms
- Creates the `odom → sim_camera` transform in the TF tree
- Uses simulation time from Isaac Sim (`use_sim_time:=true`)

**Why it's first:** The TF bridge must start before SLAM because SLAM needs the `odom` frame to exist in the TF tree. Without this transform, SLAM cannot localize the robot.

**5. Data Verification (Lines 167-180)**

```bash
timeout 3 ros2 topic hz /odom 2>&1 | grep -q "average rate"
timeout 3 ros2 topic hz /scan_lidar 2>&1 | grep -q "average rate"
```

**What it does:**
- Checks if Isaac Sim is publishing odometry and lidar data
- Uses `timeout 3` to wait maximum 3 seconds
- Displays warnings if data is not available

**Why this matters:** These checks alert you early if Isaac Sim is not running or not connected, preventing confusing errors later.

**6. SLAM Toolbox Startup (Lines 183-205)**

```bash
ros2 run slam_toolbox async_slam_toolbox_node \
    --ros-args \
    -p use_sim_time:=true \
    -p base_frame:=sim_camera \
    -p odom_frame:=odom \
    -p map_frame:=map \
    -p scan_topic:=/scan_lidar \
    -p minimum_travel_distance:=0.1 \
    -p minimum_travel_heading:=0.1 \
    -p map_update_interval:=2.0 &
```

**Parameter breakdown:**
- `use_sim_time:=true` - Use Isaac Sim's simulation clock instead of system time
- `base_frame:=sim_camera` - The robot's base coordinate frame (your robot's reference point)
- `odom_frame:=odom` - The odometry frame (from wheel encoders, drift-prone)
- `map_frame:=map` - Global map frame created by SLAM (drift-free)
- `scan_topic:=/scan_lidar` - Which topic to read lidar data from
- `minimum_travel_distance:=0.1` - Robot must move 0.1m before updating map (prevents noise)
- `minimum_travel_heading:=0.1` - Robot must rotate 0.1 rad before updating map
- `map_update_interval:=2.0` - Publish map every 2 seconds (reduces CPU load)

**Why these values:**
- Smaller `minimum_travel_distance` = more frequent updates but more CPU usage
- Larger `map_update_interval` = less network traffic but less responsive visualization

**7. Workspace Sourcing (Lines 208-211)**

```bash
source /opt/ros/humble/setup.bash
source /home/george/pointmovement/install/setup.bash
```

**What it does:**
- Loads ROS 2 core packages (first line)
- Loads custom workspace packages and plugins (second line)

**Why this matters:** Without sourcing the workspace, ROS 2 cannot find:
- The `holonomic_controller` package
- The `path_editor_rviz_plugin` library
- Custom launch files and configurations

**8. Controller Startup (Lines 214-229, Navigation Mode Only)**

```bash
ros2 run holonomic_controller controller_node --ros-args -p use_sim_time:=true &
```

**What it does:**
- Subscribes to `/odom` for robot position
- Subscribes to `/path` for waypoints from path editor
- Publishes `/cmd_vel` velocity commands to move the robot
- Implements proportional control with Mecanum wheel inverse kinematics

**Why it's conditional:** In mapping mode, you manually control the robot to build a map. The controller is only needed in navigation mode for autonomous movement.

**9. RViz Startup (Lines 232-251)**

```bash
ros2 run rviz2 rviz2 -d "$RVIZ_CONFIG" --ros-args -p use_sim_time:=true &
```

**What it does:**
- Launches RViz with the pre-configured file `slam_rviz_config.rviz`
- The config file includes:
  - Fixed frame set to `map`
  - Map display (`/map` topic)
  - LaserScan display (`/scan_lidar` topic)
  - TF frame visualization
  - Interactive Path Tool (custom plugin)
  - Path Editor Panel (custom panel)

**Why it's last:** RViz needs all the other components running so it can subscribe to their topics (`/map`, `/scan_lidar`, etc.) and visualize them immediately.

**10. Status Display & Process Management (Lines 257-322)**

The script displays:
- All process IDs (so you can kill individual processes if needed)
- Current operational mode
- Usage instructions
- How to stop the system

**Trap for cleanup:**
```bash
trap "echo 'Stopping all processes...'; kill $BRIDGE_PID $SLAM_PID $CONTROLLER_PID $RVIZ_PID 2>/dev/null; exit 0" SIGINT SIGTERM
```

This ensures that pressing Ctrl+C kills all child processes cleanly, preventing orphaned nodes.

### Startup Order: Why It Matters

The components **must** start in this specific order:

```
1. TF Bridge       → Creates odom→sim_camera transform
2. SLAM Toolbox    → Needs odom frame to exist, creates map frame
3. Controller      → Needs odom topic and can publish to /cmd_vel
4. RViz            → Visualizes everything (needs all topics active)
```

**If you start them in wrong order:**
- SLAM before TF bridge → Error: "Frame odom does not exist"
- RViz before SLAM → Warning: "Waiting for /map topic..." (recovers when SLAM starts)
- Controller before SLAM → Works, but no map to visualize paths on

### Key Configuration Files

**`slam_rviz_config.rviz`** (Line 94, 233)
- Contains all display configurations
- Loads the custom path editor plugin
- Sets fixed frame to `map`
- Pre-configures topic names

**`/home/george/odom_to_tf_bridge_sim_camera.py`** (Line 156, 161)
- Python script that bridges `/odom` topic to TF
- Critical for SLAM to work
- Must specify correct child frame (`sim_camera` for this robot)

### Common Modifications

**To change robot speed:**
Edit the controller parameters in `src/holonomic_controller/config/controller_params.yaml`, then rebuild.

**To use a different robot base frame:**
1. Change `base_frame:=sim_camera` to your frame name (line 187)
2. Edit `/home/george/odom_to_tf_bridge_sim_camera.py` to publish to your frame

**To adjust SLAM sensitivity:**
- Decrease `minimum_travel_distance` for more frequent updates (more CPU)
- Increase `map_update_interval` to reduce network load

**To add another component:**
Add it between controller and RViz (lines 230-231), following the pattern:
```bash
ros2 run your_package your_node --ros-args -p use_sim_time:=true &
YOUR_PID=$!
sleep 2
```

### Troubleshooting the Scripts

**Script exits immediately:**
- Check if file has execute permissions: `chmod +x run_navigation.sh`
- Verify Isaac Sim is running: `ros2 topic list` should show `/odom` and `/scan_lidar`

**"Command not found" errors:**
- ROS 2 not sourced: Run `source /opt/ros/humble/setup.bash`
- Workspace not built: Run `./build.sh` first

**Processes keep running after Ctrl+C:**
- The trap may have failed. Manually kill: `pkill -9 -f slam_toolbox`
- Check with: `ps aux | grep ros2`

**RViz doesn't show custom plugins:**
- Workspace not sourced before launching RViz
- Plugin library not built: Check `install/path_editor_rviz_plugin/lib/libpath_editor_rviz_plugin.so` exists
- Run `./build.sh` to rebuild plugins

---

## Appendix: Quick Reference Commands

### System Control
```bash
# Start full navigation (default)
./run_navigation.sh

# Start mapping only
./run_navigation.sh --mode mapping

# Start RViz only
./run_navigation.sh --mode rviz

# Show help
./run_navigation.sh --help

# Stop all processes
pkill -f slam_toolbox && pkill -f odom_to_tf && pkill -f holonomic_controller && pkill -f rviz2
```

### Map Management
```bash
# Save map from RViz (PREFERRED METHOD)
# - Click "Save Map" button in Path Editor Panel
# - Or use command line:
ros2 service call /slam_toolbox/save_map slam_toolbox/srv/SaveMap "{name: {data: '/path/to/my_map'}}"

# Load existing map (Upload Map button in RViz)
# - Click "Upload Map" button in Path Editor Panel
# - Select .yaml file from file dialog
```

### Diagnostics
```bash
# Check topic publishing rates
ros2 topic hz /odom
ros2 topic hz /scan_lidar
ros2 topic hz /map

# View topic data
ros2 topic echo /odom --once
ros2 topic echo /path --once
ros2 topic echo /cmd_vel

# List active nodes
ros2 node list

# Check TF frames
ros2 run tf2_tools view_frames
ros2 run tf2_echo map odom
```

### Rebuild System
```bash
cd /home/george/pointmovement
./build.sh
source install/setup.bash
```

---

**End of SOP**
