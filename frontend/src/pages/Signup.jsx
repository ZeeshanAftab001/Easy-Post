import { SignUp } from "@clerk/clerk-react";

export default function Signup() {
    return (
        <div className="min-h-screen bg-brand-bg flex items-center justify-center p-6 relative overflow-hidden">
             {/* Background Ambience */}
             <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[1000px] h-[1000px] bg-brand-secondary/5 blur-[200px] rounded-full -z-10" />

            <div className="w-full max-w-xl reveal flex flex-col items-center">
                <div className="text-center mb-12">
                    <h1 className="text-5xl font-black text-white tracking-tighter mb-4">Onboard Node.</h1>
                    <p className="text-brand-muted font-bold tracking-[0.4em] text-[10px] uppercase">New Operator Provisioning Protocol</p>
                </div>

                <SignUp 
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
                      footerActionLink: "text-brand-primary hover:underline",
                      identityPreviewText: "text-white",
                      identityPreviewEditButtonIcon: "text-brand-primary"
                    }
                  }}
                  signInUrl="/login"
                  forceRedirectUrl="/dashboard"
                />
            </div>
        </div>
    );
}