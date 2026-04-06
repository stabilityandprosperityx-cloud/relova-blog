import Link from "next/link";

export function Header() {
  return (
    <header className="sticky top-0 z-50 border-b border-white/[0.06] bg-void/90 backdrop-blur-md">
      <div className="mx-auto flex h-14 max-w-3xl items-center justify-between px-4 sm:h-16 sm:px-6">
        <Link
          href="https://relova.ai"
          className="text-[15px] font-semibold tracking-tight text-cream transition-colors hover:text-terracotta sm:text-lg"
        >
          Relova Blog
        </Link>
        <nav className="text-[13px] font-medium text-cream/55 sm:text-sm">
          <Link
            href="/blog"
            className="rounded-md px-2 py-1 transition-colors hover:bg-white/[0.04] hover:text-cream"
          >
            All posts
          </Link>
        </nav>
      </div>
    </header>
  );
}
