import Link from "next/link";

export function Footer() {
  return (
    <footer className="mt-auto border-t border-border bg-card/40 py-10">
      <div className="mx-auto max-w-3xl px-4 text-center sm:px-6">
        <p className="text-[13px] text-muted-foreground">
          © 2026 Relova ·{" "}
          <Link href="/about" className="transition-colors hover:text-primary">
            About
          </Link>
          {" · "}
          <a
            href="https://relova.ai"
            className="transition-colors hover:text-primary"
          >
            relova.ai
          </a>
        </p>
      </div>
    </footer>
  );
}
