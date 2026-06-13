import { SignIn } from "@clerk/clerk-react";

export default function Login() {
  return (
    <div className="min-h-screen bg-brand-bg flex items-center justify-center p-6 relative overflow-hidden">
      {/* Background Ambience */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-brand-primary/10 blur-[180px] rounded-full -z-10" />
      
      <div className="w-full max-w-md reveal flex flex-col items-center">
        <div className="text-center mb-12">
          <div className="w-16 h-16 brand-gradient rounded-2xl flex items-center justify-center text-white mx-auto mb-8 shadow-2xl glow-primary">
            <svg className="w-9 h-9" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z" clipRule="evenodd"/></svg>
          </div>
          <h1 className="text-4xl font-black text-white tracking-tight mb-3">Operator Authentication</h1>
          <p className="text-brand-muted font-bold tracking-widest text-[10px] uppercase">Secure Login Protocol Required</p>
        </div>

        <SignIn 
          appearance={{
            elements: {
              formButtonPrimary: "brand-gradient py-3 px-4 rounded-xl text-white font-black uppercase tracking-widest hover:scale-[1.02] active:scale-100 transition-all shadow-xl shadow-brand-primary/20",
              card: "bg-brand-card border-white/5 shadow-2xl rounded-3xl overflow-hidden",
              headerTitle: "text-white font-black",
              headerSubtitle: "text-brand-muted font-bold",
              socialButtonsBlockButton: "bg-white/5 border-white/10 text-white hover:bg-white/10",
              socialButtonsBlockButtonText: "text-white font-bold",
              formFieldLabel: "text-brand-muted font-black uppercase tracking-widest text-[10px]",
              formFieldInput: "bg-white/5 border-white/10 text-white rounded-xl p-4",
              footerActionText: "text-brand-muted font-bold",
              footerActionLink: "text-brand-secondary hover:underline",
              identityPreviewText: "text-white",
              identityPreviewEditButtonIcon: "text-brand-secondary"
            }
          }}
          signUpUrl="/signup"
          forceRedirectUrl="/dashboard"
        />
      </div>
    </div>
  );
}