import React, { useState } from 'react';
import axios from 'axios';
// import { useNavigate } from 'react-router-dom'; // Uncomment if using React Router

const Login = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    // const navigate = useNavigate(); // Uncomment if using React Router

    const handleLogin = async (e) => {
        e.preventDefault();
        setError('');

        try {
            // Use environment variable for API URL
            const apiUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api/';
            const response = await axios.post(`${apiUrl}users/login/`, {
                username: email, 
                password: password
            });

            const { access, refresh, role } = response.data;

            // Store tokens
            localStorage.setItem('accessToken', access);
            localStorage.setItem('refreshToken', refresh);
            localStorage.setItem('role', role);

            // Navigate based on Role
            console.log("Login Successful! Role:", role);
            
            if (role === 'ADMIN') {
                window.location.href = '/admin-dashboard'; 
                // navigate('/admin-dashboard');
            } else if (role === 'STUDENT') {
                window.location.href = '/student-dashboard';
                // navigate('/student-dashboard');
            } else if (role === 'TRAINER') {
                window.location.href = '/trainer-dashboard';
                // navigate('/trainer-dashboard');
            } else {
                window.location.href = '/dashboard';
            }

        } catch (err) {
            console.error("Login Error", err);
            setError('Invalid credentials. Please try again.');
        }
    };

    return (
        <div className="flex justify-center items-center h-screen bg-gray-100">
            <div className="bg-white p-8 rounded shadow-md w-96">
                <h2 className="text-2xl font-bold mb-6 text-center">LMS Login</h2>
                {error && <p className="text-red-500 text-sm mb-4">{error}</p>}
                
                <form onSubmit={handleLogin}>
                    <div className="mb-4">
                        <label className="block text-gray-700 text-sm font-bold mb-2">Username / Email</label>
                        <input 
                            type="text" 
                            className="w-full p-2 border rounded"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            placeholder="Enter username"
                        />
                    </div>
                    
                    <div className="mb-6">
                        <label className="block text-gray-700 text-sm font-bold mb-2">Password</label>
                        <input 
                            type="password" 
                            className="w-full p-2 border rounded"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            placeholder="Enter password"
                        />
                    </div>

                    <button 
                        type="submit" 
                        className="w-full bg-blue-500 text-white p-2 rounded hover:bg-blue-600 transition"
                    >
                        Sign In
                    </button>
                </form>
            </div>
        </div>
    );
};

export default Login;
