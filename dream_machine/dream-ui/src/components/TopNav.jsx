import { Link } from 'react-router-dom';

export default function TopNav() {
  return (
    <header className="topnav">
      <Link to="/" className="topnav__logo">
        <span className="topnav__logo-mark">✦</span>
        Dream Machine
      </Link>
      <span className="badge badge--primary">Beta</span>
    </header>
  );
}
