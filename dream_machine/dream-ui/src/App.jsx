import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { AnimatePresence } from 'framer-motion';
import TopNav from './components/TopNav.jsx';
import BottomNav from './components/BottomNav.jsx';
import Home from './pages/Home.jsx';
import Questions from './pages/Questions.jsx';
import Generating from './pages/Generating.jsx';
import Blueprint from './pages/Blueprint.jsx';
import Gallery from './pages/Gallery.jsx';
import Compare from './pages/Compare.jsx';
import Dashboard from './pages/Dashboard.jsx';
import Notebook from './pages/Notebook.jsx';

function AnimatedRoutes() {
  const location = useLocation();
  return (
    <AnimatePresence mode="wait">
      <Routes location={location} key={location.pathname}>
        <Route path="/"           element={<Home />} />
        <Route path="/questions"  element={<Questions />} />
        <Route path="/generating" element={<Generating />} />
        <Route path="/blueprint/:id" element={<Blueprint />} />
        <Route path="/gallery"    element={<Gallery />} />
        <Route path="/compare"    element={<Compare />} />
        <Route path="/dashboard"  element={<Dashboard />} />
        <Route path="/notebook"   element={<Notebook />} />
        <Route path="*"           element={<Navigate to="/" replace />} />
      </Routes>
    </AnimatePresence>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <div className="mesh-bg" />
      <div className="grid-overlay" />
      <div className="app-shell">
        <TopNav />
        <AnimatedRoutes />
        <BottomNav />
      </div>
    </BrowserRouter>
  );
}
