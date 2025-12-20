import Hero from "../components/Hero";
import Navbar from "../components/Navbar";
import shadow1 from '../assets/s1.png';
import Contact from "./Contact";

export default function Home() {
  return (
    <div className="relative w-full min-h-screen bg-black">
      {/* Grid Background - FIXED to cover full screen */}
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

      

      {/* Content container - This will scroll */}
      <div className="relative z-10 min-h-screen">
        {/* Navbar */}
        <Navbar />
        
        {/* Main content */}
        <main>
          {/* Hero Section */}
          <section id="hero" className="min-h-screen flex items-center pt-16">
            <Hero />
          </section>
          
          {/* Contact Section */}
          <section id="contact" className="min-h-screen py-10">
            <Contact />
          </section>
        </main>
      </div>
    </div>
  );
}