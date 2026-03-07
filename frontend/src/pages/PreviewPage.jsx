import React, { useState } from 'react';
import { useReportStore } from '../store/useReportStore';
import { FileText, CheckCircle2, Loader2, ChevronLeft, Download, RotateCcw, Printer } from 'lucide-react';
import api from '../services/api';

const PreviewPage = () => {
    const setStep = useReportStore((state) => state.setStep);
    const informeData = useReportStore((state) => state.informeData);
    const reset = useReportStore((state) => state.reset);

    const [isGeneratingPdf, setIsGeneratingPdf] = useState(false);
    const [error, setError] = useState('');

    const downloadPdf = async () => {
        setIsGeneratingPdf(true);
        setError('');
        try {
            const response = await api.post('reports/generate-pdf', informeData, {
                responseType: 'blob',
            });

            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `Informe_MIP_${informeData.cliente_nombre}_${informeData.mes}_${informeData.anio}.pdf`);
            document.body.appendChild(link);
            link.click();
            link.remove();
        } catch (err) {
            console.error(err);
            setError('Error al generar el PDF. Verificá que el servidor esté activo.');
        } finally {
            setIsGeneratingPdf(false);
        }
    };

    return (
        <div className="max-w-4xl mx-auto mt-10">
            <div className="text-center mb-10">
                <div className="inline-block p-4 bg-green-50 rounded-full mb-4">
                    <CheckCircle2 size={48} className="text-green-500" />
                </div>
                <h2 className="text-3xl font-bold text-primary-900">¡Todo listo!</h2>
                <p className="text-primary-600 mt-2">El informe ha sido consolidado exitosamente. Ya podés descargar los archivos finales.</p>
            </div>

            <div className="flex flex-col gap-6 mb-10">
                {/* Card Print (Vista A4 - Recomendado) */}
                <div className="card flex flex-col md:flex-row items-center gap-8 p-8 border-2 border-sanitas-light bg-sanitas-light/5">
                    <div className="p-4 bg-white text-sanitas rounded-xl shadow-sm">
                        <Printer size={48} />
                    </div>
                    <div className="flex-1 text-center md:text-left">
                        <h3 className="text-xl font-bold text-primary-800 mb-1">Vista A4 — Imprimir o Guardar como PDF</h3>
                        <p className="text-sm text-primary-600 mb-4 md:mb-0">
                            Previsualizá el informe en hojas A4 reales con numeración de página y diseño optimizado.
                            Guardalo como PDF usando la opción de impresión del navegador.
                        </p>
                    </div>
                    <button
                        onClick={() => setStep('print')}
                        className="btn-accent py-4 px-8 w-full md:w-auto text-lg shadow-lg hover:scale-105 active:scale-95 transition-all"
                    >
                        <Printer size={22} />
                        Abrir Vista A4
                    </button>
                </div>

                {/* Card PDF Directo */}
                <div className="card flex flex-col md:flex-row items-center gap-8 p-8">
                    <div className="p-4 bg-red-50 text-red-500 rounded-xl">
                        <FileText size={40} />
                    </div>
                    <div className="flex-1 text-center md:text-left">
                        <h3 className="text-xl font-bold text-primary-800 mb-1">Exportar PDF (Backend)</h3>
                        <p className="text-sm text-primary-500 mb-4 md:mb-0">
                            Genera el PDF directamente desde el servidor. Archivo guardado también en la carpeta
                            <code className="bg-gray-100 px-1 rounded ml-1">outputs/</code>.
                        </p>
                    </div>
                    <button
                        onClick={downloadPdf}
                        disabled={isGeneratingPdf}
                        className="btn-secondary border border-primary-300 py-3 px-6 w-full md:w-auto"
                    >
                        {isGeneratingPdf ? <Loader2 className="animate-spin" size={20} /> : <Download size={20} />}
                        <span className="ml-2">{isGeneratingPdf ? 'Generando...' : 'Descargar PDF'}</span>
                    </button>
                </div>
            </div>

            {error && (
                <div className="mb-10 p-4 bg-red-50 border border-red-200 text-red-700 rounded-lg text-center">
                    {error}
                </div>
            )}

            <div className="flex flex-col items-center gap-4">
                <div className="flex gap-4">
                    <button
                        onClick={() => setStep('summaries')}
                        className="flex items-center gap-2 text-primary-500 hover:text-primary-700 font-medium"
                    >
                        <ChevronLeft size={18} /> Volver a editar textos
                    </button>
                    <div className="w-px h-6 bg-primary-200"></div>
                    <button
                        onClick={reset}
                        className="flex items-center gap-2 text-primary-500 hover:text-red-600 font-medium"
                    >
                        <RotateCcw size={18} /> Iniciar nuevo informe
                    </button>
                </div>

                <div className="mt-12 pt-8 border-t border-primary-200 w-full text-center">
                    <p className="text-sm text-primary-400">
                        Los archivos generados se guardan también en la carpeta <code>outputs/</code> del servidor.
                    </p>
                </div>
            </div>
        </div>
    );
};

export default PreviewPage;
