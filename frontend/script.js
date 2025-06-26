let scene, camera, renderer, arm, ball, pivot;
let ws;
let motorRunning = false;
let keepRotating = false;
let ballReleased = false;
let maxSpeedReached = false;
let launchAngleRad = 0;
let angularSpeed = 0;

let ROTATION_RADIUS = 0.17;
let BALL_DIAMETER = 0.015;
let ROD_DIAMETER = 0.015;
let ROD_LENGTH = 0.2;
let ROD_AXIS_OFFSET = 0.07;

/// Initialize Ball Trajectory Chart (X vs Y)
let ctx1 = document.getElementById("trajectoryChart").getContext("2d");
let trajectoryChart = new Chart(ctx1, {
    type: "scatter",
    data: {
        datasets: [{
            label: "Ball Trajectory",
            data: [],
            borderColor: "red",
            backgroundColor: "red",
            pointRadius: 3,
            showLine: true,
        }]
    },
    options: {
        responsive: false,
        maintainAspectRatio: false,
        scales: {
            x: { title: { display: true, text: "X Position (m)" } },
            y: { title: { display: true, text: "Y Position (m)" } }
        }
    }
});

// Initialize X Position Over Time Chart
let ctx2 = document.getElementById("xPositionChart").getContext("2d");
let xPositionChart = new Chart(ctx2, {
    type: "line",
    data: {
        labels: [],
        datasets: [{
            label: "X Position",
            data: [],
            borderColor: "blue",
            fill: false
        }]
    },
    options: {
        responsive: false,
        maintainAspectRatio: false,
        scales: {
            x: { title: { display: true, text: "Time (s)" } },
            y: { title: { display: true, text: "X Position (m)" } }
        }
    }
});

// Initialize Y Position Over Time Chart
let ctx3 = document.getElementById("yPositionChart").getContext("2d");
let yPositionChart = new Chart(ctx3, {
    type: "line",
    data: {
        labels: [],
        datasets: [{
            label: "Y Position",
            data: [],
            borderColor: "green",
            fill: false
        }]
    },
    options: {
        responsive: false,
        maintainAspectRatio: false,
        scales: {
            x: { title: { display: true, text: "Time (s)" } },
            y: { title: { display: true, text: "Y Position (m)" } }
        }
    }
});

function runExperiment() {
    // Reset everything before starting
    resetArm();

    let motorTorque = parseFloat(document.getElementById("torqueInput").value);
    let startAngle = parseFloat(document.getElementById("startAngleInput").value);
    let releaseAngle = parseFloat(document.getElementById("releaseAngleInput").value);
    launchAngleRad = releaseAngle * (Math.PI / 180); // Convert to radians

    ws = new WebSocket("ws://localhost:8000/ws");

    ws.onopen = function() {
        ws.send(JSON.stringify({ motor_torque: motorTorque, start_angle: startAngle, release_angle: releaseAngle }));
    };

    motorRunning = true;
    keepRotating = false;
    ballReleased = false;
    maxSpeedReached = false;

    ws.onmessage = function (event) {
        let data = JSON.parse(event.data);

        // Update angular speed display
        if (data.omega !== undefined) {
            angularSpeed = data.omega;
            document.getElementById(
                "speedDisplay"
            ).innerText = `Angular Speed: ${angularSpeed.toFixed(2)} rad/s`;
        }

        // Rotate arm using the received angle (keeps updating)
        pivot.rotation.z = -data.theta;

        // If the ball has not been released, keep it attached to the arm
        if (!ballReleased) {
            let armLength = 0.17; // 170 mm in meters
            let ballX = pivot.position.x + armLength * Math.cos(-data.theta);
            let ballY = pivot.position.y + armLength * Math.sin(-data.theta);
            ball.position.set(ballX, ballY, 0);

            // Update trajectory chart while ball is attached
            trajectoryChart.data.datasets[0].data.push({ x: ballX, y: ballY });
            xPositionChart.data.labels.push(data.time.toFixed(2));
            xPositionChart.data.datasets[0].data.push(ballX);
            yPositionChart.data.labels.push(data.time.toFixed(2));
            yPositionChart.data.datasets[0].data.push(ballY);

            trajectoryChart.update();
            xPositionChart.update();
            yPositionChart.update();
        }
    };
}
