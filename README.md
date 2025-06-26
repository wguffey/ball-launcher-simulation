# Ball Launcher Simulation

This simulator models a rotating arm that launches a ball. You can control the inputs directly or solve for the inputs needed to achieve a desired flight distance.

1. **Simulate ball launch**: Enter motor torque, start and release angles, max angular velocity, and geometry. Run a launch simulation and get back interesting info like flight distance, flight time, etc.
2. **Solve for inputs**: Provide a target distance, release angle, spin-up time, and geometry. The required torque and max angular velocity are computed automatically and used to run a simulation.
3. **Change launcher geometry**: You can change some aspects of the ball laucher geometry.

Each simulation run adds a new row to a Results table for easy comparison.

## Table of Contents

- [Ball Launcher Simulation](#ball-launcher-simulation)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Installation](#installation)
  - [Running the app](#running-the-app)
  - [Variable definitions](#variable-definitions)
  - [Mathematical Overview](#mathematical-overview)
    - [Constants](#constants)
    - [1. System Geometry \& Moment of Inertia](#1-system-geometry--moment-of-inertia)
    - [2. Simulate ball launch](#2-simulate-ball-launch)
      - [Given](#given)
      - [Calculation steps](#calculation-steps)
      - [Output](#output)
    - [3. Solve for launch inputs](#3-solve-for-launch-inputs)
      - [Given](#given-1)
      - [Calculation steps](#calculation-steps-1)
      - [Output](#output-1)
  - [Future Improvements](#future-improvements)

## Features

1. Direct Simulation
   - Specify `motor_torque`, `start_angle`, `release_angle`, and `max_angular_velocity`. Calculate and return `flight_distance`, `flight_time`, and `spin_up_time` (which is the amount of time it takes for arm to speed up to maximum angular speed).

2. Inverse Solver
   - Specify `flight_distance`, `release_angle` and `spin_up_time`. Return Given a desired distance, release angle, and spin-up time, computes the needed torque and max angular speed.

3. Results Table
    - Stores new experiment rows, allowing quick comparisons of multiple runs.

## Installation

1. Clone this repository:

   ```bash
   git clone git@github.com:standardbots-candidate/take-home-will-guffey.git
   cd take-home-will-guffey
   ```

2. Create and activate a virtual environment (recommended):

   ```bash
    python -m venv venv
    source venv/bin/activate   # On macOS/Linux
    # or venv\Scripts\activate # On Windows
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Running the app

1. Start the server (in the same directory as `main.py`):

   ```bash
   uvicorn backend.main:app --reload
   ```

2. Open `index.html` in your browser. You can do this using your file explorer.

## Variable definitions

| Variable name|Description|Unit
| ----------- | ----------- | ----------- |
|`motor_torque`|The amount of torque, in Nm, the motor applies to attached arm. |Newton-meter|
|`start_angle`|The starting angle of the arm. |degree|
|`release_angle`|The angle of the arm when the ball is released. |degree|
|`max_angular_velocity`|The maximum angular velocity allowed for rotating arm. |rad/s|
|`flight_distance`|How far the ball travels along the ground axis during flight. |meter|
|`flight_time`|The time between ball being launched and hitting the ground. |second|
|`spin_up_time`|The amount of time it takes for the arm to reach `max_angular_velocity`. |second|

## Mathematical Overview

Below is a step-by-step outline of the math behind calculating total system inertia and both **direct** and **inverse** controls.

### Constants

| Constant name|Description|
| ----------- | ----------- |
|$\rho_{\text{aluminum}}$|Density of 6061 aluminum|
|$\rho_{\text{steel}}$|Density of 1018 steel|
|$R_\text{ball}$|Radius of ball|
|$R_\text{arm}$|Radius of arm|
|$L_\text{arm}$|Total length of arm|
|$d_\text{ball}$|Distance from ball center to axis of rotation |
|$d_\text{offset}$|Offset from center of mass of rod to axis of rotation (i.e. attatchment point to motor)|
|$g$|Standard acceleration of gravity near surface of Earth|

### 1. System Geometry & Moment of Inertia

1. We approximate the arm as a cylindrical rod. Its mass is:

$$M_{\text{arm}} = \rho_{\text{aluminum}}  \bigl(\pi  R_{\text{arm}}^{2}  L_{\text{arm}}\bigr)$$

2. Treating the arm as a uniform rod of length $L_{\text{arm}}$ and mass $M_{\text{arm}}$, rotating about its center. The arm inertia with axis of rotation at center of mass is:

$$I_{\text{cm}} = \frac{1}{12}\ M_{\text{arm}} L_{\text{arm}}^{2}$$

3. Use the parallel axis theorem to account for offset axis of rotation. The rod is offset by $d_{\text{offset}}$ from its center, so:

$$I_{\text{arm}}=I_{\text{cm}} + M_{\text{arm}} d_{\text{offset}}^{2}$$

4. Calculate the total inertia of pivot system by adding inertia from ball. Let $R

$$I_{\text{ball}} = M_{\text{ball}} d_\text{ball}^{2} = (\rho_\text{steel}  \frac{4}{3} \pi R_{\text{ball}}^{3})d_\text{ball}^{2}$$

$$I_{\text{pivot}} = I_{\text{arm}} + I_{\text{ball}}$$

This $I_{\text{pivot}}$ is used for all torque and angular acceleration calculations.

### 2. Simulate ball launch

#### Given

- Motor torque $\tau$
- Maximum angular velocity $\omega_{\max}$
- Release angle $\theta_{\text{rel}}$
- Start angle $\theta_{\text{start}}$

#### Calculation steps

1. Angular acceleration

$$\alpha = \frac{\tau}{I_{\text{pivot}}}$$

2. Time to Reach $\omega_{\max}$

$$t_{\text{toMax}} = \frac{\omega_{\max}}{\alpha}$$

1. Launch velocity at radius $r = d_\text{ball}$:

$$v = \omega_{\max}\ r$$

4. Decompose based on release angle $\theta_{\text{rel}}$:

$$v_x = v\cos(\theta_{\text{rel}}), \quad v_y = v\sin(\theta_{\text{rel}})$$

5. Projectile Flight (ignoring air resistance and launching from ground level):

$$t_{\text{flight}} = \frac{v_y + \sqrt{v_y^{2} + 2g\cdot0}}{g}$$

6. Horizontal distance travelled during flight:

$$d = v_x t_{\text{flight}}$$

#### Output

$$\{v_x,v_y,d,t_{\text{flight}},t_{\text{toMax}}\}$$

### 3. Solve for launch inputs

#### Given

- Desired distance $d$
- Release angle $\theta_{\text{rel}}$
- Spin-up time $T_{\text{spin}}$

#### Calculation steps

1. For a projectile launched at speed $v$ and angle $\theta_{\text{rel}}$:

$$d = \frac{v^{2}\sin\bigl(2\theta_{\text{rel}}\bigr)}{g}$$

2. But $v = \omega_{\max}r$. Thus:

$$d = \frac{\bigl(\omega_{\max}r\bigr)^{2}\sin\bigl(2\theta_{\text{rel}}\bigr)}{g}$$

3. Solve for $\omega_{\max}$:

$$\omega_{\max} = \sqrt{\frac{dg}{r^{2}\sin\bigl(2\theta_{\text{rel}}\bigr)}}$$

4. Torque to Achieve $\omega_{\max}$ in $T_{\text{spin}}$

$$\alpha = \frac{\omega_{\max}}{T_{\text{spin}}}, \quad \tau = I_{\text{pivot}}\times\alpha = I_{\text{pivot}} \times\frac{\omega_{\max}}{T_{\text{spin}}}$$

#### Output

$$\{\omega_{\max},\tau\}$$

## Future Improvements

| Name|Description|Priority|
| ----------- | ----------- |---|
|Unit Tests|Add some unit tests to safeguard core functionality.| High|
|Download results as CSV|Allow the user to download the results table as a CSV.| High|
|Parametric Studies|Automate running a set of simulations over a range of parameters (e.g., torque or release angles) and plot the resulting distances, flight times, etc.| High|
|Variable Arm Geometry|Allow the user to adjust arm length, width, and thickness via the interface, then recalculate moments of inertia on the fly for more flexible experiments.| High|
|3D Motion & Visualization|Extend the model beyond a simple 2D plane. Incorporate a 3D simulation or basic 3D rendering engine to visualize the arm’s rotation and the ball’s flight in three dimensions.| Medium|
|Multiple Material Options|Let users choose different materials for the arm or ball (e.g., steel vs. aluminum ball), automatically updating density and mass properties.| Medium|
|User Authentication|Implement user accounts and permissions for saving, loading, or sharing simulation configurations.|Medium
|Database or Cloud Storage|Store simulation results in a database or cloud platform so users can revisit and compare past experiment runs.| Medium|
|User-Defined Spin-Up Profile|Instead of a simple constant torque and linear acceleration, allow a custom torque vs. time or torque vs. angle function to simulate real motor dynamics.| Low|
|Energy Analysis|Display energy transfers (rotational kinetic, translational kinetic, potential) to give insight into efficiency or energy losses (if damping is introduced).| Low|
|Air Resistance|Add drag force and potentially lift if the ball is spinning. This would make the projectile motion more realistic, especially at higher launch speeds.| Low|

These additions would further enhance realism, interactivity, and analytical depth, making the Ball Launcher Simulation a more powerful research and experimentation tool.
