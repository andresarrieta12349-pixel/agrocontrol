(() => {
  window.editarProducto = (productId) => {
    const product = window.obtenerProducto(productId);
    if (product) window.abrirModal("producto", product);
  };

  window.borrarProducto = async (productId) => {
    const product = window.obtenerProducto(productId);
    if (!product || !window.confirm(`¿Borrar el producto "${product.nombre}"?`)) return;

    try {
      await window.apiFetch(`/api/inventario/productos/${productId}`, { method: "DELETE" });
      window.eliminarProductoDeTabla(productId);
      window.mostrarToast("Producto borrado correctamente");
    } catch (error) {
      window.mostrarToast(error.message, true);
    }
  };
})();
