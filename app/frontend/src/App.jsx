import { Routes, Route, NavLink } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import DailyLog from './pages/DailyLog'
import Products from './pages/Products'

export default function App() {
  return (
    <>
      <nav>
        <NavLink className="logo" to="/">🥖 Panadería</NavLink>
        <NavLink to="/"         end>Previsión</NavLink>
        <NavLink to="/registro">Registro diario</NavLink>
        <NavLink to="/productos">Productos</NavLink>
      </nav>
      <div className="container">
        <Routes>
          <Route path="/"          element={<Dashboard />} />
          <Route path="/registro"  element={<DailyLog />} />
          <Route path="/productos" element={<Products />} />
        </Routes>
      </div>
    </>
  )
}