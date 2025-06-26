import numpy as np
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Physical constants
GRAVITY = 9.81  # m/s^2
RHO_STEEL = 7850  # kg/m^3
RHO_ALUMINUM = 2700  # kg/m^3
PIVOT_OFFSET = -0.07  # Distance from arm center to pivot

app = FastAPI()

# Allow CORS for local development or cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SimulationReq(BaseModel):
    motor_torque: float
    start_angle: float
    release_angle: float
    max_omega: float
    arm_length: float
    arm_radius: float
    ball_radius: float


class InverseReq(BaseModel):
    distance: float
    angle_deg: float = 45.0
    spin_up_time: float = 1.0
    arm_length: float
    arm_radius: float
    ball_radius: float


def calc_launcher_inertia(
    arm_length: float, arm_radius: float, ball_radius: float
) -> float:
    """
    Calculate the moment of inertia of the arm and the ball about the pivot,
    given arm length, arm radius, and ball radius.
    """
    # Volume and mass of the arm (cylindrical segment)
    arm_volume = np.pi * (arm_radius**2) * arm_length
    arm_mass = RHO_ALUMINUM * arm_volume

    # Inertia of a uniform rod about its center: (1/12) m L^2
    # Apply parallel axis theorem for pivot offset
    I_arm_cm = (1.0 / 12.0) * arm_mass * (arm_length**2)
    I_arm = I_arm_cm + arm_mass * (PIVOT_OFFSET**2)

    # Volume and mass of the ball (sphere)
    ball_volume = (4.0 / 3.0) * np.pi * (ball_radius**3)
    ball_mass = RHO_STEEL * ball_volume

    # Assumes the ball is near the far end of the arm, offset by 0.03 from the tip
    # so that if arm_length=0.2, position=0.17 matches original code
    ball_position = arm_length - 0.03
    if ball_position < 0:
        # Fallback or clamp: if geometry leads to negative position, set to something non-negative
        ball_position = 0.0

    I_ball = ball_mass * (ball_position**2)
    return I_arm + I_ball


def simulate_launch(req: SimulationReq):
    """
    Simulate a launch given motor torque, angles, max omega, and geometry.
    Returns launch velocity components, flight distance, flight time, etc.
    """
    # Extract request data
    motor_torque = req.motor_torque
    start_angle = req.start_angle
    release_angle = req.release_angle
    max_omega = req.max_omega
    arm_length = req.arm_length
    arm_radius = req.arm_radius
    ball_radius = req.ball_radius

    # Compute inertia
    inertia = calc_launcher_inertia(arm_length, arm_radius, ball_radius)
    alpha = motor_torque / inertia if inertia else 0.0
    spin_up_time = max_omega / alpha if alpha else 0.0

    # Ball position is derived from arm_length
    ball_position = arm_length - 0.03
    if ball_position < 0:
        ball_position = 0.0

    # Compute launch velocity
    release_angle_rad = np.radians(release_angle)
    launch_velocity = max_omega * ball_position
    vx = launch_velocity * np.cos(release_angle_rad)
    vy = launch_velocity * np.sin(release_angle_rad)

    # Time to land (assuming level ground, no negative initial height)
    # This reduces to 2*vy/GRAVITY if vy>0, but we keep the sqrt for clarity.
    flight_time = (vy + np.sqrt(vy**2 + 2.0 * GRAVITY * 0.0)) / GRAVITY
    max_distance = vx * flight_time

    return {
        "success": True,
        "launch_vel_x": vx,
        "launch_vel_y": vy,
        "max_distance": max_distance,
        "flight_time": flight_time,
        "spin_up_time": spin_up_time,
        "arm_length": arm_length,
        "arm_radius": arm_radius,
        "ball_radius": ball_radius,
    }


def solve_for_inputs(req: InverseReq):
    """
    Given a desired distance, release angle, spin-up time, and geometry,
    calculate motor torque and max_omega that achieve the specified range.
    """
    distance = req.distance
    angle_rad = np.radians(req.angle_deg)
    spin_up_time = req.spin_up_time

    arm_length = req.arm_length
    arm_radius = req.arm_radius
    ball_radius = req.ball_radius

    sin_2theta = np.sin(2 * angle_rad)
    if abs(sin_2theta) < 1e-9:
        return {"success": False, "error": "Invalid angle (sin(2θ)=0)."}

    # Derive ball position from geometry
    ball_position = arm_length - 0.03
    if ball_position <= 0:
        return {
            "success": False,
            "error": "Ball position is non-positive (check arm_length).",
        }

    # Required angular velocity
    required_omega = np.sqrt(
        (distance * GRAVITY) / (ball_position**2 * sin_2theta)
    )

    # Calculate torque from angular acceleration and inertia
    inertia = calc_launcher_inertia(arm_length, arm_radius, ball_radius)
    alpha = required_omega / spin_up_time if spin_up_time else 0.0
    required_torque = inertia * alpha

    return {
        "success": True,
        "distance": distance,
        "release_angle_deg": req.angle_deg,
        "max_omega": required_omega,
        "motor_torque": required_torque,
        "arm_length": arm_length,
        "arm_radius": arm_radius,
        "ball_radius": ball_radius,
    }


@app.post("/simulate_launch")
def simulate(req: SimulationReq):
    """Endpoint for a forward simulation with explicit motor torque, angles, and geometry."""
    return simulate_launch(req)


@app.post("/solve_for_inputs")
def inverse_calculation(req: InverseReq):
    """Endpoint for inverse calculation given distance, angle, spin-up time, and geometry."""
    return solve_for_inputs(req)
