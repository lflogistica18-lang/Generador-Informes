import React from 'react';
import { useReportStore } from '../../store/useReportStore';
import {
    Building2, FileText, Upload, PieChart,
    Settings, LogOut, CheckCircle, AlertCircle
} from 'lucide-react';
import { clsx } from 'clsx';

const Sidebar = () => {
    const currentStep = useReportStore((state) => state.currentStep);
    const cliente = useReportStore((state) => state.cliente);
    const sucursal = useReportStore((state) => state.sucursal);

    const steps = [
        { id: 'select-client', label: 'Cliente', icon: Building2 },
        { id: 'upload', label: 'Cargar Informes', icon: Upload },
        { id: 'review', label: 'Revisión y Datos', icon: AlertCircle },
        { id: 'voladores', label: 'Voladores (UV)', icon: PieChart },
        { id: 'summaries', label: 'Resúmenes', icon: FileText },
        { id: 'preview', label: 'Generar Informe', icon: CheckCircle },
    ];

    return (
        <aside className="w-64 bg-primary-900 text-primary-50 flex flex-col h-screen fixed">
            {/* Header Sidebar */}
            <div className="p-6 border-b border-primary-800">
                <h1 className="text-xl font-bold flex items-center gap-2">
                    Sanitas <span className="text-sanitas font-light">MIP</span>
                </h1>
                <p className="text-primary-400 text-xs mt-1">Generador de Informes</p>
            </div>

            {/* Info Cliente */}
            {cliente && (
                <div className="px-6 py-4 border-b border-primary-800 bg-primary-800/50">
                    <p className="text-xs text-primary-400 uppercase font-semibold mb-1">Cliente</p>
                    <p className="font-medium truncate">{cliente.nombre}</p>
                    {sucursal && <p className="text-sm text-primary-300 truncate">{sucursal.nombre}</p>}
                </div>
            )}

            {/* Navegación (Steps) */}
            <nav className="flex-1 overflow-y-auto py-4 px-3 space-y-1">
                {steps.map((step) => {
                    const isActive = currentStep === step.id;
                    const Icon = step.icon;

                    return (
                        <div
                            key={step.id}
                            className={clsx(
                                "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors",
                                isActive
                                    ? "bg-primary-800 text-white shadow-sm ring-1 ring-primary-700"
                                    : "text-primary-300 pointer-events-none opacity-50"
                                // Nota: pointer-events-none deshabilita navegación manual por ahora para forzar flujo lineal
                            )}
                        >
                            <Icon size={18} className={isActive ? "text-sanitas" : ""} />
                            {step.label}
                        </div>
                    );
                })}
            </nav>

            {/* Footer Sidebar */}
            <div className="p-4 border-t border-primary-800 text-xs text-primary-400">
                <button className="flex items-center gap-2 hover:text-white transition-colors w-full p-2 rounded hover:bg-primary-800">
                    <Settings size={14} /> Configuración
                </button>
                <div className="mt-4 text-center opacity-50">v1.0.0</div>
            </div>
        </aside>
    );
};

export default Sidebar;
