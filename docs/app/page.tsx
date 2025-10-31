import Link from 'next/link';

export default function HomePage() {
  return (
    <main className="flex h-screen flex-col items-center justify-center text-center">
      <h1 className="mb-4 text-4xl font-bold">HumaLab SDK</h1>
      <p className="mb-8 text-lg text-muted-foreground">
        Python SDK for HumaLab - A platform for adaptive AI validation
      </p>
      <Link
        href="/docs"
        className="rounded-lg bg-primary px-4 py-2 text-primary-foreground hover:bg-primary/90"
      >
        View Documentation
      </Link>
    </main>
  );
}
