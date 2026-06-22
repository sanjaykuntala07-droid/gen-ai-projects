import { Link, useLocation } from 'react-router-dom';
import { Sparkles, Library, BarChart2, GitCompare, BookOpen } from 'lucide-react';

const items = [
  { icon: Sparkles,   label: 'Input',     path: '/'          },
  { icon: Library,    label: 'Gallery',   path: '/gallery'   },
  { icon: BarChart2,  label: 'Dash',      path: '/dashboard' },
  { icon: GitCompare, label: 'Compare',   path: '/compare'   },
  { icon: BookOpen,   label: 'Notes',     path: '/notebook'  },
];

export default function BottomNav() {
  const { pathname } = useLocation();
  return (
    <nav className="bottom-nav">
      {items.map(({ icon: Icon, label, path }) => (
        <Link
          key={path}
          to={path}
          className={`bottom-nav__item ${pathname === path || (path !== '/' && pathname.startsWith(path)) ? 'active' : ''}`}
        >
          <Icon size={20} strokeWidth={1.8} />
          {label}
        </Link>
      ))}
    </nav>
  );
}
