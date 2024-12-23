// JavaScript для управления фронтендом виртуальных машин
const API_URL = 'http://localhost:8000';
const API_URL_FOR_FILE = 'http://localhost:8001';

function downloadVMConfigFromServer(vmId, vmName) {
    const link = document.createElement('a');
    link.href = `${API_URL_FOR_FILE}/vm/${vmId}/download`;
    link.download = `${vmName}_config.xml`; // Указываем имя файла
    link.click();
}


// Функция переключения между регистрацией и входом
function toggleForms() {
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');

    if (registerForm.style.display === 'none') {
        registerForm.style.display = 'block';
        loginForm.style.display = 'none';
    } else {
        registerForm.style.display = 'none';
        loginForm.style.display = 'block';
    }
}


// Функция переключения между регистрацией и входом
function toggleForms() {
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    const toggleButton = document.getElementById('toggleRegisterFormButton');

    if (registerForm.style.display === 'none') {
        registerForm.style.display = 'block';
        loginForm.style.display = 'none';
        toggleButton.style.display = 'block';
    } else {
        registerForm.style.display = 'none';
        loginForm.style.display = 'block';
        toggleButton.style.display = 'none';
    }
}

// Обработчик для регистрации
document.getElementById('registerAuthForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const username = document.getElementById('registerUsername').value;
    const password = document.getElementById('registerPassword').value;

    try {
        const response = await fetch(`${API_URL}/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password }),
        });

        const result = await response.json();
        if (response.ok) {
            alert('Registration successful! You can now log in.');
            toggleForms(); // Возврат к форме входа
        } else {
            alert(result.message || 'Registration failed!');
        }
    } catch (error) {
        console.error('Registration error:', error);
        alert('An error occurred during registration');
    }
});

// Функция для регистрации пользователя
document.getElementById('authForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    try {
        const response = await fetch(`${API_URL}/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password }),
        });

        const result = await response.json();
        if (response.ok) {
            sessionStorage.setItem('userId', result.user_id);
            document.getElementById('loginForm').style.display = 'none';
            document.getElementById('mainContent').style.display = 'block';
            loadVMs();
        } else {
            alert(result.message || 'Invalid credentials!');
        }
    } catch (error) {
        console.error('Login error:', error);
        alert('An error occurred during login');
    }
});

// Функция для загрузки списка виртуальных машин
async function loadVMs() {
    try {
        const userId = sessionStorage.getItem('userId');
        const response = await fetch(`${API_URL}/vm?user_id=${userId}`);
        const vms = await response.json();

        const vmsList = document.getElementById('vmsList');
        vmsList.innerHTML = '';

        if (!vms.length) {
            vmsList.innerHTML = '<p>No VMs available.</p>';
            return;
        }

        vms.forEach(vm => {
            const vmElement = document.createElement('div');
            vmElement.className = 'vm-card';
            vmElement.id = `vm-${vm.id}`;
            vmElement.innerHTML = `
                <div class="vm-card-inner">
                    <h3>${vm.name}</h3>
                    <p>CPU: ${vm.cpu}</p>
                    <p>RAM: ${vm.ram} GB</p>
                    <p>Disk: ${vm.disk} GB</p>
                    <button onclick="deleteVM(${vm.id})">Delete</button>
                    <button onclick="downloadVMConfigFromServer(${vm.id}, '${vm.name}')">Download Config</button>
                </div>
            `;
            vmsList.appendChild(vmElement);
        });
    } catch (error) {
        console.error('Error loading VMs:', error);
    }
}

// Функция для создания виртуальной машины
document.getElementById('addVmFormSubmit').addEventListener('submit', async (e) => {
    e.preventDefault();

    const userId = sessionStorage.getItem('userId');
    const newVM = {
        name: document.getElementById('vmName').value,
        cpu: parseInt(document.getElementById('vmCpu').value),
        ram: parseInt(document.getElementById('vmRam').value),
        disk: parseInt(document.getElementById('vmDisk').value),
        user_id: userId,
    };

    try {
        const response = await fetch(`${API_URL}/vm`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(newVM),
        });

        if (response.ok) {
            loadVMs();
            document.getElementById('addVmForm').style.display = 'none';
            document.getElementById('addVmFormSubmit').reset();
        } else {
            alert('Failed to create VM');
        }
    } catch (error) {
        console.error('Error creating VM:', error);
    }
});

// Функция для удаления виртуальной машины
async function deleteVM(vmId) {
    try {
        const response = await fetch(`${API_URL}/vm/${vmId}`, {
            method: 'DELETE',
        });

        if (response.ok) {
            // Удаляем элемент из DOM
            const vmElement = document.getElementById(`vm-${vmId}`);
            if (vmElement) {
                vmElement.remove();
            }
        } else {
            alert('Failed to delete VM');
        }
    } catch (error) {
        console.error('Error deleting VM:', error);
    }
}

// Функция для выхода из аккаунта
function logout() {
    sessionStorage.removeItem('userId');
    document.getElementById('loginForm').style.display = 'block';
    document.getElementById('mainContent').style.display = 'none';
}



// Проверка авторизации при загрузке страницы
window.onload = () => {
    const userId = sessionStorage.getItem('userId');
    if (userId) {
        document.getElementById('loginForm').style.display = 'none';
        document.getElementById('mainContent').style.display = 'block';
        loadVMs();
    } else {
        document.getElementById('loginForm').style.display = 'block';
        document.getElementById('mainContent').style.display = 'none';
    }
};