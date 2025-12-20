import React, { useState } from "react";
import { Link } from "react-router-dom";
import "../App.css";

export default function Navbar({ className }) {
  const items = [
    { name: "Home", path: "/" },
    { name: "Connect", path: "/connect" },
    { name: "About", path: "/about" },
    { name: "Contact", path: "/contact" },
  ];
  const [menuOpen, setMenuOpen] = useState(false);
  return (
    <nav className={`${className} z-20 w-full py-4 px-6 sm:px-12 relative`}>
      <div className="flex items-center justify-between">
        {/* Logo */}
        <div>
          <Link to="/">
            <h1 className="text-white font-bold text-[20px]">Career Advisor</h1>
          </Link>
        </div>

        {/* Desktop Menu */}
        <ul className="hidden md:flex space-x-12">
          {items.map((item) => (
            <li key={item.name}>
              <Link
                to={item.path}
                className="text-white cursor-pointer hover:text-gray-300 text-xl font-medium"
              >
                {item.name}
              </Link>
            </li>
          ))}
        </ul>


        {/* Desktop Button */}
        <div className="hidden md:flex">
          <Link to="logout/">
            <button
              onClick={() => {

                setMenuOpen(false);
              }}
              className="bg-white text-black font-Inter text-[18px] font-medium p-3 rounded-full w-[150px] h-[50px] hover:bg-gray-200 transition"
            >
              Logout
            </button>
          </Link>
        </div>

        {/* Mobile Hamburger */}
        <div className="md:hidden">
          <button
            onClick={() => setMenuOpen(!menuOpen)}
            className="text-white text-3xl font-bold focus:outline-none"
          >
            {menuOpen ? "✕" : "☰"}
          </button>
        </div>
      </div>

      {/* Mobile Menu */}
      <div
        className={`md:hidden absolute top-full left-0 w-full bg-black transition-all duration-300 overflow-hidden ${menuOpen ? "max-h-96" : "max-h-0"
          }`}
      >
        <ul className="flex flex-col space-y-4 py-4 text-center">
          {items.map((item) => (
            <li key={item.name}>
              <Link
                to={item.path}
                className="text-white cursor-pointer hover:text-gray-300 text-xl font-medium"
                onClick={() => setMenuOpen(false)}
              >
                {item.name}
              </Link>
            </li>
          ))}
          <li>
            <Link to="logout/">
              <button
                onClick={() => {

                  setMenuOpen(false);
                }}
                className="bg-white text-black font-Inter text-[18px] font-medium p-3 rounded-full w-[150px] h-[50px] hover:bg-gray-200 transition"
              >
                Logout
              </button>
            </Link>
          </li>
        </ul>
      </div>
    </nav>
  );
}