import React, { useState } from 'react';
import { useReportStore } from '../store/useReportStore';
import { ChevronRight, Calendar } from 'lucide-react';

const SelectClientPage = () => {
    const setStep = useReportStore((state) => state.setStep);
    const setCliente = useReportStore((state) => state.setCliente);
    const setSucursal = useReportStore((state) => state.setSucursal);
    const setPeriodo = useReportStore((state) => state.setPeriodo);

    // Estado local para form
    const [clienteSel, setClienteSel] = useState('');
    const [sucursalSel, setSucursalSel] = useState('');
    const [mes, setMes] = useState(new Date().getMonth() + 1); // 1-12
    const [anio, setAnio] = useState(new Date().getFullYear());
    const [direccionSel, setDireccionSel] = useState('');
    // Mock data (luego vendrá del backend)
    const clientes = [
        { id: '1', nombre: 'CALSA', sucursales: [{ id: 's1', nombre: 'Planta 4' }, { id: 's2', nombre: 'Planta 1' }] },
        { id: '2', nombre: 'Nestlé', sucursales: [{ id: 's3', nombre: 'Magdalena' }] },
    ];

    const handleNext = () => {
        if (!clienteSel || !sucursalSel) return;

        // Guardar en store (Usando los valores de texto directamente)
        // Buscamos si existe en la lista para obtener un ID, sino generamos uno
        const existingClient = clientes.find(c => c.nombre === clienteSel);

        const clienteObj = {
            id: existingClient ? existingClient.id : `custom-${Date.now()}`,
            nombre: clienteSel,
            sucursales: []
        };

        const sucursalObj = {
            id: `suc-${Date.now()}`,
            nombre: sucursalSel,
            direccion: direccionSel
        };

        setCliente(clienteObj);
        setSucursal(sucursalObj);

        // Convertir mes número a nombre
        const mesNombre = new Date(anio, mes - 1).toLocaleString('es-ES', { month: 'long' });
        setPeriodo(mesNombre.charAt(0).toUpperCase() + mesNombre.slice(1), anio);

        // Avanzar
        setStep('upload');
    };

    return (
        <div className="max-w-2xl mx-auto mt-10">
            <div className="mb-8 text-center">
                <h2 className="text-3xl font-bold text-primary-900">Nuevo Informe MIP</h2>
                <p className="text-primary-600 mt-2">Selecciona el cliente y el período para comenzar.</p>
            </div>

            <div className="card space-y-6">
                {/* Cliente */}
                <div>
                    <label className="block text-sm font-medium text-primary-700 mb-1">Cliente</label>
                    <div className="space-y-2">
                        <select
                            className="input-field text-sm"
                            onChange={(e) => {
                                const cId = e.target.value;
                                const cObj = clientes.find(c => c.id === cId);
                                if (cObj) {
                                    setClienteSel(cObj.nombre);
                                    setSucursalSel(''); // Reset sucursal
                                }
                            }}
                        >
                            <option value="">-- Seleccionar de lista (Opcional) --</option>
                            {clientes.map(c => (
                                <option key={c.id} value={c.id}>{c.nombre}</option>
                            ))}
                        </select>
                        <input
                            type="text"
                            className="input-field"
                            placeholder="Nombre del Cliente"
                            value={clienteSel}
                            onChange={(e) => setClienteSel(e.target.value)}
                        />
                    </div>
                </div>

                {/* Sucursal */}
                <div>
                    <label className="block text-sm font-medium text-primary-700 mb-1">Sucursal / Planta</label>
                    <div className="space-y-2">
                        <select
                            className="input-field text-sm"
                            onChange={(e) => setSucursalSel(e.target.value)}
                            disabled={!clienteSel}
                        >
                            <option value="">-- Seleccionar de lista (Opcional) --</option>
                            {/* Buscar si el nombre tipeado coincide con alguno de la lista para mostrar sus sucursales */}
                            {clientes.find(c => c.nombre === clienteSel)?.sucursales.map(s => (
                                <option key={s.id} value={s.nombre}>{s.nombre}</option>
                            )) || <option disabled>Escribe el nombre del cliente arriba</option>}
                        </select>
                        <input
                            type="text"
                            className="input-field"
                            placeholder="Nombre de la Sucursal o Planta"
                            value={sucursalSel}
                            onChange={(e) => setSucursalSel(e.target.value)}
                        />
                        <input
                            type="text"
                            className="input-field mt-2"
                            placeholder="Dirección de la Planta / Sucursal"
                            value={direccionSel}
                            onChange={(e) => setDireccionSel(e.target.value)}
                        />
                    </div>
                </div>

                {/* Período (Mes/Año) */}
                <div className="grid grid-cols-2 gap-4">
                    <div>
                        <label className="block text-sm font-medium text-primary-700 mb-1">Mes</label>
                        <select
                            className="input-field"
                            value={mes}
                            onChange={(e) => setMes(parseInt(e.target.value))}
                        >
                            {Array.from({ length: 12 }, (_, i) => (
                                <option key={i + 1} value={i + 1}>{new Date(0, i).toLocaleString('es-ES', { month: 'long' })}</option>
                            ))}
                        </select>
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-primary-700 mb-1">Año</label>
                        <input
                            type="number"
                            className="input-field"
                            value={anio}
                            onChange={(e) => setAnio(parseInt(e.target.value))}
                        />
                    </div>
                </div>

                {/* Botón Siguiente */}
                <div className="pt-4 flex justify-end">
                    <button
                        onClick={handleNext}
                        disabled={!clienteSel || !sucursalSel}
                        className={`btn-primary w-full sm:w-auto ${(!clienteSel || !sucursalSel) ? 'opacity-50 cursor-not-allowed' : ''}`}
                    >
                        Comenzar <ChevronRight size={18} />
                    </button>
                </div>
            </div>
        </div>
    );
};

export default SelectClientPage;
