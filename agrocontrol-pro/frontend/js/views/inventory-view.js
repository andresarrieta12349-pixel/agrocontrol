(() => {
  function formatoPrecio(valor) {
    return "$" + Number(valor || 0).toLocaleString("es-CO", { maximumFractionDigits: 0 });
  }

  window.renderProductRows = (products) => products.map((product) => `
    <tr>
      <td>${product.codigo}</td>
      <td>${product.nombre}</td>
      <td>${product.categoria || "—"}</td>
      <td>${product.stock_actual} ${product.unidad_medida}</td>
      <td>${product.stock_minimo}</td>
      <td>${formatoPrecio(product.precio_unitario)}</td>
      <td><span class="badge ${product.en_stock_critico ? "critico" : "ok"}">
        ${product.en_stock_critico ? "Crítico" : "Normal"}
      </span></td>
      <td><div class="table-actions">
        <button class="btn-tabla" type="button" onclick="editarProducto(${product.id})">Editar</button>
        <button class="btn-tabla danger" type="button" onclick="borrarProducto(${product.id})">Borrar</button>
      </div></td>
    </tr>
  `).join("");
})();