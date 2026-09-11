(() => {
  function escapar(valor) {
    return String(valor ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  window.renderPotreros = (potreros, animales) => {
    const contenedor = document.getElementById("tarjetas-potreros");
    if (!potreros.length) {
      contenedor.innerHTML = '<div class="vacio">Sin potreros registrados.</div>';
      return;
    }

    contenedor.innerHTML = potreros.map((potrero) => {
      const asignados = animales.filter((animal) => animal.potrero_id === potrero.id).length;
      const porcentaje = potrero.capacidad_animales
        ? Math.min(100, Math.round((asignados / potrero.capacidad_animales) * 100))
        : 0;
      return `
        <article class="potrero-card">
          <div class="potrero-card__header">
            <div>
              <span class="potrero-card__eyebrow">Lote #${potrero.lote_id}</span>
              <h3>${escapar(potrero.nombre)}</h3>
            </div>
            <span class="badge ${porcentaje >= 100 ? "critico" : "ok"}">${asignados}/${potrero.capacidad_animales} animales</span>
          </div>
          <div class="potrero-card__meta">
            <span>🌾 ${escapar(potrero.tipo_pasto || "Pasto no definido")}</span>
            <span>Capacidad ${potrero.capacidad_animales}</span>
          </div>
          <div class="potrero-progress"><span style="width:${porcentaje}%"></span></div>
          <div class="table-actions">
            <button class="btn-tabla" type="button" onclick="editarPotrero(${potrero.id})">Editar</button>
            <button class="btn-tabla danger" type="button" onclick="borrarPotrero(${potrero.id})">Borrar</button>
          </div>
        </article>
      `;
    }).join("");
  };

  window.renderAnimales = (animales, potreros) => {
    const nombresPotreros = new Map(potreros.map((potrero) => [potrero.id, potrero.nombre]));
    const cuerpo = document.getElementById("tabla-animales");
    cuerpo.innerHTML = animales.map((animal) => `
      <tr>
        <td><strong>${escapar(animal.arete)}</strong></td>
        <td>${Number(animal.peso_kg).toLocaleString("es-CO")} kg</td>
        <td><span class="badge ${animal.estado_salud === "saludable" ? "ok" : "critico"}">${escapar(animal.estado_salud)}</span></td>
        <td>${escapar(nombresPotreros.get(animal.potrero_id) || `Potrero #${animal.potrero_id}`)}</td>
        <td><div class="table-actions">
          <button class="btn-tabla" type="button" onclick="editarAnimal(${animal.id})">Editar</button>
          <button class="btn-tabla danger" type="button" onclick="borrarAnimal(${animal.id})">Borrar</button>
        </div></td>
      </tr>
    `).join("") || '<tr><td colspan="5" class="vacio">Sin animales registrados.</td></tr>';
  };
})();
