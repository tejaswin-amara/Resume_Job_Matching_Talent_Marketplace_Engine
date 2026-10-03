import Link from "next/link";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { UserCircle, Briefcase } from "lucide-react";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24 bg-gray-950">
      <div className="z-10 max-w-5xl w-full items-center justify-between font-mono text-sm">
        <h1 className="text-5xl font-extrabold text-center mb-12 bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-emerald-400">
          Talent Marketplace Engine
        </h1>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl mx-auto">
          <Link href="/candidates" className="group">
            <Card className="h-full transition-transform transform group-hover:scale-105 group-hover:border-blue-500 cursor-pointer bg-gray-900/50 backdrop-blur">
              <CardHeader className="text-center">
                <UserCircle className="w-16 h-16 mx-auto mb-4 text-blue-500 group-hover:text-blue-400" />
                <CardTitle className="text-2xl text-gray-100">Candidate Portal</CardTitle>
              </CardHeader>
              <CardContent className="text-center text-gray-400">
                Upload your resume, see your parsed profile, and find matching jobs instantly.
              </CardContent>
            </Card>
          </Link>

          <Link href="/recruiter" className="group">
            <Card className="h-full transition-transform transform group-hover:scale-105 group-hover:border-emerald-500 cursor-pointer bg-gray-900/50 backdrop-blur">
              <CardHeader className="text-center">
                <Briefcase className="w-16 h-16 mx-auto mb-4 text-emerald-500 group-hover:text-emerald-400" />
                <CardTitle className="text-2xl text-gray-100">Recruiter Portal</CardTitle>
              </CardHeader>
              <CardContent className="text-center text-gray-400">
                Post jobs, view candidate leaderboards, and run market allocations.
              </CardContent>
            </Card>
          </Link>
        </div>
      </div>
    </main>
  );
}
