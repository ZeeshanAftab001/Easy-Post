import { useState } from 'react';
import { FaEnvelope, FaPhone, FaMapMarkerAlt, FaPaperPlane, FaCheck, FaLinkedin, FaGithub, FaTwitter } from 'react-icons/fa';
import { MdAccessTime } from 'react-icons/md';
import { RiCustomerService2Fill } from 'react-icons/ri';
import shadow1 from '../assets/s1.png';
import Navbar from '../components/Navbar';

export default function Contact({ isPage = false }) { // Changed parameter name and default value
    // Removed the problematic useEffect that was causing infinite loop
    
    const [formData, setFormData] = useState({
        name: '',
        email: '',
        subject: '',
        message: ''
    });
    
    const [formStatus, setFormStatus] = useState({
        submitting: false,
        submitted: false,
        error: null
    });

    const contactInfo = [
        {
            icon: <FaEnvelope className="text-xl" />,
            title: 'Email Us',
            details: ['support@careeradvisor.ai', 'info@careeradvisor.ai'],
            color: 'from-blue-500 to-cyan-400'
        },
        {
            icon: <FaPhone className="text-xl" />,
            title: 'Call Us',
            details: ['+1 (555) 123-4567', '+1 (555) 987-6543'],
            color: 'from-purple-500 to-pink-400'
        },
        {
            icon: <FaMapMarkerAlt className="text-xl" />,
            title: 'Visit Us',
            details: ['123 Career Street', 'San Francisco, CA 94107'],
            color: 'from-green-500 to-emerald-400'
        },
        {
            icon: <MdAccessTime className="text-xl" />,
            title: 'Working Hours',
            details: ['Mon - Fri: 9:00 AM - 6:00 PM', 'Sat: 10:00 AM - 4:00 PM'],
            color: 'from-orange-500 to-yellow-400'
        }
    ];

    const faqs = [
        {
            question: 'How does the AI career advisor work?',
            answer: 'Our AI analyzes your skills, interests, and goals to provide personalized career recommendations and learning paths.'
        },
        {
            question: 'Is the service free to use?',
            answer: 'Yes! Basic career guidance is completely free. Premium features are available for advanced analysis.'
        },
        {
            question: 'How accurate are the job recommendations?',
            answer: 'We use real-time market data and AI algorithms to provide 95%+ accurate career recommendations.'
        },
        {
            question: 'Can I get personalized coaching?',
            answer: 'Yes, we offer both AI guidance and optional human career coaching sessions.'
        }
    ];

    const [expandedFaq, setExpandedFaq] = useState(null);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setFormStatus({ submitting: true, submitted: false, error: null });

        // Simulate API call
        setTimeout(() => {
            if (formData.email && formData.message) {
                setFormStatus({ submitting: false, submitted: true, error: null });
                setFormData({ name: '', email: '', subject: '', message: '' });
                
                // Reset success message after 5 seconds
                setTimeout(() => {
                    setFormStatus(prev => ({ ...prev, submitted: false }));
                }, 5000);
            } else {
                setFormStatus({ 
                    submitting: false, 
                    submitted: false, 
                    error: 'Please fill in all required fields' 
                });
            }
        }, 1500);
    };

    return (
        <div className="w-full min-h-screen relative overflow-hidden text-white">
            {/* Grid Background - FIXED: Use negative z-index */}
            <div
                className="fixed inset-0 -z-20"
                style={{
                    backgroundImage: `
                        repeating-linear-gradient(0deg, #d1d5db 0px, #d1d5db 1px, transparent 1px, transparent 100px),
                        repeating-linear-gradient(90deg, #d1d5db 0px, #d1d5db 1px, transparent 1px, transparent 100px)
                    `,
                    backgroundSize: '100px 100px',
                    opacity: 0.1,
                }}
            />

            {/* Shadow Overlay - FIXED: Use negative z-index */}
        
            {/* Conditionally render Navbar */}
            {isPage && <Navbar />}

            {/* Main Content - FIXED: Remove z-10 to avoid stacking issues */}
            <div className="relative">
                {/* Hero Header */}
                <section className={`${isPage ? 'pt-20' : 'pt-4'} pb-16 px-4 lg:px-8`}>
                    <div className="max-w-7xl mx-auto">
                        <div className="text-center mb-16">
                            <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-gradient-to-r from-blue-600 to-purple-600 mb-6">
                                <RiCustomerService2Fill className="text-3xl" />
                            </div>
                            <h1 className="text-5xl lg:text-6xl font-bold mb-6 bg-gradient-to-r from-white via-blue-200 to-purple-200 bg-clip-text text-transparent">
                                Get In Touch
                            </h1>
                            <p className="text-xl text-gray-300 max-w-3xl mx-auto">
                                Have questions about careers? Need assistance with our AI advisor? We're here to help you succeed.
                            </p>
                        </div>

                        {/* Contact Cards Grid */}
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-20">
                            {contactInfo.map((info, index) => (
                                <div key={index} className="chat_color rounded-2xl p-6 transform hover:scale-105 transition duration-300 relative z-10">
                                    <div className={`inline-flex items-center justify-center w-14 h-14 rounded-full bg-gradient-to-r ${info.color} mb-4`}>
                                        {info.icon}
                                    </div>
                                    <h3 className="text-xl font-bold mb-3">{info.title}</h3>
                                    {info.details.map((detail, idx) => (
                                        <p key={idx} className="text-gray-400 mb-1">{detail}</p>
                                    ))}
                                </div>
                            ))}
                        </div>
                    </div>
                </section>

                {/* Contact Form & Info */}
                <section className="py-16 px-4 lg:px-8">
                    <div className="max-w-7xl mx-auto">
                        <div className="grid lg:grid-cols-2 gap-12">
                            {/* Contact Form */}
                            <div className="chat_color rounded-2xl p-8 relative z-10">
                                <h2 className="text-3xl font-bold mb-6">Send Us a Message</h2>
                                
                                {formStatus.submitted ? (
                                    <div className="bg-gradient-to-r from-green-500/20 to-emerald-500/20 border border-green-500/30 rounded-xl p-6 mb-6">
                                        <div className="flex items-center gap-3 mb-3">
                                            <div className="w-10 h-10 rounded-full bg-green-500 flex items-center justify-center">
                                                <FaCheck className="text-xl" />
                                            </div>
                                            <div>
                                                <h3 className="text-xl font-bold">Message Sent!</h3>
                                                <p className="text-gray-300">We'll get back to you within 24 hours.</p>
                                            </div>
                                        </div>
                                        <p className="text-gray-400 text-sm">Thank you for contacting Career Advisor AI. Our team will review your message and respond promptly.</p>
                                    </div>
                                ) : formStatus.error ? (
                                    <div className="bg-gradient-to-r from-red-500/20 to-pink-500/20 border border-red-500/30 rounded-xl p-4 mb-6">
                                        <p className="text-red-400">{formStatus.error}</p>
                                    </div>
                                ) : null}

                                <form onSubmit={handleSubmit} className="space-y-6">
                                    <div className="grid md:grid-cols-2 gap-6">
                                        <div>
                                            <label className="block text-sm font-medium mb-2">
                                                Your Name <span className="text-gray-500">(Optional)</span>
                                            </label>
                                            <input
                                                type="text"
                                                name="name"
                                                value={formData.name}
                                                onChange={handleChange}
                                                className="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                                placeholder="John Doe"
                                            />
                                        </div>
                                        <div>
                                            <label className="block text-sm font-medium mb-2">
                                                Email Address <span className="text-red-400">*</span>
                                            </label>
                                            <input
                                                type="email"
                                                name="email"
                                                value={formData.email}
                                                onChange={handleChange}
                                                required
                                                className="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                                placeholder="john@example.com"
                                            />
                                        </div>
                                    </div>
                                    
                                    <div>
                                        <label className="block text-sm font-medium mb-2">
                                            Subject <span className="text-gray-500">(Optional)</span>
                                        </label>
                                        <input
                                            type="text"
                                            name="subject"
                                            value={formData.subject}
                                            onChange={handleChange}
                                            className="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                            placeholder="How can we help?"
                                        />
                                    </div>
                                    
                                    <div>
                                        <label className="block text-sm font-medium mb-2">
                                            Your Message <span className="text-red-400">*</span>
                                        </label>
                                        <textarea
                                            name="message"
                                            value={formData.message}
                                            onChange={handleChange}
                                            required
                                            rows="6"
                                            className="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                                            placeholder="Tell us about your career questions or feedback..."
                                        />
                                    </div>
                                    
                                    <button
                                        type="submit"
                                        disabled={formStatus.submitting}
                                        className="btn text-black px-8 py-3 rounded-lg font-semibold w-full flex items-center justify-center gap-2 hover:opacity-90 transition disabled:opacity-50 disabled:cursor-not-allowed relative z-20"
                                    >
                                        {formStatus.submitting ? (
                                            <>
                                                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-black"></div>
                                                Sending...
                                            </>
                                        ) : (
                                            <>
                                                <FaPaperPlane />
                                                Send Message
                                            </>
                                        )}
                                    </button>
                                </form>
                            </div>

                            {/* FAQ & Social */}
                            <div>
                                {/* FAQ Section */}
                                <div className="chat_color rounded-2xl p-8 mb-8 relative z-10">
                                    <h2 className="text-3xl font-bold mb-6">Frequently Asked Questions</h2>
                                    <div className="space-y-4">
                                        {faqs.map((faq, index) => (
                                            <div key={index} className="border-b border-gray-800 pb-4 last:border-0">
                                                <button
                                                    onClick={() => setExpandedFaq(expandedFaq === index ? null : index)}
                                                    className="w-full flex justify-between items-center text-left"
                                                >
                                                    <h3 className="text-lg font-medium pr-4">{faq.question}</h3>
                                                    <span className={`transform transition-transform ${expandedFaq === index ? 'rotate-180' : ''}`}>
                                                        ▼
                                                    </span>
                                                </button>
                                                {expandedFaq === index && (
                                                    <p className="text-gray-400 mt-3 pl-2">{faq.answer}</p>
                                                )}
                                            </div>
                                        ))}
                                    </div>
                                </div>

                                {/* Social Links */}
                                <div className="chat_color rounded-2xl p-8 relative z-10">
                                    <h2 className="text-3xl font-bold mb-6">Connect With Us</h2>
                                    <p className="text-gray-400 mb-6">
                                        Follow us on social media for career tips, industry insights, and platform updates.
                                    </p>
                                    <div className="flex gap-4">
                                        <a 
                                            href="#" 
                                            className="flex-1 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 p-4 rounded-xl text-center transition transform hover:scale-105 relative z-10"
                                        >
                                            <div className="flex items-center justify-center gap-2">
                                                <FaLinkedin className="text-xl" />
                                                <span>LinkedIn</span>
                                            </div>
                                        </a>
                                        <a 
                                            href="#" 
                                            className="flex-1 bg-gradient-to-r from-gray-800 to-gray-900 hover:from-gray-900 hover:to-black p-4 rounded-xl text-center transition transform hover:scale-105 relative z-10"
                                        >
                                            <div className="flex items-center justify-center gap-2">
                                                <FaGithub className="text-xl" />
                                                <span>GitHub</span>
                                            </div>
                                        </a>
                                        <a 
                                            href="#" 
                                            className="flex-1 bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-600 hover:to-blue-600 p-4 rounded-xl text-center transition transform hover:scale-105 relative z-10"
                                        >
                                            <div className="flex items-center justify-center gap-2">
                                                <FaTwitter className="text-xl" />
                                                <span>Twitter</span>
                                            </div>
                                        </a>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </section>

                {/* Map & Location */}
                <section className="py-16 px-4 lg:px-8 bg-gradient-to-b">
                    <div className="max-w-7xl mx-auto">
                        <div className="chat_color rounded-2xl overflow-hidden relative z-10">
                            <div className="p-8 border-b border-gray-800">
                                <h2 className="text-3xl font-bold mb-4">Our Location</h2>
                                <p className="text-gray-400">
                                    Visit our headquarters in San Francisco's tech hub. We're always happy to meet career enthusiasts!
                                </p>
                            </div>
                            <div className="p-8 bg-gradient-to-r from-blue-900/20 to-purple-900/20">
                                <div className="aspect-video rounded-xl overflow-hidden bg-gradient-to-br from-gray-900 to-black flex items-center justify-center">
                                    <div className="text-center p-8">
                                        <div className="text-6xl mb-4">📍</div>
                                        <h3 className="text-2xl font-bold mb-2">Career Advisor AI HQ</h3>
                                        <p className="text-gray-400">123 Career Street, San Francisco, CA 94107</p>
                                        <button className="btn text-black px-4 py-2 rounded-lg mt-4 flex items-center gap-2 mx-auto relative z-20">
                                            <FaMapMarkerAlt />
                                            <span>View on Google Maps</span>
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </section>

                {/* Quick Contact CTA */}
                <section className="py-20 px-4 lg:px-8">
                    <div className="max-w-4xl mx-auto text-center">
                        <div className="inline-flex items-center justify-center w-24 h-24 rounded-full bg-gradient-to-r from-blue-600/20 to-purple-600/20 mb-6 border border-blue-500/30">
                            <RiCustomerService2Fill className="text-4xl text-blue-400" />
                        </div>
                        <h2 className="text-4xl font-bold mb-6">Need Immediate Assistance?</h2>
                        <p className="text-xl text-gray-300 mb-8 max-w-2xl mx-auto">
                            Our AI career advisor is available 24/7. Start a conversation anytime!
                        </p>
                        <div className="flex flex-col sm:flex-row gap-4 justify-center">
                            <button className="btn text-black px-8 py-3 rounded-lg font-semibold text-lg hover:opacity-90 transition flex items-center justify-center gap-2 relative z-20">
                                <RiCustomerService2Fill />
                                Chat with AI Advisor
                            </button>
                            <button className="px-8 py-3 rounded-lg font-semibold text-lg border-2 border-blue-500 text-blue-400 hover:bg-blue-500/10 transition relative z-10">
                                Schedule a Call
                            </button>
                        </div>
                        <p className="mt-8 text-gray-500 text-sm">
                            Average response time: <span className="text-green-400">Under 2 hours</span>
                        </p>
                    </div>
                </section>
            </div>
        </div>
    );
}