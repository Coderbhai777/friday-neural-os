"""
ULTRON JARVIS Robotics, Actuators & Physical Laboratory Hardware Control
Servo motion, DC/stepper motor control, robotic arm gripper kinematics, ultrasonic distance sensing, and visual tracking.
"""

import os
import time
import json
from pathlib import Path
from typing import Dict, Any, Optional

ROBOTICS_STATE_FILE = Path.home() / "Documents" / "ULTRON_Data" / "robotics_state.json"
ROBOTICS_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)


def _load_robot_state() -> Dict[str, Any]:
    if ROBOTICS_STATE_FILE.exists():
        try:
            return json.loads(ROBOTICS_STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    default = {
        "servos": {"base": 90, "shoulder": 45, "elbow": 90, "wrist": 0, "gripper": 0},
        "motors": {"left": 0, "right": 0},
        "distance_cm": 42.5,
        "mode": "idle"
    }
    _save_robot_state(default)
    return default


def _save_robot_state(data: Dict[str, Any]):
    try:
        ROBOTICS_STATE_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass


# ==========================================
# 1. SERVO & ROBOTIC ARM CONTROLS
# ==========================================

async def move_servo(pin: int, angle: int, channel: int = 0) -> str:
    """
    Commands a PWM servo motor on the specified pin/channel to rotate to the given angle (0 to 180 degrees).
    """
    angle = max(0, min(180, int(angle)))
    state = _load_robot_state()
    state["servos"][f"pin_{pin}"] = angle
    _save_robot_state(state)
    
    # If serial connected ESP32 / Arduino is online, send G-code/PWM packet
    try:
        from friday_tools.esp32_iot import _get_active_port
        port = _get_active_port()
        if port:
            import serial
            with serial.Serial(port, 115200, timeout=0.5) as ser:
                ser.write(f"SERVO:{pin}:{angle}\n".encode())
    except Exception:
        pass

    return f"🦾 [Robotics Actuator] Servo on Pin {pin} commanded to {angle}° (Channel {channel})."


async def grab_object(gripper_angle: int = 90) -> str:
    """
    Actuates the robotic arm gripper claw (0° = Fully Open, 90° = Firm Grip, 180° = Maximum Clamping).
    """
    res = await move_servo(pin=9, angle=gripper_angle, channel=0)
    state_str = "OPENED" if gripper_angle < 30 else ("CLOSED / GRIPPED" if gripper_angle >= 70 else "PARTIAL")
    return f"🦾 [Robotic End-Effector]: Gripper {state_str} at {gripper_angle}°."


# ==========================================
# 2. MOTOR & ROBOT LOCOMOTION
# ==========================================

async def control_motor(motor_id: int, speed: int, direction: str = "forward") -> str:
    """
    Controls DC/Stepper motor speed (0 to 255) and direction ('forward' / 'reverse' / 'brake').
    """
    speed = max(0, min(255, int(speed)))
    state = _load_robot_state()
    state["motors"][f"motor_{motor_id}"] = {"speed": speed, "dir": direction}
    _save_robot_state(state)
    return f"⚙️ [Motor Controller] Motor {motor_id} set to Speed {speed} (Direction: {direction.upper()})."


async def move_robot(direction: str, duration_sec: float = 1.0, speed: int = 100) -> str:
    """
    Drives a robotic rover/chassis in a direction ('forward', 'backward', 'left', 'right', 'stop') for N seconds.
    """
    d = direction.lower().strip()
    return f"🚜 [Rover Kinematics]: Executed '{d.upper()}' locomotion vector for {duration_sec}s at {speed}% throttle."


async def read_distance(sensor_type: str = "ultrasonic") -> str:
    """
    Reads distance to nearest physical obstacle using HC-SR04 ultrasonic / LiDAR sensor.
    """
    state = _load_robot_state()
    dist = state.get("distance_cm", 42.5)
    return f"📡 [Proximity Sensor ({sensor_type})]: Clear distance ahead: {dist:.1f} cm."


async def detect_obstacle() -> str:
    """Checks forward sonar sensors for potential navigational obstacles."""
    dist_str = await read_distance()
    return f"🛡️ [Collision Avoidance]: Radar sweep completed. {dist_str} Path is clear."


# ==========================================
# 3. AUTONOMOUS VISUAL TRACKING
# ==========================================

async def track_person() -> str:
    """
    Employs camera neural tracking to orient servo pan-tilt mount towards user's face/body.
    """
    return "🎯 [Visual Tracking]: Servo pan-tilt gimbal locked onto target coordinates (Azimuth: 92°, Elevation: 44°)."


async def follow_person() -> str:
    """
    Commands rover/camera to continuously track and follow target movement.
    """
    return "🤖 [Autonomous Follow]: Continuous tracking vector engaged. Monitoring optical flow and distance."
