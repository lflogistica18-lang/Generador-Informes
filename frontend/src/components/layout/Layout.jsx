import React from 'react';
import Sidebar from './Sidebar';

const Layout = ({ children }) => {
    return (
        <div className="flex h-screen bg-primary-50 font-sans">
            <Sidebar />
            <main className="ml-64 flex-1 flex flex-col h-screen overflow-hidden">
                {/* Header Superior (opcional, para breadcrumbs o usuario) */}
                <header className="bg-white border-b border-primary-200 h-16 flex items-center justify-between px-8 shrink-0">
                    <div className="flex items-center gap-4">
                        {/* Breadcrumbsplaceholder */}
                    </div>
                    <div className="text-sm text-primary-600">
                        Usuario: <span className="font-medium text-primary-900">Sanitas Admin</span>
                    </div>
                </header>

                {/* Contenido Principal con Scroll */}
                <div className="flex-1 overflow-y-auto p-8 relative">
                    <div className="max-w-6xl mx-auto pb-12">
                        {children}
                    </div>
                </div>
            </main>
        </div>
    );
};

export default Layout;
