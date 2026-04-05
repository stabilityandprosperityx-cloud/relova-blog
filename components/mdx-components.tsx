import type { AnchorHTMLAttributes } from "react";

export const mdxComponents = {
  a: (props: AnchorHTMLAttributes<HTMLAnchorElement>) => (
    <a
      {...props}
      className="font-medium text-terracotta underline-offset-2 hover:underline"
    />
  ),
};
