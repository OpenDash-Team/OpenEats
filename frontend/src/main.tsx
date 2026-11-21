import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Route, Routes } from 'react-router-dom'

import 'bootstrap/dist/css/bootstrap.min.css';
import './index.css'

import IndexPage from './pages/IndexPage.tsx';
import RestaurantPage from './pages/RestaurantPage.tsx';
import RegisterPage from './pages/RegisterPage.tsx';
import LoginPage from './pages/LoginPage.tsx';
import OrdersPage from './pages/OrdersPage.tsx';
import CartPage from './pages/CartPage.tsx';

const root = document.getElementById('root')!

createRoot(root).render(
  <StrictMode>
    <BrowserRouter>
      <Routes>
        <Route index element={<IndexPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/cart" element={<CartPage />} />
        <Route path="/orders" element={<OrdersPage />} />
        <Route path="/restaurants/:restaurantId" element={<RestaurantPage />} />
      </Routes>
    </BrowserRouter>
  </StrictMode>,
)
