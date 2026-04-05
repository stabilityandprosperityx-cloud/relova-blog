import Link from "next/link";

export function Header() {
  return (
    <header className="border-b border-navy/10 bg-cream/80 backdrop-blur-sm">
      <div className="mx-auto flex h-16 max-w-3xl items-center justify-between px-4 sm:px-6">
        <Link
          href="https://relova.ai"
          className="text-lg font-semibold tracking-tight text-navy transition-colors hover:text-terracotta"
        >
          Relova Blog
        </Link>
        <nav className="text-sm font-medium text-navy/80">
          <Link href="/blog" className="transition-colors hover:text-terracotta">
            All posts
          </Link>
        </nav>
      </div>
    </header>
  );
}
