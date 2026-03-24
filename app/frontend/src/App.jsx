import { Routes, Route, NavLink } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import DailyLog from './pages/DailyLog'
import Products from './pages/Products'
import Trends from './pages/Trends'
import Orders from './pages/Orders'
import Calendar from './pages/Calendar'



export default function App() {
  return (
    <>
      <nav>
        <NavLink className="logo" to="/">🥖 Panadería</NavLink>
        <NavLink to="/"         end>Previsión</NavLink>
        <NavLink to="/registro">Registro diario</NavLink>
        <NavLink to="/productos">Productos</NavLink>
        <NavLink to="/tendencias">Tendencias</NavLink>      
        <NavLink to="/pedidos">Pedidos</NavLink>
        <NavLink to="/historico">Histórico</NavLink>
      </nav>

      <div className="container">
        <Routes>
          <Route path="/"          element={<Dashboard />} />
          <Route path="/registro"  element={<DailyLog />} />
          <Route path="/productos"   element={<Products />} />
          <Route path="/tendencias"  element={<Trends />} />
          <Route path="/pedidos"     element={<Orders />} /> 
          <Route path="/historico"   element={<Calendar />} />       </Routes>
      </div>
    </>
  )
}