import React, { useState, useEffect } from 'react';
import { useReportStore } from '../store/useReportStore';
import { ChevronRight, ChevronLeft, Plus, Trash2, LayoutGrid, Info } from 'lucide-react';

const RoedoresConfigPage = () => {
    const setStep = useReportStore((state) => state.setStep);
    const informeData = useReportStore((state) => state.informeData);
    const setInformeData = useReportStore((state) => state.setInformeData);

    const TIPOS_CEBADERA = [
        { id: 'CB', nombre: 'Cebadera CB (Cebo Rodenticida)', desc: 'Contiene bloques parafinados o cereales.' },
        { id: 'PG', nombre: 'Cebadera PG (Plaqueta Pegamento)', desc: 'Contiene placa adhesiva con atrayente.' }
    ];

    const [sectores, setSectores] = useState([]);
    const [nuevoSector, setNuevoSector] = useState('');

    useEffect(() => {
        if (informeData?.configuracion_roedores?.sectores) {
            setSectores(informeData.configuracion_roedores.sectores);
        } else {
            // Inicializar con estructura base
            setSectores([
                { nombre: 'Perímetro Externo', cantidad_cb: 0, cantidad_pg: 0 },
                { nombre: 'Perímetro Interno', cantidad_cb: 0, cantidad_pg: 0 }
            ]);
        }
    }, [informeData]);

    const addSector = () => {
        if (!nuevoSector || sectores.find(s => s.nombre.toLowerCase() === nuevoSector.toLowerCase())) return;
        setSectores([...sectores, { nombre: nuevoSector, cantidad_cb: 0, cantidad_pg: 0 }]);
        setNuevoSector('');
    };

    const removeSector = (idx) => {
        setSectores(sectores.filter((_, i) => i !== idx));
    };

    const updateSector = (idx, field, value) => {
        const nuevos = [...sectores];
        nuevos[idx][field] = parseInt(value) || 0;
        setSectores(nuevos);
    };

    const handleNext = () => {
        // Calcular totales estrictos por tipo de dispositivo
        const totalCB = sectores.reduce((acc, s) => acc + (parseInt(s.cantidad_cb) || 0), 0);
        const totalPG = sectores.reduce((acc, s) => acc + (parseInt(s.cantidad_pg) || 0), 0);
        setInformeData({
            ...informeData,
            estaciones_perimetro_externo: totalCB,
            estaciones_perimetro_interno: totalPG,
            configuracion_roedores: {
                sectores: sectores,
                ultima_actualizacion: new Date().toISOString()
            }
        });
        setStep('voladores');
    };

    return (
        <div className="max-w-5xl mx-auto mt-8">
            <div className="flex justify-between items-center mb-6">
                <div>
                    <h2 className="text-2xl font-bold text-primary-900">Configuración de Roedores</h2>
                    <p className="text-primary-600">Define los sectores y la cantidad de dispositivos (CB y PG) instalados.</p>
                </div>
                <div className="flex gap-3">
                    <button onClick={() => setStep('review')} className="btn-secondary">
                        <ChevronLeft size={18} /> Atrás
                    </button>
                    <button onClick={handleNext} className="btn-primary">
                        Continuar <ChevronRight size={18} />
                    </button>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Panel de Ayuda/Tipos */}
                <div className="lg:col-span-1">
                    <div className="card bg-sanitas-light/10 border-sanitas-light">
                        <div className="flex items-center gap-2 mb-4 text-sanitas font-bold">
                            <Info size={20} />
                            <h3>Tipos de Dispositivos</h3>
                        </div>
                        <div className="space-y-4">
                            {TIPOS_CEBADERA.map(tipo => (
                                <div key={tipo.id} className="bg-white p-3 rounded-md border border-sanitas-light/30">
                                    <span className="font-bold text-sanitas text-sm">{tipo.nombre}</span>
                                    <p className="text-xs text-primary-600 mt-1">{tipo.desc}</p>
                                </div>
                            ))}
                        </div>
                        <div className="mt-6 p-3 bg-white/50 rounded text-xs text-primary-500 italic">
                            Tip: Los sectores que incluyan "Externo" o "Interno" en su nombre se sumarán automáticamente a los totales de portada.
                        </div>
                    </div>
                </div>

                {/* Grilla de Sectores */}
                <div className="lg:col-span-2">
                    <div className="card">
                        <div className="flex items-center gap-4 mb-6 p-4 bg-primary-50 rounded-lg">
                            <LayoutGrid className="text-sanitas" size={32} />
                            <div className="flex-1">
                                <h3 className="font-bold text-primary-800">Sectores y Cantidades</h3>
                                <div className="flex gap-2 mt-2">
                                    <input
                                        type="text"
                                        placeholder="Nombre del sector (ej: Depósito, Comedor)"
                                        className="input-field text-sm py-1"
                                        value={nuevoSector}
                                        onChange={(e) => setNuevoSector(e.target.value)}
                                        onKeyPress={(e) => e.key === 'Enter' && addSector()}
                                    />
                                    <button onClick={addSector} className="btn-accent py-1 px-3 text-sm">
                                        <Plus size={16} /> Añadir
                                    </button>
                                </div>
                            </div>
                        </div>

                        <div className="overflow-x-auto">
                            <table className="w-full text-sm">
                                <thead>
                                    <tr className="bg-primary-100 uppercase text-[10px] tracking-wider font-bold">
                                        <th className="p-3 text-left border-b border-primary-200">Sector</th>
                                        <th className="p-3 text-center border-b border-primary-200">Cant. CB</th>
                                        <th className="p-3 text-center border-b border-primary-200">Cant. PG</th>
                                        <th className="p-3 text-center border-b border-primary-200 bg-primary-200">Total</th>
                                        <th className="p-3 text-center border-b border-primary-200 w-16"></th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {sectores.map((s, idx) => (
                                        <tr key={idx} className="hover:bg-primary-50 border-b border-primary-50">
                                            <td className="p-3 font-semibold text-primary-800">
                                                <input
                                                    type="text"
                                                    value={s.nombre}
                                                    onChange={(e) => {
                                                        const n = [...sectores];
                                                        n[idx].nombre = e.target.value;
                                                        setSectores(n);
                                                    }}
                                                    className="bg-transparent border-none focus:ring-0 p-0 w-full"
                                                />
                                            </td>
                                            <td className="p-3 text-center">
                                                <input
                                                    type="number"
                                                    min="0"
                                                    className="w-16 p-1 text-center bg-white border border-primary-200 rounded focus:ring-1 focus:ring-sanitas outline-none"
                                                    value={s.cantidad_cb}
                                                    onChange={(e) => updateSector(idx, 'cantidad_cb', e.target.value)}
                                                />
                                            </td>
                                            <td className="p-3 text-center">
                                                <input
                                                    type="number"
                                                    min="0"
                                                    className="w-16 p-1 text-center bg-white border border-primary-200 rounded focus:ring-1 focus:ring-sanitas outline-none"
                                                    value={s.cantidad_pg}
                                                    onChange={(e) => updateSector(idx, 'cantidad_pg', e.target.value)}
                                                />
                                            </td>
                                            <td className="p-3 text-center font-bold text-sanitas bg-primary-50/50">
                                                {s.cantidad_cb + s.cantidad_pg}
                                            </td>
                                            <td className="p-3 text-center">
                                                <button
                                                    onClick={() => removeSector(idx)}
                                                    className="text-primary-300 hover:text-red-500 transition-colors"
                                                >
                                                    <Trash2 size={16} />
                                                </button>
                                            </td>
                                        </tr>
                                    ))}
                                    {sectores.length === 0 && (
                                        <tr>
                                            <td colSpan="5" className="p-10 text-center text-primary-400 italic">
                                                No hay sectores definidos. Agrega uno arriba.
                                            </td>
                                        </tr>
                                    )}
                                </tbody>
                            </table>
                        </div>

                        <div className="mt-6 pt-4 border-t border-primary-100 flex justify-end gap-8">
                            <div className="text-right">
                                <span className="block text-xs text-primary-400 uppercase font-bold">Total Dispositivos</span>
                                <span className="text-2xl font-black text-primary-900 leading-none">
                                    {sectores.reduce((acc, s) => acc + s.cantidad_cb + s.cantidad_pg, 0)}
                                </span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default RoedoresConfigPage;
