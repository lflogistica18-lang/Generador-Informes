import { create } from 'zustand';

// Store para manejar el estado global de la app
// Mantiene: cliente seleccionado, PDFs procesados, datos consolidados, pasos del wizard.

export const useReportStore = create((set, get) => ({
    // ─── Estado del Flujo ───────────────────────────────────────────────────────
    currentStep: 'select-client', // select-client, upload, review, voladores, summaries, preview, print
    setStep: (step) => set({ currentStep: step }),

    // ─── Cliente y Configuración ────────────────────────────────────────────────
    cliente: null,
    sucursal: null,
    mes: new Date().toLocaleString('es-ES', { month: 'long' }),
    anio: new Date().getFullYear(),

    setCliente: (cliente) => set({ cliente }),
    setSucursal: (sucursal) => set({ sucursal }),
    setPeriodo: (mes, anio) => set({ mes, anio }),

    // ─── Archivos y Parseo ──────────────────────────────────────────────────────
    uploadResult: null, // { conformes: [], mips: [], errores: [], campos_faltantes: [] }
    isUploading: false,

    setUploadResult: (result) => set({ uploadResult: result }),
    setIsUploading: (status) => set({ isUploading: status }),

    updateConforme: (index, updates) => set((state) => {
        const nuevosConformes = [...state.uploadResult.conformes];
        nuevosConformes[index] = { ...nuevosConformes[index], ...updates };
        return { uploadResult: { ...state.uploadResult, conformes: nuevosConformes } };
    }),

    // ─── Informe Consolidado ────────────────────────────────────────────────────
    informeData: null, // Datos consolidados desde el backend
    isConsolidating: false,

    setInformeData: (data) => set({ informeData: data }),
    setIsConsolidating: (status) => set({ isConsolidating: status }),

    updateResumen: (campo, valor) => set((state) => ({
        informeData: { ...state.informeData, [campo]: valor }
    })),

    // ─── Acciones Derivadas ─────────────────────────────────────────────────────
    reset: () => set({
        currentStep: 'select-client',
        uploadResult: null,
        informeData: null,
        cliente: null,
        sucursal: null
    }),
}));
