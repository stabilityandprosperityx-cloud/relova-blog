import Link from "next/link";
import { ThemeToggle } from "@/components/ThemeToggle";

export function Header() {
  return (
    <header className="sticky top-0 z-50 border-b border-white/10 bg-[#211625]/95 text-white backdrop-blur-md">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-5 sm:px-8">
        <Link
          href="https://relova.ai"
          className="flex items-center gap-3 text-[13px] font-medium tracking-[0.14em] text-[#dfc27f]"
        >
          <img src="/favicon.png?v=6" alt="" className="h-7 w-7 object-contain"/> RELOVA JOURNAL
        </Link>
        <div className="flex items-center gap-1 sm:gap-2">
          <nav className="flex items-center text-[13px] font-medium text-[#cbbfd0] sm:text-sm">
            <Link
              href="/blog"
              className="rounded-md px-2 py-1 transition-colors hover:bg-secondary hover:text-foreground"
            >
              All posts
            </Link>
            <Link
              href="/about"
              className="rounded-md px-2 py-1 transition-colors hover:bg-secondary hover:text-foreground"
            >
              About
            </Link>
          </nav>
          <ThemeToggle />
        </div>
      </div>
    </header>
  );
}
