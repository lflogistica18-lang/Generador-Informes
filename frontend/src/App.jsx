import React, { useEffect, useState } from 'react';
import { useReportStore } from './store/useReportStore';
import Layout from './components/layout/Layout';

// Páginas
import SelectClientPage from './pages/SelectClientPage';
import UploadPage from './pages/UploadPage';
import ReviewPage from './pages/ReviewPage';
import VoladoresPage from './pages/VoladoresPage';
import SummariesPage from './pages/SummariesPage';
import PreviewPage from './pages/PreviewPage';
import PrintPage from './pages/PrintPage';

function App() {
  const currentStep = useReportStore((state) => state.currentStep);

  // Renderizado condicional basado en el paso actual del wizard
  const renderStep = () => {
    switch (currentStep) {
      case 'select-client':
        return <SelectClientPage />;
      case 'upload':
        return <UploadPage />;
      case 'review':
        return <ReviewPage />;
      case 'voladores':
        return <VoladoresPage />;
      case 'summaries':
        return <SummariesPage />;
      case 'preview':
        return <PreviewPage />;
      case 'print':
        return <PrintPage />;
      default:
        return <SelectClientPage />;
    }
  };

  if (currentStep === 'print') {
    return renderStep();
  }

  return (
    <Layout>
      {renderStep()}
    </Layout>
  );
}

export default App;
