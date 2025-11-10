# RViz Troubleshooting Guide
## Holonomic Robot SLAM Navigation System

**Version:** 2.0
**Last Updated:** 2025-11-10
**System:** ROS 2 Humble + Isaac Sim Integration

---

## Table of Contents
1. [Quick Start](#quick-start)
2. [Troubleshooting](#troubleshooting)
3. [Known Issues and Limitations](#known-issues-and-limitations)
4. [Diagnostic Commands](#diagnostic-commands)

---

## Quick Start

### Starting the System
```bash
cd /home/george/pointmovement
./slam_full_system.sh
```

### Stopping the System
Press **Ctrl+C** in the terminal, or:
```bash
pkill -f slam_toolbox && pkill -f odom_to_tf && pkill -f holonomic_controller && pkill -f rviz2
```

---

## Troubleshooting

### Issue 1: "frame [map] does not exist" Error

**Symptom:** RViz shows error about missing `map` frame

**Cause:** SLAM Toolbox not running (map frame is created dynamically)

**Solution:**
1. Ensure Isaac Sim is **PLAYING** (not paused)
2. Restart the system:
   ```bash
   ./slam_full_system.sh
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
./slam_full_system.sh
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
   ./slam_full_system.sh --mode rviz
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
   ./slam_full_system.sh
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
- Solution: Ensure you started with `./slam_full_system.sh` (not just RViz mode)
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

## Diagnostic Commands

### Check Topics
```bash
# Check topic publishing rates
ros2 topic hz /odom
ros2 topic hz /scan_lidar
ros2 topic hz /map

# View topic data
ros2 topic echo /odom --once
ros2 topic echo /path --once
ros2 topic echo /cmd_vel

# List all topics
ros2 topic list
```

### Check Nodes
```bash
# List active nodes
ros2 node list

# Check specific nodes
ros2 node list | grep slam
ros2 node list | grep controller
```

### Check TF Frames
```bash
# Generate TF tree diagram
ros2 run tf2_tools view_frames

# Check specific transform
ros2 run tf2_ros tf2_echo map odom
ros2 run tf2_ros tf2_echo odom sim_camera
```

### Rebuild System
If you need to rebuild after making changes:
```bash
cd /home/george/pointmovement
./build.sh
source install/setup.bash
```

---

## Notes

**System is Pre-Configured:** All RViz displays, plugins, and launch configurations are set up by default. Simply run `./slam_full_system.sh` to start the entire system.

**For Detailed Setup Information:** Refer to the original documentation files:
- `README_SLAM.md` - SLAM integration details
- `INTERACTIVE_PATH_EDITOR.md` - Path editor usage
- `CLAUDE.md` - Developer documentation

---

**End of Troubleshooting Guide**
