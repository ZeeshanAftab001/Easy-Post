import robot from '../assets/robot.png';
import { Link } from 'react-router-dom';

export default function Hero() {
  return (
    <div className="w-full min-h-screen relative overflow-hidden">
      

      {/* Hero Content */}
      <div className="relative z-10 flex flex-col md:flex-row items-center justify-center min-h-screen px-6 md:px-20 gap-10 md:gap-20">
        {/* Robot Image */}
        <div className="flex-shrink-0">
          <img className="h-64 sm:h-96 md:h-[600px] animate-fadeUp w-auto" src={robot} alt="Robot" />
        </div>

        {/* Text & Buttons */}
        <div className="flex flex-col items-center text-center md:items-center md:text-left gap-6 md:gap-10 justify-center">
          <h1 className="text-white text-4xl animate-fadeUp sm:text-5xl md:text-[82px] font-bold leading-tight text-center">
            The Future of <br />
            The Next-Gen Chatbot
          </h1>
          <p className="leading-tight animate-fadeUp text-white text-[18px] sm:text-[20px] md:text-[22px] text-center ">
            Meet Aidy, the next-gen AI chatbot designed to enhance conversations with intuitive responses,<br /> seamless integration, and powerful automation.
          </p>
          {/* Buttons */}
          <div className="flex  animate-fadeUp flex-col sm:flex-row gap-4 sm:gap-10 mt-4">
            <Link to="/chat" className="bg-white btn text-black font-Inter text-[18px] font-medium p-3 rounded-full w-[150px] h-[50px] text-center hover:bg-gray-200 transition">
              Get Started
            </Link>
            <Link to="/contact" className="border-2 border-white text-white flex justify-center items-center font-Inter text-[18px] font-medium p-3 rounded-full w-[150px] h-[50px] text-center hover:bg-black hover:text-white transition">
              Contact Us
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}