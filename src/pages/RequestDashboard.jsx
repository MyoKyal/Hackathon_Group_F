import React from 'react';
import { useNavigate } from 'react-router-dom';
import { FaFireExtinguisher, FaUser, FaSignOutAlt } from 'react-icons/fa';
import DonationRequestForm from '../components/DonationRequestForm';

const RequestDashboard = ({ user, onLogout }) => {
  const navigate = useNavigate();

  const handleLogout = () => {
    onLogout();
    navigate('/');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-md">
        <div className="container mx-auto px-4 py-3 flex justify-between items-center">
          <div className="flex items-center space-x-2">
            <FaFireExtinguisher className="text-red-600 text-2xl" />
            <h1 className="text-2xl font-bold text-gray-800">
              Disaster<span className="text-red-600">Relief</span>
            </h1>
          </div>
          <div className="flex items-center space-x-4">
            <span className="text-gray-700 flex items-center gap-1">
              <FaUser className="text-red-500" />
              {user?.name || 'User'}
            </span>
            <button
              onClick={handleLogout}
              className="flex items-center gap-2 bg-red-50 hover:bg-red-100 text-red-700 px-3 py-1 rounded-md transition"
            >
              <FaSignOutAlt />
              Logout
            </button>
          </div>
        </div>
      </nav>

      <div className="container mx-auto px-4 py-8">
        <div className="mb-6">
          <h2 className="text-2xl font-bold text-gray-800">Submit a Disaster Request</h2>
          <p className="text-gray-600">Fill in the details below to request help for your community.</p>
        </div>
        <DonationRequestForm />
      </div>
    </div>
  );
};

export default RequestDashboard;