export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-4">
      <div className="text-center">
        <h1 className="text-4xl font-bold tracking-tight text-foreground mb-4">Welcome to v0</h1>
        <p className="text-lg text-muted-foreground mb-8">Your application is ready to deploy</p>
        <a
          href="https://v0.app"
          className="inline-flex items-center justify-center px-6 py-3 rounded-lg bg-primary text-primary-foreground font-semibold hover:opacity-90 transition-opacity"
        >
          Learn more about v0
        </a>
      </div>
    </main>
  )
}
