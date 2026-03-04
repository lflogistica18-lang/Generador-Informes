import React, { useEffect } from 'react';
import { useReportStore } from '../store/useReportStore';
import { ChevronLeft, Printer, Download } from 'lucide-react';

const SummarySection = ({ title, content }) => (
    <div className="mb-6">
        <div className="section-header-print">{title}</div>
        <div className="summary-text-print">{content}</div>
    </div>
);

const PageWrapper = ({ children, pageNumber, totalPages, clientName, period }) => (
    <div className="a4-page">
        <div className="page-header-print">
            <div className="flex justify-between items-center w-full">
                <div className="flex items-center gap-2">
                    <span className="text-sanitas font-bold text-xl uppercase tracking-wider">Sanitas</span>
                    <span className="text-primary-600 font-light text-xl uppercase tracking-wider">Ambiental</span>
                </div>
                <div className="text-right text-[8pt] text-primary-400">
                    Sistema de Gestión Certificado<br />
                    ISO 9001 - 14001 - 45001
                </div>
            </div>
        </div>

        <div className="page-content-print">
            {children}
        </div>

        <div className="page-footer-print">
            <div className="flex justify-between items-center w-full font-medium">
                <div>{clientName} - {period}</div>
                <div className="text-[7pt] text-primary-300 italic">Informe Mensual MIP</div>
            </div>
        </div>
    </div>
);
const PrintPage = () => {
    const informeData = useReportStore((state) => state.informeData);
    const setStep = useReportStore((state) => state.setStep);

    useEffect(() => {
        // Al entrar a esta página, desplazamos arriba
        window.scrollTo(0, 0);
    }, []);

    if (!informeData) {
        return (
            <div className="p-10 text-center">
                <p>No hay datos cargados para el informe.</p>
                <button onClick={() => setStep('select-client')} className="btn-primary mt-4 mx-auto">
                    Volver al inicio
                </button>
            </div>
        );
    }

    const { cliente_nombre, sucursal_nombre, mes, anio, sucursal_direccion } = informeData;
    const period = `${mes} ${anio}`;

    // Detectar si los paths vienen con backslash (Windows/WSL mixed) o slash
    const firstPath = informeData.desvios_roedores?.[0]?.imagen_path || "";
    const pathStyle = firstPath.includes('\\') ? '\\' : '/';

    const handlePrint = () => {
        window.print();
    };

    return (
        <div className="min-h-screen bg-primary-50">
            {/* Barra de herramientas (No se imprime) */}
            <div className="no-print sticky top-0 z-50 bg-white border-b border-primary-200 px-6 py-4 flex justify-between items-center shadow-sm">
                <div className="flex items-center gap-4">
                    <button
                        onClick={() => setStep('preview')}
                        className="p-2 hover:bg-primary-100 rounded-full transition-colors text-primary-600"
                        title="Volver"
                    >
                        <ChevronLeft size={24} />
                    </button>
                    <div>
                        <h1 className="text-lg font-bold text-primary-900 leading-tight">Vista de Impresión</h1>
                        <p className="text-xs text-primary-500">El informe ahora fluye continuamente para evitar espacios vacíos.</p>
                    </div>
                </div>
                <div className="flex gap-3">
                    <button onClick={handlePrint} className="btn-accent px-6">
                        <Printer size={18} />
                        Imprimir / Guardar PDF
                    </button>
                </div>
            </div>

            {/* Contenedor Único Continuo */}
            <div className="print-preview-container">
                <div className="a4-page-continuous">
                    {/* Cabecera y Pie que se repiten en PDF se manejan por CSS fixed, 
                        pero aquí los ponemos como elementos base para la vista web */}
                    <div className="page-header-print no-screen">
                        <div className="flex justify-between items-center w-full">
                            <div className="flex items-center gap-2">
                                <span className="text-sanitas font-bold text-xl uppercase tracking-wider">Sanitas</span>
                                <span className="text-primary-600 font-light text-xl uppercase tracking-wider">Ambiental</span>
                            </div>
                            <div className="text-right text-[8pt] text-primary-400">
                                Sistema de Gestión Certificado<br />
                                ISO 9001 - 14001 - 45001
                            </div>
                        </div>
                    </div>

                    <div className="page-footer-print no-screen">
                        <div className="flex justify-between items-center w-full font-medium">
                            <div>{cliente_nombre} - {period}</div>
                            <div className="text-[7pt] text-primary-300 italic">Informe Mensual MIP</div>
                        </div>
                    </div>

                    {/* CONTENIDO FLUIDO */}
                    <div className="report-content-fluid">
                        <div className="text-center py-10 mb-8 border-b border-primary-100">
                            <h1 className="text-4xl font-black text-sanitas-dark uppercase tracking-[0.2em] mb-2">Informe MIP</h1>
                            <p className="text-primary-400 font-medium tracking-widest uppercase">Manejo Integrado de Plagas</p>
                        </div>

                        <div className="grid grid-cols-2 gap-6 mb-10 bg-primary-50 p-6 rounded-lg border border-primary-100">
                            <div>
                                <label className="text-[9pt] font-bold text-primary-500 uppercase block mb-1">Cliente</label>
                                <p className="text-lg font-bold text-primary-900 leading-tight">{cliente_nombre}</p>
                            </div>
                            <div>
                                <label className="text-[9pt] font-bold text-primary-500 uppercase block mb-1">Período</label>
                                <p className="text-lg font-bold text-primary-900 leading-tight">{period}</p>
                            </div>
                            <div className="col-span-2">
                                <label className="text-[9pt] font-bold text-primary-500 uppercase block mb-1">Sucursal / Planta</label>
                                <p className="text-md font-semibold text-primary-800 leading-tight">{sucursal_nombre} - {sucursal_direccion}</p>
                            </div>
                        </div>

                        {/* SECCIÓN ROEDORES */}
                        <div className="report-section">
                            <div className="section-header-print">Control de Roedores</div>

                            <div className="grid grid-cols-2 gap-4 mb-6">
                                <div className="bg-white border border-primary-100 p-4 rounded-md text-center">
                                    <span className="block text-xl font-bold text-sanitas">{informeData.estaciones_perimetro_externo || 0}</span>
                                    <span className="text-[8pt] text-primary-400 uppercase font-bold">Estaciones Perímetro Externo</span>
                                </div>
                                <div className="bg-white border border-primary-100 p-4 rounded-md text-center">
                                    <span className="block text-xl font-bold text-sanitas">{informeData.estaciones_perimetro_interno || 0}</span>
                                    <span className="text-[8pt] text-primary-400 uppercase font-bold">Estaciones Perímetro Interno</span>
                                </div>
                            </div>

                            {informeData.chart_consumos && (
                                <div className="mb-8 break-inside-avoid">
                                    <div className="text-[10pt] font-bold text-primary-800 mb-2 border-b border-primary-100 pb-1">Análisis de Consumos</div>
                                    <div className="chart-box">
                                        <img
                                            src={`data:image/png;base64,${informeData.chart_consumos}`}
                                            className="max-w-full h-auto mx-auto"
                                            style={{ maxHeight: '320px' }}
                                            alt="Gráfico Consumos"
                                        />
                                    </div>
                                </div>
                            )}

                            {informeData.ranking_cebaderas?.length > 0 && (
                                <div className="mb-6 break-inside-avoid">
                                    <div className="text-[10pt] font-bold text-primary-800 mb-2 border-b border-primary-100 pb-1">Top Estaciones con Actividad</div>
                                    <table className="w-full text-[8pt] border-collapse">
                                        <thead>
                                            <tr className="bg-primary-50 text-left">
                                                <th className="p-2 border border-primary-200">ID</th>
                                                <th className="p-2 border border-primary-200">Tipo</th>
                                                <th className="p-2 border border-primary-200">Sector</th>
                                                <th className="p-2 border border-primary-200 text-right">Consumo (gr)</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {informeData.ranking_cebaderas.slice(0, 10).map((ceb, i) => (
                                                <tr key={i}>
                                                    <td className="p-2 border border-primary-100 font-bold">{ceb.codigo}</td>
                                                    <td className="p-2 border border-primary-100">{ceb.herramienta}</td>
                                                    <td className="p-2 border border-primary-100">{ceb.subseccion}</td>
                                                    <td className="p-2 border border-primary-100 text-right text-sanitas font-bold">
                                                        {Number(ceb.consumo).toFixed(1)}g
                                                    </td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            )}

                            {informeData.observaciones_roedores?.length > 0 && (
                                <div className="mb-6">
                                    <div className="text-[10pt] font-bold text-primary-800 mb-2 border-b border-primary-100 pb-1">Observaciones Técnicas</div>
                                    <table className="w-full text-[9pt]">
                                        <tbody>
                                            {informeData.observaciones_roedores.map((obs, i) => (
                                                <tr key={i} className="break-inside-avoid">
                                                    <td className="py-2 pr-4 border-b border-primary-50 w-24 font-bold text-primary-400 align-top">{obs.fecha}</td>
                                                    <td className="py-2 border-b border-primary-50 text-primary-700 italic">{obs.observaciones}</td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            )}

                            <SummarySection title="Resumen Roedores" content={informeData.resumen_roedores} />

                            {informeData.desvios_roedores?.length > 0 && (
                                <div className="mb-8">
                                    <div className="text-[10pt] font-bold text-primary-800 mb-3 border-b border-primary-100 pb-1 uppercase tracking-wider">Hallazgos Fotográficos - Roedores</div>
                                    <div className="grid grid-cols-2 gap-4">
                                        {informeData.desvios_roedores.map((foto, i) => (
                                            <div key={i} className="photo-card-new">
                                                <div className="photo-container">
                                                    <img
                                                        src={foto.imagen_base64 || (foto.imagen_path ? `http://localhost:8000/static/images/${foto.imagen_path.includes('conforme_') ? foto.imagen_path.split(pathStyle).slice(-2).join('/') : foto.imagen_path.split(pathStyle).pop()}` : '')}
                                                        className="max-h-full max-w-full object-contain"
                                                        alt="Desvío"
                                                    />
                                                </div>
                                                <div className="p-2">
                                                    <p className="text-[8pt] font-bold text-primary-800">{foto.sector}</p>
                                                    <p className="text-[7pt] text-primary-500 italic mt-0.5">{foto.descripcion}</p>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </div>

                        {/* SECCIÓN VOLADORES */}
                        <div className="report-section mt-12 pt-8 border-t-2 border-primary-100">
                            <div className="section-header-print">Control de Insectos Voladores</div>
                            <p className="text-sm text-primary-700 mb-6 font-medium">
                                Equipos de captura UV monitoreados: <span className="text-sanitas font-bold">{informeData.cantidad_trampas_uv || 0} unidades.</span>
                            </p>

                            {informeData.chart_voladores && (
                                <div className="mb-8 break-inside-avoid">
                                    <div className="text-[10pt] font-bold text-primary-800 mb-2 border-b border-primary-100 pb-1">Distribución de Capturas</div>
                                    <div className="chart-box">
                                        <img
                                            src={`data:image/png;base64,${informeData.chart_voladores}`}
                                            className="max-w-full h-auto mx-auto"
                                            style={{ maxHeight: '350px' }}
                                            alt="Gráfico Voladores"
                                        />
                                    </div>
                                </div>
                            )}

                            <SummarySection title="Análisis de Capturas" content={informeData.resumen_voladores} />

                            {informeData.desvios_voladores?.length > 0 && (
                                <div className="mb-8">
                                    <div className="text-[10pt] font-bold text-primary-800 mb-3 border-b border-primary-100 pb-1 uppercase tracking-wider">Hallazgos Fotográficos - Voladores</div>
                                    <div className="grid grid-cols-2 gap-4">
                                        {informeData.desvios_voladores.map((foto, i) => (
                                            <div key={i} className="photo-card-new">
                                                <div className="photo-container">
                                                    <img
                                                        src={foto.imagen_base64 || (foto.imagen_path ? `http://localhost:8000/static/images/${foto.imagen_path.includes('conforme_') ? foto.imagen_path.split(pathStyle).slice(-2).join('/') : foto.imagen_path.split(pathStyle).pop()}` : '')}
                                                        className="max-h-full max-w-full object-contain"
                                                        alt="Desvío"
                                                    />
                                                </div>
                                                <div className="p-2">
                                                    <p className="text-[8pt] font-bold text-primary-800">{foto.sector}</p>
                                                    <p className="text-[7pt] text-primary-500 italic mt-0.5">{foto.descripcion}</p>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </div>

                        {/* SECCIÓN RASTREROS */}
                        <div className="report-section mt-12 pt-8 border-t-2 border-primary-100">
                            <div className="section-header-print">Control de Insectos Rastreros</div>

                            {informeData.aplicaciones_rastreros?.length > 0 && (
                                <div className="mb-6 break-inside-avoid">
                                    <div className="text-[10pt] font-bold text-primary-800 mb-2 border-b border-primary-100 pb-1">Detalle de Aplicaciones Realizadas</div>
                                    <table className="w-full text-[8pt] border-collapse">
                                        <thead>
                                            <tr className="bg-primary-800 text-white text-left">
                                                <th className="p-2 border border-primary-900">Fecha</th>
                                                <th className="p-2 border border-primary-900">Producto Utilizado</th>
                                                <th className="p-2 border border-primary-900 text-center">Cant.</th>
                                                <th className="p-2 border border-primary-900">Sectores Tratados</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {informeData.aplicaciones_rastreros.map((app, i) => (
                                                <tr key={i} className={i % 2 === 0 ? 'bg-white' : 'bg-primary-50'}>
                                                    <td className="p-2 border border-primary-100 font-bold">{app.fecha}</td>
                                                    <td className="p-2 border border-primary-100">
                                                        <div className="font-bold text-primary-900">{app.producto}</div>
                                                        <div className="text-[7pt] text-primary-500 font-medium italic">{app.principio_activo}</div>
                                                    </td>
                                                    <td className="p-2 border border-primary-100 text-center font-bold">{app.cantidad_aplicada}</td>
                                                    <td className="p-2 border border-primary-100 text-[7pt] text-primary-600 leading-tight">{app.sectores_tratados}</td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            )}

                            <SummarySection title="Estado General Rastreros" content={informeData.resumen_rastreros} />
                        </div>

                        {/* CONCLUSIÓN Y CIERRE */}
                        <div className="report-section mt-12 pt-8 border-t-2 border-primary-700">
                            <div className="section-header-print">Conclusión General del Periodo</div>
                            <div className="bg-white p-6 rounded border border-primary-100 text-[10pt] leading-relaxed text-justify italic text-primary-900 shadow-sm">
                                {informeData.conclusion_general}
                            </div>
                        </div>

                        <div className="mt-20 pt-10 text-[9pt] text-primary-400 text-center italic border-t border-primary-100">
                            <p className="mb-1 uppercase font-bold tracking-widest text-primary-300">Sanitas Ambiental</p>
                            Atención al cliente: consultas@sanitasambiental.com.ar<br />
                            Documento generado automáticamente para soporte MIP.
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default PrintPage;
