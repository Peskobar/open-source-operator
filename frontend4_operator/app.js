const metricsList = document.getElementById('metrics-list');
const agentsList = document.getElementById('agents-list');
const canvas = document.getElementById('xr-canvas');
let ws;

function connectWebSocket() {
    ws = new WebSocket(`ws://${location.host}/ws`);
    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        updateDashboard(data);
    };
    ws.onclose = () => {
        setTimeout(connectWebSocket, 1000);
    };
}

function updateDashboard(data) {
    if (data.metrics) {
        metricsList.innerHTML = '';
        Object.entries(data.metrics).forEach(([key, value]) => {
            const li = document.createElement('li');
            li.textContent = `${key}: ${value}`;
            metricsList.appendChild(li);
        });
    }
    if (data.agents) {
        agentsList.innerHTML = '';
        data.agents.forEach(agent => {
            const li = document.createElement('li');
            li.textContent = `${agent.name} - ${agent.status}`;
            agentsList.appendChild(li);
        });
    }
}

// Voice commands using Web Speech API
const voiceBtn = document.getElementById('voice-btn');
const recognition = window.SpeechRecognition ? new window.SpeechRecognition() : new window.webkitSpeechRecognition();
recognition.lang = 'en-US';
voiceBtn.onclick = () => {
    recognition.start();
};

recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    ws.send(JSON.stringify({ type: 'voice_command', text: transcript }));
};

// Basic 3D scene using Three.js
import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.163.0/build/three.module.js';

let scene, camera, renderer, cube;
function init3D() {
    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(75, canvas.clientWidth / canvas.clientHeight, 0.1, 1000);
    renderer = new THREE.WebGLRenderer({ canvas });
    renderer.setSize(canvas.clientWidth, canvas.clientHeight);
    cube = new THREE.Mesh(new THREE.BoxGeometry(), new THREE.MeshStandardMaterial({ color: 0x4f46e5 }));
    scene.add(cube);
    const light = new THREE.HemisphereLight(0xffffff, 0x444444);
    scene.add(light);
    camera.position.z = 3;
    animate();
}

function animate() {
    requestAnimationFrame(animate);
    cube.rotation.x += 0.01;
    cube.rotation.y += 0.01;
    renderer.render(scene, camera);
}

window.addEventListener('resize', () => {
    camera.aspect = canvas.clientWidth / canvas.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(canvas.clientWidth, canvas.clientHeight);
});

connectWebSocket();
init3D();
