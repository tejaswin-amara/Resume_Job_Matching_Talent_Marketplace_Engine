export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24">
      <h1 className="text-4xl font-bold">Talent Engine Dashboard</h1>
      <div className="grid grid-cols-2 gap-4 mt-8">
        <div className="border p-4 rounded shadow">
          <h2 className="text-2xl font-semibold mb-2">Employers</h2>
          <p>Post jobs, view allocations, and find candidates.</p>
        </div>
        <div className="border p-4 rounded shadow">
          <h2 className="text-2xl font-semibold mb-2">Candidates</h2>
          <p>Upload resumes, track matches, and apply to roles.</p>
        </div>
      </div>
    </main>
  )
}
