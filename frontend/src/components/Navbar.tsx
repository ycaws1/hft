'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

const links = [
  { href: '/', label: 'Dashboard' },
  { href: '/backtest', label: 'Backtest' },
  { href: '/simulation', label: 'Simulation' },
];

export default function Navbar() {
  const pathname = usePathname();

  return (
    <nav className="border-b bg-background">
      <div className="container mx-auto flex h-14 items-center gap-6 px-4">
        <Link href="/" className="text-lg font-bold">
          HFT Bot
        </Link>
        <div className="flex gap-4">
          {links.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className={`text-sm transition-colors hover:text-foreground ${
                pathname === link.href
                  ? 'text-foreground font-medium'
                  : 'text-muted-foreground'
              }`}
            >
              {link.label}
            </Link>
          ))}
        </div>
      </div>
    </nav>
  );
}
