import React, { useState } from 'react';

const DonationRequestForm = () => {
  const [formData, setFormData] = useState({
    contactNumber: '',
    address: '',
    category: 'disaster',
    description: '',
    quantity: '',
    urgency: 'medium',
  });

  const [errors, setErrors] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [submitStatus, setSubmitStatus] = useState({ type: '', message: '' });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    if (errors[name]) setErrors((prev) => ({ ...prev, [name]: '' }));
    if (submitStatus.message) setSubmitStatus({ type: '', message: '' });
  };

  const validate = () => {
    const newErrors = {};
    if (!formData.contactNumber.trim()) newErrors.contactNumber = 'Contact number is required';
    if (!formData.address.trim()) newErrors.address = 'Address is required';
    if (!formData.description.trim()) newErrors.description = 'Description is required';
    return newErrors;
  };

  const submitDonationRequest = async (data) => {
    // API placeholder – replace with actual fetch call
    return new Promise((resolve) => {
      setTimeout(() => resolve({ success: true, requestId: 'req_' + Date.now() }), 1500);
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const validationErrors = validate();
    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors);
      return;
    }
    setIsLoading(true);
    setSubmitStatus({ type: '', message: '' });

    try {
      const payload = { ...formData, requestedAt: new Date().toISOString() };
      const response = await submitDonationRequest(payload);
      setSubmitStatus({
        type: 'success',
        message: `✅ Request submitted! ID: ${response.requestId}`,
      });
      // Optionally reset form
    } catch (error) {
      setSubmitStatus({ type: 'error', message: `❌ ${error.message || 'Submission failed'}` });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-2xl shadow-xl overflow-hidden">
      <div className="bg-gradient-to-r from-red-600 to-orange-500 px-6 py-5">
        <h3 className="text-xl font-bold text-white">Emergency Request Form</h3>
        <p className="text-red-100 text-sm">All fields marked with * are required</p>
      </div>

      <form onSubmit={handleSubmit} className="p-6 space-y-6">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-6">
          <div>
            <label htmlFor="contactNumber" className="block text-sm font-medium text-gray-700">
              Contact Number <span className="text-red-500">*</span>
            </label>
            <input
              type="tel"
              id="contactNumber"
              name="contactNumber"
              value={formData.contactNumber}
              onChange={handleChange}
              className={`mt-1 block w-full border ${errors.contactNumber ? 'border-red-500 ring-red-200' : 'border-gray-300 focus:ring-red-400'} rounded-lg shadow-sm p-3 transition focus:ring-2 focus:border-transparent outline-none`}
              placeholder="e.g., 09-123-456-789"
              disabled={isLoading}
            />
            {errors.contactNumber && <p className="text-red-500 text-xs mt-1">{errors.contactNumber}</p>}
          </div>

          <div>
            <label htmlFor="address" className="block text-sm font-medium text-gray-700">
              Address <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              id="address"
              name="address"
              value={formData.address}
              onChange={handleChange}
              className={`mt-1 block w-full border ${errors.address ? 'border-red-500 ring-red-200' : 'border-gray-300 focus:ring-red-400'} rounded-lg shadow-sm p-3 transition focus:ring-2 focus:border-transparent outline-none`}
              placeholder="Street, city, state"
              disabled={isLoading}
            />
            {errors.address && <p className="text-red-500 text-xs mt-1">{errors.address}</p>}
          </div>
        </div>

        <div>
          <label htmlFor="category" className="block text-sm font-medium text-gray-700">
            Category <span className="text-red-500">*</span>
          </label>
          <select
            id="category"
            name="category"
            value={formData.category}
            onChange={handleChange}
            className="mt-1 block w-full border border-gray-300 rounded-lg shadow-sm p-3 focus:ring-2 focus:ring-red-400 focus:border-transparent outline-none bg-white"
            disabled={isLoading}
          >
            <option value="disaster">Disaster Urgent</option>
            <option value="food">Food</option>
            <option value="clothes">Clothes</option>
            <option value="shelter">Shelter</option>
            <option value="others">Others</option>
          </select>
        </div>

        <div>
          <label htmlFor="description" className="block text-sm font-medium text-gray-700">
            Description of Need <span className="text-red-500">*</span>
          </label>
          <textarea
            id="description"
            name="description"
            rows="3"
            value={formData.description}
            onChange={handleChange}
            className={`mt-1 block w-full border ${errors.description ? 'border-red-500 ring-red-200' : 'border-gray-300 focus:ring-red-400'} rounded-lg shadow-sm p-3 transition focus:ring-2 focus:border-transparent outline-none resize-y`}
            placeholder="Describe what you need and why..."
            disabled={isLoading}
          />
          {errors.description && <p className="text-red-500 text-xs mt-1">{errors.description}</p>}
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-6">
          <div>
            <label htmlFor="quantity" className="block text-sm font-medium text-gray-700">
              Quantity (optional)
            </label>
            <input
              type="text"
              id="quantity"
              name="quantity"
              value={formData.quantity}
              onChange={handleChange}
              className="mt-1 block w-full border border-gray-300 rounded-lg shadow-sm p-3 focus:ring-2 focus:ring-red-400 focus:border-transparent outline-none"
              placeholder="e.g., 5 boxes, 10 kg"
              disabled={isLoading}
            />
          </div>

          <div>
            <label htmlFor="urgency" className="block text-sm font-medium text-gray-700">
              Urgency Level
            </label>
            <select
              id="urgency"
              name="urgency"
              value={formData.urgency}
              onChange={handleChange}
              className="mt-1 block w-full border border-gray-300 rounded-lg shadow-sm p-3 focus:ring-2 focus:ring-red-400 focus:border-transparent outline-none bg-white"
              disabled={isLoading}
            >
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
              <option value="critical">Critical</option>
            </select>
          </div>
        </div>

        {submitStatus.message && (
          <div className={`p-3 rounded-lg text-sm ${submitStatus.type === 'success' ? 'bg-green-50 text-green-800 border border-green-200' : 'bg-red-50 text-red-800 border border-red-200'}`}>
            {submitStatus.message}
          </div>
        )}

        <button
          type="submit"
          disabled={isLoading}
          className={`w-full bg-gradient-to-r from-red-600 to-orange-500 hover:from-red-700 hover:to-orange-600 text-white font-semibold py-3 rounded-lg shadow-md transition-all transform hover:scale-[1.02] active:scale-[0.98] ${isLoading ? 'opacity-70 cursor-not-allowed' : ''}`}
        >
          {isLoading ? 'Submitting...' : 'Submit Request'}
        </button>
      </form>
    </div>
  );
};

export default DonationRequestForm;