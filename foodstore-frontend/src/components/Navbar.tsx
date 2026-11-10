interface NavbarProps {
  onNuevoProducto: () => void;
}

export function Navbar({ onNuevoProducto }: NavbarProps) {
  return (
    <header className="bg-slate-900 border-b border-slate-800 sticky top-0 z-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-9 h-9 bg-emerald-500 rounded-lg flex items-center justify-center font-bold text-slate-950 text-xl shadow-lg shadow-emerald-500/20">
            FS
          </div>
          <div>
            <h1 className="text-lg font-bold text-white leading-tight">Food Store</h1>
            <p className="text-xs text-slate-400">Administración de Catálogo</p>
          </div>
        </div>
        <button
          type="button"
          onClick={onNuevoProducto}
          className="inline-flex items-center gap-2 px-4 py-2 bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-semibold rounded-lg text-sm transition-colors shadow-md cursor-pointer"
        >
          <span className="text-base font-bold">+</span>
          Nuevo Producto
        </button>
      </div>
    </header>
  );
}
