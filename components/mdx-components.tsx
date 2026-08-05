import type {
  AnchorHTMLAttributes,
  HTMLAttributes,
  ReactNode,
  TableHTMLAttributes,
  TdHTMLAttributes,
  ThHTMLAttributes,
} from "react";

function cx(...parts: (string | undefined)[]) {
  return parts.filter(Boolean).join(" ");
}

function JsonLd({ children }: { children?: ReactNode }) {
  const raw =
    typeof children === "string"
      ? children
      : Array.isArray(children)
        ? children.map(String).join("")
        : String(children ?? "");
  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: raw.trim() }}
    />
  );
}

export const mdxComponents = {
  JsonLd,
  a: (props: AnchorHTMLAttributes<HTMLAnchorElement>) => (
    <a
      {...props}
      className="font-medium text-primary underline-offset-2 hover:text-primary/90 hover:underline"
    />
  ),

  table: ({ className, children, ...props }: TableHTMLAttributes<HTMLTableElement>) => (
    <div className="mdx-table-scroll my-8 w-full overflow-x-auto rounded-lg border border-border bg-card">
      <table
        {...props}
        className={cx(
          "mdx-table w-full min-w-[min(100%,520px)] border-collapse text-left text-sm",
          className,
        )}
      >
        {children}
      </table>
    </div>
  ),

  thead: ({ className, ...props }: HTMLAttributes<HTMLTableSectionElement>) => (
    <thead {...props} className={cx("bg-secondary", className)} />
  ),

  tbody: ({ className, ...props }: HTMLAttributes<HTMLTableSectionElement>) => (
    <tbody {...props} className={cx(className)} />
  ),

  tr: ({ className, ...props }: HTMLAttributes<HTMLTableRowElement>) => (
    <tr {...props} className={cx(className)} />
  ),

  th: ({ className, ...props }: ThHTMLAttributes<HTMLTableCellElement>) => (
    <th
      {...props}
      className={cx(
        "border border-border px-4 py-3 align-top text-sm font-semibold text-foreground",
        className,
      )}
    />
  ),

  td: ({ className, ...props }: TdHTMLAttributes<HTMLTableCellElement>) => (
    <td
      {...props}
      className={cx(
        "border border-border px-4 py-3 align-top text-muted-foreground",
        className,
      )}
    />
  ),
};
