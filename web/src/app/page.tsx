import Link from "next/link";
import { SpotlightCard, ShinyText, Squares, FadeContent } from "@/components/reactbits";
import { UserCircle, Briefcase } from "lucide-react";

export default function Home() {
  return (
    <main className="relative flex min-h-screen flex-col items-center justify-center p-8 md:p-24 bg-gray-950 overflow-hidden">
      <div className="absolute inset-0 z-0 pointer-events-none opacity-40">
        <Squares direction="diagonal" speed={0.4} squareSize={48} borderColor="rgba(255, 255, 255, 0.06)" />
      </div>

      <FadeContent className="relative z-10 max-w-5xl w-full items-center justify-between font-mono text-sm">
        <h1 className="text-4xl md:text-5xl font-extrabold text-center mb-12">
          <ShinyText text="Talent Marketplace Engine" className="bg-gradient-to-r from-blue-400 to-emerald-400" />
        </h1>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl mx-auto">
          <Link href="/candidates" className="group">
            <SpotlightCard
              spotlightColor="rgba(59, 130, 246, 0.25)"
              className="h-full p-8 transition-transform transform group-hover:scale-105 group-hover:border-blue-500 cursor-pointer bg-gray-900/60 backdrop-blur"
            >
              <div className="text-center">
                <UserCircle className="w-16 h-16 mx-auto mb-4 text-blue-500 group-hover:text-blue-400 transition-colors" />
                <h2 className="text-2xl font-bold text-gray-100 mb-3">Candidate Portal</h2>
                <p className="text-gray-400">
                  Upload your resume, see your parsed profile, and find matching jobs instantly.
                </p>
              </div>
            </SpotlightCard>
          </Link>

          <Link href="/recruiter" className="group">
            <SpotlightCard
              spotlightColor="rgba(16, 185, 129, 0.25)"
              className="h-full p-8 transition-transform transform group-hover:scale-105 group-hover:border-emerald-500 cursor-pointer bg-gray-900/60 backdrop-blur"
            >
              <div className="text-center">
                <Briefcase className="w-16 h-16 mx-auto mb-4 text-emerald-500 group-hover:text-emerald-400 transition-colors" />
                <h2 className="text-2xl font-bold text-gray-100 mb-3">Recruiter Portal</h2>
                <p className="text-gray-400">
                  Post jobs, view candidate leaderboards, and run market allocations.
                </p>
              </div>
            </SpotlightCard>
          </Link>
        </div>
      </FadeContent>
    </main>
  );
}
