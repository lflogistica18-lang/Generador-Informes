import api from '../services/api';
import { Check, AlertTriangle, FileText, ChevronRight, Loader2 } from 'lucide-react';

const ReviewPage = () => {
    const setStep = useReportStore((state) => state.setStep);
    const uploadResult = useReportStore((state) => state.uploadResult);
    const setUploadResult = useReportStore((state) => state.setUploadResult);
    const setInformeData = useReportStore((state) => state.setInformeData);
    const cliente = useReportStore((state) => state.cliente);
    const sucursal = useReportStore((state) => state.sucursal);
    const mes = useReportStore((state) => state.mes);
    const anio = useReportStore((state) => state.anio);

    const [activeTab, setActiveTab] = useState('conformes');
    const [isConsolidating, setIsConsolidating] = useState(false);

    const consolidarDatos = async () => {
        setIsConsolidating(true);
        try {
            const response = await api.post('reports/consolidate', {
                conformes: uploadResult.conformes,
                mips: uploadResult.mips,
                informe_base: {
                    cliente_nombre: cliente?.nombre,
                    sucursal_nombre: sucursal?.nombre,
                    mes: mes,
                    anio: anio
                }
            });
            setInformeData(response.data);
            setStep('roedores');
        } catch (err) {
            console.error('Error al consolidar:', err);
            alert('Error al consolidar los datos. Por favor reintente.');
        } finally {
            setIsConsolidating(false);
        }
    };

    const handleNext = () => {
        consolidarDatos();
    };

    const updateRastrerosField = (index, field, value) => {
        if (!uploadResult) return;
        const newConformes = [...uploadResult.conformes];
        // Ensure rastreros object exists
        if (!newConformes[index].rastreros) {
            newConformes[index].rastreros = {};
        }
        newConformes[index].rastreros = {
            ...newConformes[index].rastreros,
            [field]: value
        };
        setUploadResult({
            ...uploadResult,
            conformes: newConformes
        });
    };

    if (!uploadResult) {
        return <div className="p-8 text-center text-primary-500">No hay datos para revisar.</div>;
    }

    const { conformes, mips, errores, campos_faltantes } = uploadResult;

    return (
        <div className="max-w-6xl mx-auto mt-8 relative">
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h2 className="text-2xl font-bold text-primary-900">Revisión de Datos Extraídos</h2>
                    <p className="text-primary-600">Verifica los datos de las visitas y completa los campos faltantes.</p>
                </div>
                <button
                    onClick={handleNext}
                    disabled={isConsolidating}
                    className="btn-primary min-w-[200px]"
                >
                    {isConsolidating ? (
                        <>
                            <Loader2 className="animate-spin" size={18} /> Consolidando...
                        </>
                    ) : (
                        <>
                            Siguiente: Roedores <ChevronRight size={18} />
                        </>
                    )}
                </button>
            </div>

            {/* Stats Cards */}
            <div className="grid grid-cols-4 gap-4 mb-8">
                <div className="card p-4 flex items-center gap-3 border-l-4 border-l-sanitas">
                    <FileText className="text-sanitas" size={24} />
                    <div>
                        <p className="text-sm text-primary-500 font-medium">Conformes Procesados</p>
                        <p className="text-2xl font-bold text-primary-900">{conformes?.length || 0}</p>
                    </div>
                </div>
                <div className="card p-4 flex items-center gap-3 border-l-4 border-l-primary-500">
                    <FileText className="text-primary-500" size={24} />
                    <div>
                        <p className="text-sm text-primary-500 font-medium">MIPs Procesados</p>
                        <p className="text-2xl font-bold text-primary-900">{mips?.length || 0}</p>
                    </div>
                </div>
                <div className="card p-4 flex items-center gap-3 border-l-4 border-l-red-500 bg-red-50">
                    <AlertTriangle className="text-red-500" size={24} />
                    <div>
                        <p className="text-sm text-red-600 font-medium">Errores</p>
                        <p className="text-2xl font-bold text-red-700">{errores?.length || 0}</p>
                    </div>
                </div>
                <div className="card p-4 flex items-center gap-3 border-l-4 border-l-amber-500 bg-amber-50">
                    <AlertTriangle className="text-amber-500" size={24} />
                    <div>
                        <p className="text-sm text-amber-600 font-medium">Campos Faltantes</p>
                        <p className="text-2xl font-bold text-amber-700">{campos_faltantes?.length || 0}</p>
                    </div>
                </div>
            </div>

            {/* Tabs */}
            <div className="flex border-b border-primary-200 mb-6">
                <button
                    className={`px-4 py-2 font-medium text-sm transition-colors border-b-2 ${activeTab === 'conformes'
                        ? 'border-sanitas text-sanitas'
                        : 'border-transparent text-primary-500 hover:text-primary-700'
                        }`}
                    onClick={() => setActiveTab('conformes')}
                >
                    Conformes ({conformes?.length})
                </button>
                <button
                    className={`px-4 py-2 font-medium text-sm transition-colors border-b-2 ${activeTab === 'mips'
                        ? 'border-sanitas text-sanitas'
                        : 'border-transparent text-primary-500 hover:text-primary-700'
                        }`}
                    onClick={() => setActiveTab('mips')}
                >
                    Registros MIP ({mips?.length})
                </button>
                <button
                    className={`px-4 py-2 font-medium text-sm transition-colors border-b-2 ${activeTab === 'faltantes'
                        ? 'border-amber-500 text-amber-600'
                        : 'border-transparent text-primary-500 hover:text-primary-700'
                        }`}
                    onClick={() => setActiveTab('faltantes')}
                >
                    Datos Faltantes ({campos_faltantes?.length})
                </button>
            </div>

            {/* Content */}
            <div className="bg-white rounded-lg shadow-sm border border-primary-200 min-h-[400px] p-6 overflow-x-auto">
                {activeTab === 'conformes' && (
                    <div className="space-y-6">
                        {conformes?.map((conf, idx) => (
                            <div key={idx} className="border border-primary-200 rounded-lg p-4">
                                <div className="flex justify-between items-start mb-4 border-b border-primary-100 pb-2">
                                    <div>
                                        <h4 className="font-bold text-lg text-primary-800">Visita: {conf.fecha || 'Sin Fecha'}</h4>
                                        <p className="text-sm text-primary-500">Track ID: {conf.track_id} — Operario: {conf.operario}</p>
                                    </div>
                                    <span className="bg-primary-100 text-primary-700 text-xs px-2 py-1 rounded-full font-medium">Conforme</span>
                                </div>

                                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                                    {/* Servicios */}
                                    {conf.rastreros && (
                                        <div className="p-3 bg-gray-50 rounded border border-gray-100">
                                            <h5 className="font-semibold text-primary-700 mb-2">Rastreros</h5>
                                            <p>Modo: {conf.rastreros.modo}</p>
                                            <p>Producto: {conf.rastreros.producto || <span className="text-red-500 italic">Faltante</span>}</p>

                                            {/* Inputs Editables */}
                                            <div className="mt-2 grid grid-cols-2 gap-2">
                                                <div>
                                                    <label className="text-xs text-primary-500 block">Dosis</label>
                                                    <input
                                                        type="text"
                                                        className="w-full text-xs p-1 border rounded"
                                                        placeholder="Ej: 50cc"
                                                        value={conf.rastreros.dosis || ''}
                                                        onChange={(e) => updateRastrerosField(idx, 'dosis', e.target.value)}
                                                    />
                                                </div>
                                                <div>
                                                    <label className="text-xs text-primary-500 block">Cant. Solución</label>
                                                    <input
                                                        type="text"
                                                        className="w-full text-xs p-1 border rounded"
                                                        placeholder="Ej: 5L"
                                                        value={conf.rastreros.cantidad || ''}
                                                        onChange={(e) => updateRastrerosField(idx, 'cantidad', e.target.value)}
                                                    />
                                                </div>
                                            </div>

                                            <p className="mt-2 text-sm text-primary-600 bg-white p-2 rounded border border-gray-200/50 italic leading-relaxed">
                                                <span className="font-bold text-xs uppercase not-italic block mb-1 text-primary-400">Observaciones:</span>
                                                {conf.rastreros.comentarios || 'Sin observaciones'}
                                            </p>
                                        </div>
                                    )}
                                    {conf.voladores && (
                                        <div className="p-3 bg-gray-50 rounded border border-gray-100">
                                            <h5 className="font-semibold text-primary-700 mb-2">Voladores</h5>
                                            <p>Modo: {conf.voladores.modo}</p>
                                            <p>Producto: {conf.voladores.producto || <span className="text-red-500 italic">Faltante</span>}</p>
                                            <p className="mt-2 text-sm text-primary-600 bg-white p-2 rounded border border-gray-200/50 italic leading-relaxed">
                                                <span className="font-bold text-xs uppercase not-italic block mb-1 text-primary-400">Observaciones:</span>
                                                {conf.voladores.comentarios || 'Sin observaciones'}
                                            </p>
                                        </div>
                                    )}
                                    {conf.roedores && (
                                        <div className="p-3 bg-gray-50 rounded border border-gray-100">
                                            <h5 className="font-semibold text-primary-700 mb-2">Roedores</h5>
                                            <p>Modo: {conf.roedores.modo}</p>
                                            <p>Consumo: {conf.roedores.consumo} | Repos: {conf.roedores.reposicion}</p>
                                            <p className="mt-2 text-sm text-primary-600 bg-white p-2 rounded border border-gray-200/50 italic leading-relaxed">
                                                <span className="font-bold text-xs uppercase not-italic block mb-1 text-primary-400">Observaciones:</span>
                                                {conf.roedores.observaciones || 'Sin observaciones'}
                                            </p>
                                        </div>
                                    )}
                                </div>

                                {/* Desvios */}
                                {conf.desvios?.length > 0 && (
                                    <div className="mt-4 pt-2 border-t border-primary-100">
                                        <p className="text-xs font-semibold text-primary-500 uppercase mb-2">Desvíos Fotográficos ({conf.desvios.length})</p>
                                        <div className="flex gap-2 overflows-x-auto">
                                            {conf.desvios.map((d, i) => (
                                                <div key={i} className="w-24 h-24 bg-gray-100 rounded border border-gray-200 relative overflow-hidden group">
                                                    {/* Imagen Base64 preview (pequeño) */}
                                                    {d.imagen_base64 && (
                                                        <img src={d.imagen_base64} alt="Desvío" className="w-full h-full object-cover" />
                                                    )}
                                                    <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center p-1">
                                                        <p className="text-[10px] text-white text-center leading-tight">{d.sector}</p>
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                )}

                {/* Placeholder para otras tabs por brevedad */}
                {activeTab === 'mips' && (
                    <div className="space-y-6">
                        {mips?.length === 0 && (
                            <p className="text-primary-500 text-center py-8">No se cargaron registros MIP.</p>
                        )}
                        {mips?.map((mip, idx) => (
                            <div key={idx} className="border border-primary-200 rounded-lg p-4">
                                {/* Encabezado MIP */}
                                <div className="flex justify-between items-start mb-4 border-b border-primary-100 pb-2">
                                    <div>
                                        <h4 className="font-bold text-lg text-primary-800">MIP: {mip.fecha || 'Sin Fecha'}</h4>
                                        <p className="text-sm text-primary-500">
                                            Trabajo ID: {mip.trabajo_id} — Cliente: {mip.cliente} — Sucursal: {mip.sucursal}
                                        </p>
                                    </div>
                                    <span className="bg-primary-700 text-white text-xs px-2 py-1 rounded-full font-medium">Registro MIP</span>
                                </div>

                                {/* Dashboard */}
                                {mip.dashboard && (
                                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
                                        <div className="p-3 bg-amber-50 border border-amber-100 rounded text-center">
                                            <p className="text-xs text-amber-600 font-medium">Consumos</p>
                                            <p className="text-xl font-bold text-amber-800">{mip.dashboard.total_consumos}</p>
                                            <p className="text-xs text-amber-500">{mip.dashboard.gramos_consumos} gr</p>
                                        </div>
                                        <div className="p-3 bg-red-50 border border-red-100 rounded text-center">
                                            <p className="text-xs text-red-600 font-medium">Capturas</p>
                                            <p className="text-xl font-bold text-red-800">{mip.dashboard.total_capturas}</p>
                                        </div>
                                        <div className="p-3 bg-blue-50 border border-blue-100 rounded text-center">
                                            <p className="text-xs text-blue-600 font-medium">Reposiciones</p>
                                            <p className="text-xl font-bold text-blue-800">{mip.dashboard.total_reposiciones}</p>
                                        </div>
                                        <div className="p-3 bg-green-50 border border-green-100 rounded text-center">
                                            <p className="text-xs text-green-600 font-medium">Operarios</p>
                                            <p className="text-xl font-bold text-green-800">{mip.dashboard.total_operarios}</p>
                                        </div>
                                    </div>
                                )}

                                {/* Productos */}
                                {mip.productos?.length > 0 && (
                                    <div className="mb-4">
                                        <p className="text-xs font-semibold text-primary-500 uppercase mb-1">Productos Utilizados</p>
                                        <div className="flex flex-wrap gap-2">
                                            {mip.productos.map((p, i) => (
                                                <span key={i} className="bg-primary-100 text-primary-700 text-xs px-2 py-1 rounded">{p}</span>
                                            ))}
                                        </div>
                                    </div>
                                )}

                                {/* Tabla de Relevamiento (primeras 10 filas) */}
                                {mip.relevamiento?.length > 0 && (
                                    <div>
                                        <p className="text-xs font-semibold text-primary-500 uppercase mb-2">
                                            Relevamiento ({mip.relevamiento.length} puntos)
                                        </p>
                                        <div className="overflow-x-auto max-h-[500px] border border-gray-100 rounded-md">
                                            <table className="text-xs w-full border-collapse">
                                                <thead className="sticky top-0 bg-gray-100 z-20 shadow-sm">
                                                    <tr>
                                                        <th className="text-left p-3 border-b font-bold text-primary-800">Sector</th>
                                                        <th className="text-left p-3 border-b font-bold text-primary-800">Código</th>
                                                        <th className="text-left p-3 border-b font-bold text-primary-800">Herramienta</th>
                                                        <th className="text-left p-3 border-b font-bold text-primary-800">Estado</th>
                                                        <th className="text-right p-3 border-b font-bold text-primary-800">Consumo (gr)</th>
                                                        <th className="text-right p-3 border-b font-bold text-primary-800">Capturas</th>
                                                        <th className="text-right p-3 border-b font-bold text-primary-800">Repos.</th>
                                                    </tr>
                                                </thead>
                                                <tbody>
                                                    {mip.relevamiento.map((punto, i) => (
                                                        <tr key={i} className={`border-b border-gray-50 hover:bg-primary-50/50 transition-colors ${punto.consumos > 0 ? 'bg-amber-50/20' : ''} ${punto.capturas > 0 ? 'bg-red-50/20' : ''}`}>
                                                            <td className="p-3 text-primary-600 font-medium">{punto.subseccion || '—'}</td>
                                                            <td className="p-3 font-bold text-primary-900">{punto.codigo || '—'}</td>
                                                            <td className="p-3 text-primary-500">{punto.herramienta || '—'}</td>
                                                            <td className="p-3">
                                                                <span className={`px-2 py-0.5 rounded text-[10px] uppercase font-bold tracking-wider shadow-sm ${punto.estado === 'Sin Novedad' ? 'bg-green-500 text-white' :
                                                                    punto.estado === 'Activa' ? 'bg-amber-500 text-white' :
                                                                        'bg-gray-400 text-white'
                                                                    }`}>{punto.estado || '—'}</span>
                                                            </td>
                                                            <td className={`p-3 text-right font-bold text-sm ${punto.consumos > 0 ? 'text-amber-700' : 'text-gray-300'}`}>
                                                                {punto.consumos > 0 ? `${punto.consumos} gr` : '0'}
                                                            </td>
                                                            <td className={`p-3 text-right font-bold text-sm ${punto.capturas > 0 ? 'text-red-700' : 'text-gray-300'}`}>
                                                                {punto.capturas > 0 ? punto.capturas : '0'}
                                                            </td>
                                                            <td className="p-3 text-right text-gray-400 font-medium">
                                                                {punto.reposiciones > 0 ? punto.reposiciones : '—'}
                                                            </td>
                                                        </tr>
                                                    ))}
                                                </tbody>
                                            </table>
                                        </div>
                                    </div>
                                )}

                                {/* Comentarios del MIP */}
                                {mip.comentarios && (
                                    <div className="mt-3 pt-2 border-t border-primary-100">
                                        <p className="text-xs font-semibold text-primary-500 uppercase mb-1">Comentarios</p>
                                        <p className="text-sm text-primary-700 whitespace-pre-wrap">{mip.comentarios}</p>
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                )}
                {activeTab === 'faltantes' && (
                    <div className="space-y-4">
                        {campos_faltantes?.map((f, i) => (
                            <div key={i} className="p-4 bg-amber-50 border border-amber-200 rounded text-amber-800">
                                <p className="font-bold">Archivo: {f.archivo}</p>
                                <p className="text-sm">Fecha: {f.fecha}</p>
                                <ul className="list-disc pl-5 mt-2 text-sm">
                                    {f.campos.map((c, j) => <li key={j}>{c}</li>)}
                                </ul>
                            </div>
                        ))}
                        {campos_faltantes?.length === 0 && <p className="text-green-600">¡Todo completo! No se detectaron campos faltantes.</p>}
                    </div>
                )}
            </div>
        </div>
    );
};

export default ReviewPage;
