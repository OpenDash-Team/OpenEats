import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Route, Routes } from 'react-router-dom'

import 'bootstrap/dist/css/bootstrap.min.css';
import './index.css'

import IndexPage from './pages/IndexPage.tsx';
import RestaurantPage from './pages/RestaurantPage.tsx';

const root = document.getElementById('root')!

createRoot(root).render(
  <StrictMode>
    <BrowserRouter>
      <Routes>
        <Route index element={<IndexPage />} />
        <Route path="/restaurants/:restaurantId" element={<RestaurantPage />} />
      </Routes>
    </BrowserRouter>
  </StrictMode>,
)
