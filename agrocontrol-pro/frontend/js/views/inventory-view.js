(() => {
  function escapar(valor) {
    return String(valor ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  function formatoPrecio(valor) {
    return "$" + Number(valor || 0).toLocaleString("es-CO", { maximumFractionDigits: 0 });
  }

  window.renderProductRows = (products) => products.map((product) => `
    <tr>
      <td>${escapar(product.codigo)}</td>
      <td>${escapar(product.nombre)}</td>
      <td>${escapar(product.categoria || "—")}</td>
      <td>${escapar(product.stock_actual)} ${escapar(product.unidad_medida)}</td>
      <td>${escapar(product.stock_minimo)}</td>
      <td>${formatoPrecio(product.precio_unitario)}</td>
      <td><span class="badge ${product.en_stock_critico ? "critico" : "ok"}">
        ${product.en_stock_critico ? "Crítico" : "Normal"}
      </span></td>
      <td><div class="table-actions">
        <button class="btn-tabla" type="button" onclick="editarProducto(${Number(product.id)})">Editar</button>
        <button class="btn-tabla danger" type="button" onclick="borrarProducto(${Number(product.id)})">Borrar</button>
      </div></td>
    </tr>
  `).join("");
})();