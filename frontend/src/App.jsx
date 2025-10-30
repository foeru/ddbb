import "./App.css";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import MainPage from "./pages/MainPage";
import GuidePage from "./pages/GuidePage";
import Payment from "./pages/Payment";
import AiDashboard from "./pages/AiDashboard";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<MainPage />} />
        <Route path="/guide" element={<GuidePage />} />
        <Route path="/payment" element={<Payment />} />
        <Route path="/admin" element={<AiDashboard />} />
      </Routes>
    </Router>
  );
}

export default App;
