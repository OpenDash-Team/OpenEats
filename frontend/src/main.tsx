import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Route, Routes } from 'react-router-dom'

import './index.css'
import 'bootstrap/dist/css/bootstrap.min.css';

import DiscoverPage from './pages/DiscoverPage.tsx'
import RestaurantPage from './pages/RestaurantPage.tsx';

const root = document.getElementById('root')!

createRoot(root).render(
  <StrictMode>
    <BrowserRouter>
      <Routes>
        <Route index element={<DiscoverPage />} />
        <Route path="/restaurants/:restaurantId" element={<RestaurantPage />} />
      </Routes>
    </BrowserRouter>
  </StrictMode>,
)
