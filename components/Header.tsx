import Link from "next/link";
import { ThemeToggle } from "@/components/ThemeToggle";

export function Header() {
  return (
    <header className="sticky top-0 z-50 border-b border-border bg-background/90 backdrop-blur-md">
      <div className="mx-auto flex h-14 max-w-3xl items-center justify-between px-4 sm:h-16 sm:px-6">
        <Link
          href="https://relova.ai"
          className="font-serif text-[15px] font-semibold tracking-tight text-foreground sm:text-lg"
        >
          Relova Blog
        </Link>
        <div className="flex items-center gap-1 sm:gap-2">
          <nav className="text-[13px] font-medium text-muted-foreground sm:text-sm">
            <Link
              href="/blog"
              className="rounded-md px-2 py-1 transition-colors hover:bg-secondary hover:text-foreground"
            >
              All posts
            </Link>
          </nav>
          <ThemeToggle />
        </div>
      </div>
    </header>
  );
}
