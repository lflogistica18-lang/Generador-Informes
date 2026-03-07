import React, { useState, useRef } from 'react';
import { useReportStore } from '../store/useReportStore';
import { Upload, X, FileText, CheckCircle, AlertTriangle, Loader2 } from 'lucide-react';
import api from '../services/api';

const UploadPage = () => {
    const setStep = useReportStore((state) => state.setStep);
    const setUploadResult = useReportStore((state) => state.setUploadResult);
    const setIsUploading = useReportStore((state) => state.setIsUploading);
    const isUploading = useReportStore((state) => state.isUploading);
    const uploadResult = useReportStore((state) => state.uploadResult);

    const [files, setFiles] = useState([]);
    const [errorLocal, setErrorLocal] = useState('');
    const fileInputRef = useRef(null);

    const handleFileChange = (e) => {
        const selectedFiles = Array.from(e.target.files);
        // Filtrar solo PDFs
        const validFiles = selectedFiles.filter(f => f.type === 'application/pdf');
        if (validFiles.length !== selectedFiles.length) {
            setErrorLocal('Algunos archivos no son PDF y fueron ignorados.');
        }
        setFiles(prev => [...prev, ...validFiles]);
    };

    const removeFile = (index) => {
        setFiles(prev => prev.filter((_, i) => i !== index));
    };

    const handleUpload = async () => {
        if (files.length === 0) return;

        setIsUploading(true);
        setErrorLocal('');

        const formData = new FormData();
        files.forEach(file => {
            formData.append('files', file);
        });

        try {
            // Usar api de services configurado con baseURL dinámico
            const response = await api.post('upload/', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });


            setUploadResult(response.data);
            // Avanzar al siguiente paso si todo salió bien
            if (response.data.archivos_procesados > 0) {
                setStep('review');
            } else {
                setErrorLocal('No se procesaron archivos válidos.');
            }
        } catch (err) {
            console.error(err);
            setErrorLocal('Ocurrió un error al subir los archivos. Verifica que el backend esté corriendo.');
        } finally {
            setIsUploading(false);
        }
    };

    return (
        <div className="max-w-4xl mx-auto mt-8">
            <div className="mb-6">
                <h2 className="text-2xl font-bold text-primary-900">Cargar Informes PDF</h2>
                <p className="text-primary-600">Sube los informes de visita (Conformes) y registros MIP del mes.</p>
            </div>

            <div
                className="border-2 border-dashed border-primary-300 rounded-lg p-10 text-center hover:bg-primary-50 transition-colors cursor-pointer"
                onClick={() => fileInputRef.current?.click()}
            >
                <input
                    type="file"
                    multiple
                    accept=".pdf"
                    className="hidden"
                    ref={fileInputRef}
                    onChange={handleFileChange}
                />
                <div className="text-primary-400 mb-4 inline-block p-4 bg-primary-50 rounded-full">
                    <Upload size={48} />
                </div>
                <p className="text-lg font-medium text-primary-700">Haz clic para seleccionar o arrastra tus archivos aquí</p>
                <p className="text-sm text-primary-400 mt-2">Solo archivos PDF (.pdf)</p>
            </div>

            {errorLocal && (
                <div className="mt-4 p-3 bg-red-50 text-red-700 rounded-md flex items-center gap-2">
                    <AlertTriangle size={18} />
                    {errorLocal}
                </div>
            )}

            {files.length > 0 && (
                <div className="mt-8">
                    <h3 className="text-lg font-semibold text-primary-800 mb-3">Archivos seleccionados ({files.length})</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                        {files.map((file, idx) => (
                            <div key={idx} className="flex items-center justify-between p-3 bg-white border border-primary-200 rounded-md shadow-sm">
                                <div className="flex items-center gap-3 overflow-hidden">
                                    <FileText className="text-primary-500 shrink-0" size={20} />
                                    <span className="truncate text-sm font-medium text-primary-700">{file.name}</span>
                                </div>
                                <button
                                    onClick={(e) => { e.stopPropagation(); removeFile(idx); }}
                                    className="text-primary-400 hover:text-red-500 p-1"
                                >
                                    <X size={18} />
                                </button>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            <div className="mt-8 flex justify-end gap-4">
                <button
                    onClick={() => setStep('select-client')}
                    className="bg-gray-200 hover:bg-gray-300 text-gray-800 font-medium py-2 px-4 rounded"
                    disabled={isUploading}
                >
                    Atrás
                </button>
                <button
                    onClick={handleUpload}
                    className="bg-primary-600 hover:bg-primary-700 text-white font-medium py-2 px-4 rounded flex items-center gap-2"
                    disabled={files.length === 0 || isUploading}
                >
                    {isUploading ? <Loader2 className="animate-spin" size={20} /> : 'Procesar Archivos'}
                </button>
            </div>
        </div>
    );
};

export default UploadPage;
