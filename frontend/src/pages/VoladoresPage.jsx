import React, { useState, useEffect } from 'react';
import { useReportStore } from '../store/useReportStore';
import { ChevronRight, ChevronLeft, Plus, Trash2, PieChart } from 'lucide-react';
import api from '../services/api';

const VoladoresPage = () => {
    const setStep = useReportStore((state) => state.setStep);
    const uploadResult = useReportStore((state) => state.uploadResult);
    const cliente = useReportStore((state) => state.cliente);
    const sucursal = useReportStore((state) => state.sucursal);
    const mes = useReportStore((state) => state.mes);
    const anio = useReportStore((state) => state.anio);
    const setInformeData = useReportStore((state) => state.setInformeData);
    const informeData = useReportStore((state) => state.informeData);

    // Especies fijas solicitadas por el usuario
    const ESPECIES_FIJAS = ['Moscas', 'Mosquitos', 'Polillas', 'Lepidópteros', 'Coleópteros', 'Dípteros', 'Otros'];

    // Estado local para capturas de voladores
    const [capturas, setCapturas] = useState([]);
    const [especies, setEspecies] = useState(ESPECIES_FIJAS);
    const [nuevaEspecie, setNuevaEspecie] = useState('');

    // Cargar datos iniciales si ya existen o crear estructura base
    useEffect(() => {
        if (!informeData) {
            consolidarDatos();
        } else if (informeData.capturas_trampas_uv && informeData.capturas_trampas_uv.length > 0) {
            // Asegurar que las capturas existentes tengan todas las especies fijas
            const capturasActualizadas = informeData.capturas_trampas_uv.map(c => {
                const nuevasCapturas = { ...c.capturas };
                ESPECIES_FIJAS.forEach(esp => {
                    if (nuevasCapturas[esp] === undefined) nuevasCapturas[esp] = 0;
                });
                return { ...c, capturas: nuevasCapturas };
            });
            setCapturas(capturasActualizadas);

            // Combinar especies guardadas con las fijas
            const todasEspecies = Array.from(new Set([...ESPECIES_FIJAS, ...(informeData.especies_voladores || [])]));
            setEspecies(todasEspecies);
        } else {
            // Crear base según cantidad de trampas UV (usar cantidad_trampas_uv del store o 12 por defecto)
            const nTrampas = informeData?.cantidad_trampas_uv || 12;
            const inicial = Array.from({ length: nTrampas }, (_, i) => ({
                trampa: `TUV ${i + 1}`,
                capturas: Object.fromEntries(ESPECIES_FIJAS.map(e => [e, 0]))
            }));
            setCapturas(inicial);
        }
    }, []);

    const consolidarDatos = async () => {
        try {
            const response = await api.post('/reports/consolidate', {
                conformes: uploadResult.conformes,
                mips: uploadResult.mips,
                informe_base: {
                    cliente_nombre: cliente.nombre,
                    sucursal_nombre: sucursal.nombre,
                    sucursal_direccion: 'Dirección Mock', // Debería venir del cliente/sucursal real
                    mes: mes,
                    anio: anio
                }
            });
            setInformeData(response.data);
            if (response.data.capturas_trampas_uv?.length > 0) {
                setCapturas(response.data.capturas_trampas_uv);
            }
        } catch (err) {
            console.error('Error al consolidar:', err);
        }
    };

    const updateCaptura = (trampaIdx, especie, valor) => {
        const nuevas = [...capturas];
        nuevas[trampaIdx].capturas[especie] = parseInt(valor) || 0;
        setCapturas(nuevas);
    };

    const addEspecie = () => {
        if (!nuevaEspecie || especies.includes(nuevaEspecie)) return;
        setEspecies([...especies, nuevaEspecie]);
        const nuevas = capturas.map(c => ({
            ...c,
            capturas: { ...c.capturas, [nuevaEspecie]: 0 }
        }));
        setCapturas(nuevas);
        setNuevaEspecie('');
    };

    const handleNext = () => {
        setInformeData({
            ...informeData,
            capturas_trampas_uv: capturas,
            especies_voladores: especies
        });
        setStep('summaries');
    };

    return (
        <div className="max-w-6xl mx-auto mt-8">
            <div className="flex justify-between items-center mb-6">
                <div>
                    <h2 className="text-2xl font-bold text-primary-900">Capturas de Insectos Voladores</h2>
                    <p className="text-primary-600">Ingresa el conteo de individuos por trampa UV y especie.</p>
                </div>
                <div className="flex gap-3">
                    <button onClick={() => setStep('roedores')} className="btn-secondary"><ChevronLeft size={18} /> Atrás</button>
                    <button onClick={handleNext} className="btn-primary">Continuar <ChevronRight size={18} /></button>
                </div>
            </div>

            <div className="card mb-6">
                <div className="flex items-center gap-4 mb-6 p-4 bg-primary-50 rounded-lg">
                    <PieChart className="text-sanitas" size={32} />
                    <div className="flex-1">
                        <h3 className="font-bold text-primary-800">Gestionar Especies y Trampas</h3>
                        <div className="flex gap-2 mt-2">
                            <input
                                type="text"
                                placeholder="Nueva especie (ej: Dípteros)"
                                className="input-field text-sm py-1"
                                value={nuevaEspecie}
                                onChange={(e) => setNuevaEspecie(e.target.value)}
                            />
                            <button onClick={addEspecie} className="btn-accent py-1 px-3 text-sm"><Plus size={16} /> Añadir</button>
                        </div>
                    </div>
                </div>

                <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                        <thead>
                            <tr className="bg-primary-100">
                                <th className="p-3 text-left border-b border-primary-200 sticky left-0 bg-primary-100 z-10 w-32 font-bold">Trampa / ID</th>
                                {especies.map(esp => (
                                    <th key={esp} className="p-3 text-center border-b border-primary-200 font-bold">{esp}</th>
                                ))}
                                <th className="p-3 text-center border-b border-primary-200 font-bold bg-primary-200">Total</th>
                                <th className="p-3 text-center border-b border-primary-200">Acciones</th>
                            </tr>
                        </thead>
                        <tbody>
                            {capturas.map((cap, idx) => {
                                const totalRow = Object.values(cap.capturas).reduce((a, b) => a + b, 0);
                                return (
                                    <tr key={idx} className="hover:bg-primary-50">
                                        <td className="p-3 border-b border-primary-100 font-medium sticky left-0 bg-white z-10">
                                            <input
                                                type="text"
                                                value={cap.trampa}
                                                onChange={(e) => {
                                                    const n = [...capturas];
                                                    n[idx].trampa = e.target.value;
                                                    setCapturas(n);
                                                }}
                                                className="bg-transparent border-none focus:ring-0 w-full font-bold text-primary-700"
                                            />
                                        </td>
                                        {especies.map(esp => (
                                            <td key={esp} className="p-3 border-b border-primary-100 text-center">
                                                <input
                                                    type="number"
                                                    min="0"
                                                    className="w-16 p-1 text-center bg-white border border-primary-200 rounded focus:ring-1 focus:ring-sanitas outline-none"
                                                    value={cap.capturas[esp] || 0}
                                                    onChange={(e) => updateCaptura(idx, esp, e.target.value)}
                                                />
                                            </td>
                                        ))}
                                        <td className="p-3 border-b border-primary-100 text-center font-bold text-primary-800 bg-primary-50/50">
                                            {totalRow}
                                        </td>
                                        <td className="p-3 border-b border-primary-100 text-center">
                                            <button
                                                onClick={() => {
                                                    const n = capturas.filter((_, i) => i !== idx);
                                                    setCapturas(n);
                                                }}
                                                className="text-red-500 hover:text-red-700 transition-colors"
                                                title="Eliminar Trampa"
                                            >
                                                <Trash2 size={18} />
                                            </button>
                                        </td>
                                    </tr>
                                );
                            })}
                        </tbody>
                    </table>
                </div>

                <div className="mt-6 flex justify-between items-center text-sm text-primary-500">
                    <p>* Los datos de voladores se ingresan manualmente según planillas de campo.</p>
                    <button
                        onClick={() => setCapturas([...capturas, { trampa: `TUV ${capturas.length + 1}`, capturas: Object.fromEntries(especies.map(e => [e, 0])) }])}
                        className="text-sanitas hover:text-sanitas-dark font-bold flex items-center gap-1"
                    >
                        <Plus size={16} /> Añadir Trampa UV
                    </button>
                </div>
            </div>
        </div>
    );
};

export default VoladoresPage;
