import React from 'react';
import { Link } from 'react-router-dom';
import {
  FaDonate,
  FaHandsHelping,
  FaCheckCircle,
  FaCertificate,
  FaHeart,
  FaUsers,
  FaChartLine,
  FaHandHoldingHeart,
  FaHome,
  FaShieldAlt,
  FaBullhorn,
  FaGlobeAmericas,
  FaFireExtinguisher,
  FaTruck,
  FaClock,
  FaExclamationTriangle,
} from 'react-icons/fa';

const LandingPage = () => {
  return (
    <div className="min-h-screen bg-white">
      {/* Navigation */}
      <nav className="bg-white shadow-md">
        <div className="container mx-auto px-4 py-3">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="flex items-center space-x-2 mb-4 md:mb-0">
              <FaFireExtinguisher className="text-red-600 text-2xl" />
              <h1 className="text-2xl font-bold text-gray-800">
                Disaster<span className="text-red-600">Relief</span>
              </h1>
            </div>
            <div className="flex flex-wrap justify-center gap-4 md:gap-6">
              <Link
                to="/login"
                className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md font-medium transition-all hover:shadow-md"
              >
                Login
              </Link>
              <Link
                to="/register"
                className="bg-orange-500 hover:bg-orange-600 text-white px-4 py-2 rounded-md font-medium transition-all hover:shadow-md"
              >
                Donate Now
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="container mx-auto px-4 py-12 md:py-20">
        <div className="flex flex-col lg:flex-row items-center">
          <div className="lg:w-1/2 mb-12 lg:mb-0">
            <div className="flex items-center gap-2 mb-4">
              <FaExclamationTriangle className="text-red-500 text-3xl animate-pulse" />
              <span className="bg-red-100 text-red-800 text-sm font-semibold px-3 py-1 rounded-full">
                Urgent Help Needed
              </span>
            </div>
            <h2 className="text-4xl md:text-5xl font-bold text-gray-800 mb-6 leading-tight">
              Rapid Response for<br />
              <span className="text-red-600">Disaster & Crisis</span>
            </h2>
            <p className="text-gray-600 text-lg mb-8 max-w-lg">
              A trusted platform that connects donors directly with communities affected by disasters.
              Every second counts – your support brings immediate relief.
            </p>
            <div className="flex flex-col sm:flex-row gap-4">
              <Link
                to="/register"
                className="bg-red-600 hover:bg-red-700 text-white px-8 py-3 rounded-md font-medium text-lg transition-all hover:shadow-md transform hover:-translate-y-1 text-center"
              >
                Send Emergency Aid
              </Link>
              <Link
                to="/dashboard"
                className="bg-orange-500 hover:bg-orange-600 text-white px-8 py-3 rounded-md font-medium text-lg transition-all hover:shadow-md transform hover:-translate-y-1 text-center"
              >
                Request Support
              </Link>
            </div>
          </div>
          <div className="lg:w-1/2 grid grid-cols-2 gap-6">
            <div className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow border-l-4 border-red-500">
              <FaTruck className="text-red-600 text-4xl mb-4" />
              <h3 className="font-bold text-xl mb-2">Fast Delivery</h3>
              <p className="text-gray-600">Emergency supplies dispatched within hours</p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow border-l-4 border-orange-500">
              <FaClock className="text-orange-500 text-4xl mb-4" />
              <h3 className="font-bold text-xl mb-2">24/7 Response</h3>
              <p className="text-gray-600">Around‑the‑clock coordination for crises</p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow border-l-4 border-amber-500">
              <FaUsers className="text-amber-500 text-4xl mb-4" />
              <h3 className="font-bold text-xl mb-2">Community Resilience</h3>
              <p className="text-gray-600">Empowering local volunteers and groups</p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow border-l-4 border-emerald-500">
              <FaCheckCircle className="text-emerald-600 text-4xl mb-4" />
              <h3 className="font-bold text-xl mb-2">Full Transparency</h3>
              <p className="text-gray-600">Track every donation from source to impact</p>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="container mx-auto px-4 py-16">
        <h3 className="text-3xl font-bold text-center mb-12 text-gray-800">
          How Disaster Relief Works
        </h3>
        <div className="grid md:grid-cols-3 gap-8">
          <div className="text-center p-6 rounded-lg bg-white shadow-md hover:shadow-lg transition-all transform hover:-translate-y-1">
            <div className="bg-red-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-6">
              <FaDonate className="text-red-600 text-2xl" />
            </div>
            <h4 className="font-bold text-xl mb-4 text-gray-800">Donate Supplies or Funds</h4>
            <p className="text-gray-600">
              Contribute money, food, water, medicine, or essential items through our secure portal.
            </p>
          </div>
          <div className="text-center p-6 rounded-lg bg-white shadow-md hover:shadow-lg transition-all transform hover:-translate-y-1">
            <div className="bg-orange-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-6">
              <FaHandsHelping className="text-orange-500 text-2xl" />
            </div>
            <h4 className="font-bold text-xl mb-4 text-gray-800">Request & Verify</h4>
            <p className="text-gray-600">
              Affected communities submit verified requests; our team validates needs and prioritises.
            </p>
          </div>
          <div className="text-center p-6 rounded-lg bg-white shadow-md hover:shadow-lg transition-all transform hover:-translate-y-1">
            <div className="bg-amber-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-6">
              <FaChartLine className="text-amber-500 text-2xl" />
            </div>
            <h4 className="font-bold text-xl mb-4 text-gray-800">Deliver & Report</h4>
            <p className="text-gray-600">
              Supplies reach those in need, and you receive real‑time reports on the impact of your gift.
            </p>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="bg-gray-50 py-16">
        <div className="container mx-auto px-4">
          <h3 className="text-3xl font-bold text-center mb-12 text-gray-800">
            Why Choose Our Platform
          </h3>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            <div className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-all border-l-4 border-red-500">
              <FaShieldAlt className="text-red-600 text-3xl mb-4" />
              <h4 className="font-bold text-xl mb-3">Secure & Transparent</h4>
              <p className="text-gray-600">
                Every transaction is recorded on an immutable ledger – full visibility for donors.
              </p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-all border-l-4 border-orange-500">
              <FaBullhorn className="text-orange-500 text-3xl mb-4" />
              <h4 className="font-bold text-xl mb-3">Real‑time Alerts</h4>
              <p className="text-gray-600">
                Instant notifications about emerging disasters and urgent requests in your area.
              </p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-all border-l-4 border-amber-500">
              <FaGlobeAmericas className="text-amber-500 text-3xl mb-4" />
              <h4 className="font-bold text-xl mb-3">Global & Local Reach</h4>
              <p className="text-gray-600">
                Support communities worldwide or focus on neighbourhoods near you.
              </p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-all border-l-4 border-emerald-500">
              <FaCertificate className="text-emerald-600 text-3xl mb-4" />
              <h4 className="font-bold text-xl mb-3">Recognition & Certificates</h4>
              <p className="text-gray-600">
                Receive official acknowledgment for your generosity and contribution.
              </p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-all border-l-4 border-sky-500">
              <FaHeart className="text-sky-500 text-3xl mb-4" />
              <h4 className="font-bold text-xl mb-3">Volunteer Matching</h4>
              <p className="text-gray-600">
                Connect with local volunteers to assist in relief operations and distribution.
              </p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-all border-l-4 border-indigo-500">
              <FaHandHoldingHeart className="text-indigo-500 text-3xl mb-4" />
              <h4 className="font-bold text-xl mb-3">Post‑Disaster Recovery</h4>
              <p className="text-gray-600">
                Support long‑term rebuilding and rehabilitation projects beyond the immediate crisis.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Emergency CTA */}
      <section className="container mx-auto px-4 py-16 text-center">
        <div className="bg-gradient-to-r from-red-50 via-orange-50 to-amber-50 p-12 rounded-2xl border-2 border-red-200">
          <div className="flex justify-center items-center gap-4 mb-6">
            <FaExclamationTriangle className="text-red-500 text-5xl animate-pulse" />
            <h3 className="text-3xl md:text-4xl font-bold text-gray-800">
              Disasters Don't Wait –<br />
              <span className="text-red-600">Every Moment Matters</span>
            </h3>
          </div>
          <p className="text-gray-700 text-lg mb-8 max-w-2xl mx-auto">
            Join thousands of donors who are making a real difference. Your action today
            can save lives and rebuild communities.
          </p>
          <Link
            to="/register"
            className="inline-block bg-orange-500 hover:bg-orange-600 text-white px-10 py-4 rounded-md font-bold text-lg transition-all hover:shadow-lg transform hover:-translate-y-1"
          >
            Become a Disaster Responder
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-800 text-white py-8">
        <div className="container mx-auto px-4">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <FaFireExtinguisher className="text-red-400" />
                <h4 className="text-xl font-bold">DisasterRelief</h4>
              </div>
              <p className="text-gray-400">Rapid response, lasting recovery.</p>
            </div>
            <div>
              <h5 className="font-bold mb-4">About Us</h5>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#" className="hover:text-red-300 transition-colors">Our Mission</a></li>
                <li><a href="#" className="hover:text-red-300 transition-colors">Emergency Team</a></li>
                <li><a href="#" className="hover:text-red-300 transition-colors">Partners</a></li>
              </ul>
            </div>
            <div>
              <h5 className="font-bold mb-4">Contact</h5>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#" className="hover:text-red-300 transition-colors">Emergency Hotline</a></li>
                <li><a href="#" className="hover:text-red-300 transition-colors">Support</a></li>
                <li><a href="#" className="hover:text-red-300 transition-colors">Email</a></li>
              </ul>
            </div>
            <div>
              <h5 className="font-bold mb-4">Legal</h5>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#" className="hover:text-red-300 transition-colors">Privacy Policy</a></li>
                <li><a href="#" className="hover:text-red-300 transition-colors">Terms of Use</a></li>
                <li><a href="#" className="hover:text-red-300 transition-colors">Transparency Report</a></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-700 mt-8 pt-8 text-center text-gray-400">
            <p>&copy; 2024 Disaster & Charity Donation System. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;