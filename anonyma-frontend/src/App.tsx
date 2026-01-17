import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import TextAnonymization from './pages/TextAnonymization';
import DocumentProcessing from './pages/DocumentProcessing';
import Jobs from './pages/Jobs';
import Settings from './pages/Settings';

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<TextAnonymization />} />
          <Route path="/document" element={<DocumentProcessing />} />
          <Route path="/jobs" element={<Jobs />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
