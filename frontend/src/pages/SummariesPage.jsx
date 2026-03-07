import React from 'react';
import { useReportStore } from '../store/useReportStore';
import { ChevronRight, ChevronLeft, FileText, ClipboardList } from 'lucide-react';
import api from '../services/api';

const SummariesPage = () => {
    const setStep = useReportStore((state) => state.setStep);
    const informeData = useReportStore((state) => state.informeData);
    const updateResumen = useReportStore((state) => state.updateResumen);
    const setInformeData = useReportStore((state) => state.setInformeData);

    if (!informeData) return <div className="p-8 text-center">Cargando datos...</div>;

    // Actualizar gráficos al cargar la página por si hubo cambios manuales
    React.useEffect(() => {
        const refreshCharts = async () => {
            try {
                const response = await api.post('reports/update-charts', informeData);
                if (response.data) {
                    setInformeData(response.data);
                }
            } catch (err) {
                console.error("Error refreshing charts:", err);
            }
        };
        refreshCharts();
    }, []);


    const handleNext = () => {
        setStep('preview');
    };

    return (
        <div className="max-w-5xl mx-auto mt-8">
            <div className="flex justify-between items-center mb-6">
                <div>
                    <h2 className="text-2xl font-bold text-primary-900">Resúmenes y Conclusión</h2>
                    <p className="text-primary-600">Revisa y personaliza los textos narrativos del informe.</p>
                </div>
                <div className="flex gap-3">
                    <button onClick={() => setStep('voladores')} className="btn-secondary"><ChevronLeft size={18} /> Atrás</button>
                    <button onClick={handleNext} className="btn-primary">Vista Previa <ChevronRight size={18} /></button>
                </div>
            </div>

            <div className="space-y-6">
                {/* Roedores */}
                <div className="card">
                    <div className="flex items-center gap-2 mb-4 text-primary-800">
                        <ClipboardList className="text-sanitas" size={24} />
                        <h3 className="text-lg font-bold uppercase tracking-wide">Tratamiento Roedores</h3>
                    </div>
                    <textarea
                        className="input-field min-h-[220px] font-sans text-base leading-relaxed p-4 bg-white focus:ring-2 focus:ring-sanitas/20 transition-all border-primary-200"
                        value={informeData.resumen_roedores || ''}
                        onChange={(e) => updateResumen('resumen_roedores', e.target.value)}
                        placeholder="Escribí aquí el resumen del tratamiento de roedores..."
                    />
                    <p className="mt-2 text-xs text-primary-400">Texto generado automáticamente basado en consumos y capturas del mes.</p>
                </div>

                {/* Voladores */}
                <div className="card">
                    <div className="flex items-center gap-2 mb-4 text-primary-800">
                        <ClipboardList className="text-sanitas" size={24} />
                        <h3 className="text-lg font-bold uppercase tracking-wide">Tratamiento Voladores</h3>
                    </div>
                    <textarea
                        className="input-field min-h-[180px] font-sans text-base leading-relaxed p-4 bg-white focus:ring-2 focus:ring-sanitas/20 transition-all border-primary-200"
                        value={informeData.resumen_voladores || ''}
                        onChange={(e) => updateResumen('resumen_voladores', e.target.value)}
                        placeholder="Escribí aquí el resumen del tratamiento de voladores..."
                    />
                </div>

                {/* Rastreros */}
                <div className="card">
                    <div className="flex items-center gap-2 mb-4 text-primary-800">
                        <ClipboardList className="text-sanitas" size={24} />
                        <h3 className="text-lg font-bold uppercase tracking-wide">Tratamiento Rastreros</h3>
                    </div>
                    <textarea
                        className="input-field min-h-[180px] font-sans text-base leading-relaxed p-4 bg-white focus:ring-2 focus:ring-sanitas/20 transition-all border-primary-200"
                        value={informeData.resumen_rastreros || ''}
                        onChange={(e) => updateResumen('resumen_rastreros', e.target.value)}
                        placeholder="Escribí aquí el resumen del tratamiento de rastreros..."
                    />
                </div>

                {/* Conclusión General */}
                <div className="card bg-primary-800 text-white border-none">
                    <div className="flex items-center gap-2 mb-4">
                        <FileText className="text-sanitas-light" size={24} />
                        <h3 className="text-lg font-bold uppercase tracking-wide">Conclusión General</h3>
                    </div>
                    <textarea
                        className="w-full bg-primary-700/50 border border-primary-600 rounded p-4 text-base leading-relaxed focus:outline-none focus:ring-2 focus:ring-sanitas-light min-h-[250px] shadow-inner"
                        value={informeData.conclusion_general || ''}
                        onChange={(e) => updateResumen('conclusion_general', e.target.value)}
                        placeholder="Escribí aquí la conclusión general del informe..."
                    />
                    <p className="mt-2 text-xs text-primary-300">Este texto aparecerá al final del informe como cierre del periodo.</p>
                </div>
            </div>

            <div className="mt-8 p-4 bg-amber-50 border border-amber-200 rounded-lg flex items-start gap-3">
                <div className="text-amber-500 mt-0.5"><ClipboardList size={20} /></div>
                <div className="text-sm text-amber-800">
                    <strong>Consejo de Mentor:</strong> Los textos en cursiva en el informe final ayudan a distinguir la narrativa del profesional del dato duro de las tablas. Asegurate de mantener un tono técnico y profesional.
                </div>
            </div>
        </div>
    );
};

export default SummariesPage;
