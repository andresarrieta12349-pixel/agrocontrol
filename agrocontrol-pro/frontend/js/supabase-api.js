/* ==========================================================================
   supabase-api.js
   Reemplaza al backend FastAPI: traduce las llamadas apiFetch("/api/...")
   que hace la app en consultas a Supabase. Las pantallas no cambian.
   Debe cargarse DESPUÉS de supabase-js y config.js, y ANTES del script
   principal de index.html.
   ========================================================================== */
(() => {
  "use strict";

  if (!window.supabase || !window.SUPABASE_URL || !window.SUPABASE_KEY) {
    console.error("[AgroControl] Falta supabase-js o config.js");
    return;
  }

  /* ----------------------------------------------------------------------
     1. Cliente de Supabase y sesión
     ---------------------------------------------------------------------- */
  // Si Google (o el correo de recuperación) nos devuelve a la página con los
  // tokens en la URL (#access_token=...), los leemos ahora mismo.
  const hashParams = new URLSearchParams(location.hash.replace(/^#/, ""));
  const tokenHash = hashParams.get("access_token");
  const refreshHash = hashParams.get("refresh_token");
  const esRecuperacion = hashParams.get("type") === "recovery";

  // Si viene del correo de recuperar contraseña, limpiamos la URL de inmediato
  // para que el script principal NO lo trate como un inicio de sesión normal.
  if (esRecuperacion) {
    history.replaceState(null, "", location.pathname + location.search);
  }

  const db = window.supabase.createClient(window.SUPABASE_URL, window.SUPABASE_KEY, {
    auth: { persistSession: true, autoRefreshToken: true, detectSessionInUrl: false }
  });
  window.supabaseClient = db;

  const sesionLista = (async () => {
    try {
      if (tokenHash && refreshHash) {
        await db.auth.setSession({ access_token: tokenHash, refresh_token: refreshHash });
      }
    } catch (e) {
      console.error("[AgroControl] No se pudo restaurar la sesión:", e);
    }
    const { data } = await db.auth.getSession();
    return data.session;
  })();

  async function cargarPerfil(session) {
    const user = session.user;
    let perfil = null;
    // El perfil lo crea un trigger al registrarse; damos un par de reintentos por si tarda.
    for (let i = 0; i < 3 && !perfil; i++) {
      const { data } = await db.from("perfiles").select("*").eq("id", user.id).maybeSingle();
      perfil = data;
      if (!perfil) await new Promise((r) => setTimeout(r, 400));
    }
    const meta = user.user_metadata || {};
    return {
      id: user.id,
      correo: user.email,
      nombre_completo: (perfil && perfil.nombre_completo) || meta.full_name || meta.name || user.email,
      nombre_usuario: meta.username || (user.email || "").split("@")[0],
      rol: (perfil && perfil.rol) || "operador"
    };
  }

  window.loginConGoogle = async function () {
    const { error } = await db.auth.signInWithOAuth({
      provider: "google",
      options: { redirectTo: location.origin + "/" }
    });
    if (error) {
      const caja = document.getElementById("error-login");
      if (caja) {
        caja.textContent = "No se pudo iniciar sesión con Google: " + error.message;
        caja.style.display = "block";
      }
    }
  };

  /* ----------------------------------------------------------------------
     2. Utilidades
     ---------------------------------------------------------------------- */
  function convertirError(error) {
    const msg = (error && error.message) || "";
    if (/Failed to fetch|NetworkError|Load failed/i.test(msg)) return new Error("ERR_NETWORK_DISCONNECTED");
    if (error.code === "23505") return new Error("Ya existe un registro con ese valor (código, NIT, arete o nombre repetido).");
    if (error.code === "23503") return new Error("No se puede completar: el registro está relacionado con otros datos.");
    if (error.code === "PGRST301" || /JWT/i.test(msg)) {
      if (window.cerrarSesion) window.cerrarSesion();
      return new Error("Sesión expirada");
    }
    return new Error(msg || "Error en la solicitud");
  }

  function limpiar(cuerpo) {
    const salida = {};
    Object.keys(cuerpo || {}).forEach((k) => {
      if (["id", "user_id", "creado_en"].includes(k)) return;
      if (cuerpo[k] !== undefined) salida[k] = cuerpo[k];
    });
    return salida;
  }

  const conStockCritico = (p) => Object.assign({}, p, {
    en_stock_critico: Number(p.stock_actual) <= Number(p.stock_minimo)
  });

  const aISO = (d) => d.toLocaleDateString("en-CA"); // YYYY-MM-DD en hora local

  function fechaDesdePeriodo(periodo) {
    const hoy = new Date();
    if (periodo === "mes") return aISO(new Date(hoy.getFullYear(), hoy.getMonth(), 1));
    if (periodo === "trimestre") { const d = new Date(hoy); d.setDate(d.getDate() - 90); return aISO(d); }
    if (periodo === "anio") return aISO(new Date(hoy.getFullYear(), 0, 1));
    return null; // "todo"
  }

  function lunesDeSemana(fecha) {
    const x = new Date(fecha);
    x.setHours(0, 0, 0, 0);
    x.setDate(x.getDate() - ((x.getDay() + 6) % 7));
    return x;
  }

  /* ----------------------------------------------------------------------
     3. Recursos CRUD (ruta de la API vieja -> tabla de Supabase)
     ---------------------------------------------------------------------- */
  const RECURSOS = {
    "admin/fincas":          { t: "fincas",              orden: ["nombre"] },
    "admin/lotes":           { t: "lotes",               orden: ["nombre"] },
    "admin/proveedores":     { t: "proveedores",         orden: ["nombre"] },
    "admin/potreros":        { t: "potreros",            orden: ["nombre"] },
    "admin/animales":        { t: "animales",            orden: ["arete"] },
    "admin/pastos":          { t: "pastos",              orden: ["nombre"] },
    "inventario/bodegas":    { t: "bodegas",             orden: ["nombre"], blando: true },
    "inventario/productos":  { t: "productos",           orden: ["nombre"], blando: true, soloActivos: true },
    "produccion/ciclos":     { t: "ciclos_productivos",  orden: ["fecha_inicio", false] },
    "produccion/actividades":{ t: "actividades_diarias", orden: ["fecha", false] },
    "produccion/cosechas":   { t: "cosechas",            orden: ["fecha", false] },
    "gastos":                { t: "gastos",              orden: ["fecha", false] }
  };

  async function validarFincaActiva(fincaId) {
    if (!fincaId) throw new Error("Debes registrar y seleccionar una finca activa antes de crear una bodega.");
    const { data, error } = await db.from("fincas").select("id").eq("id", fincaId).eq("activo", true).maybeSingle();
    if (error) throw convertirError(error);
    if (!data) throw new Error("La finca indicada no existe o está inactiva.");
  }

  async function crud(r, metodo, id, cuerpo, q) {
    const T = db.from(r.t);

    if (metodo === "GET") {
      let c = T.select("*");
      if (r.soloActivos) c = c.eq("activo", true);
      if (r.t === "bodegas" && q.get("incluir_inactivas") === "false") c = c.eq("activo", true);
      if (r.t === "gastos") {
        const desde = fechaDesdePeriodo(q.get("periodo"));
        if (desde) c = c.gte("fecha", desde);
      }
      c = c.order(r.orden[0], { ascending: r.orden[1] !== false });
      if (r.t === "gastos") c = c.order("id", { ascending: false });
      if (q.get("limite")) c = c.limit(Number(q.get("limite")));
      const { data, error } = await c;
      if (error) throw convertirError(error);
      if (r.t !== "productos") return data;
      const productos = data.map(conStockCritico);
      return q.get("stock_critico") === "true" ? productos.filter((p) => p.en_stock_critico) : productos;
    }

    if (metodo === "POST") {
      if (r.t === "bodegas") await validarFincaActiva(cuerpo.finca_id);
      const { data, error } = await T.insert(limpiar(cuerpo)).select().single();
      if (error) {
        if (error.code === "23505" && r.t === "productos") throw new Error("Ya existe un producto con ese código");
        throw convertirError(error);
      }
      return r.t === "productos" ? conStockCritico(data) : data;
    }

    if (metodo === "PUT") {
      if (r.t === "bodegas" && cuerpo.finca_id != null) await validarFincaActiva(cuerpo.finca_id);
      const { data, error } = await T.update(limpiar(cuerpo)).eq("id", id).select().single();
      if (error) throw convertirError(error);
      return r.t === "productos" ? conStockCritico(data) : data;
    }

    if (metodo === "DELETE") {
      const { error } = r.blando
        ? await T.update({ activo: false }).eq("id", id)
        : await T.delete().eq("id", id);
      if (error) throw convertirError(error);
      return null;
    }

    throw new Error("Operación no soportada");
  }

  /* ----------------------------------------------------------------------
     4. Movimientos de kardex (usa la función SQL registrar_movimiento)
     ---------------------------------------------------------------------- */
  async function movimientos(metodo, cuerpo, q) {
    if (metodo === "GET") {
      let c = db.from("movimientos_inventario").select("*").order("fecha", { ascending: false }).limit(200);
      if (q.get("producto_id")) c = c.eq("producto_id", q.get("producto_id"));
      if (q.get("bodega_id")) c = c.eq("bodega_id", q.get("bodega_id"));
      const { data, error } = await c;
      if (error) throw convertirError(error);
      return data;
    }
    const { data, error } = await db.rpc("registrar_movimiento", {
      p_producto_id: cuerpo.producto_id,
      p_bodega_id: cuerpo.bodega_id,
      p_tipo: cuerpo.tipo,
      p_cantidad: cuerpo.cantidad,
      p_costo_unitario: cuerpo.costo_unitario ?? 0,
      p_referencia: cuerpo.referencia ?? null,
      p_observaciones: cuerpo.observaciones ?? null
    });
    if (error) throw convertirError(error);
    return data;
  }

  /* ----------------------------------------------------------------------
     5. Resumen del dashboard (antes lo calculaba dashboard.py)
     ---------------------------------------------------------------------- */
  async function resumenDashboard(periodo) {
    const desde = fechaDesdePeriodo(periodo);
    const inicioSemanas = lunesDeSemana(new Date());
    inicioSemanas.setDate(inicioSemanas.getDate() - 5 * 7);

    let consultaGastos = db.from("gastos").select("categoria,monto");
    if (desde) consultaGastos = consultaGastos.gte("fecha", desde);

    const [ciclos, alertasCrit, productos, alertasRec, gastos, movs] = await Promise.all([
      db.from("ciclos_productivos").select("id", { count: "exact", head: true }).eq("estado", "activo"),
      db.from("alertas").select("id", { count: "exact", head: true }).eq("severidad", "critica").eq("resuelta", false),
      db.from("productos").select("stock_actual,stock_minimo,precio_unitario").eq("activo", true),
      db.from("alertas").select("titulo,mensaje,severidad").eq("resuelta", false).order("creado_en", { ascending: false }).limit(5),
      consultaGastos,
      db.from("movimientos_inventario").select("tipo,cantidad,fecha").gte("fecha", inicioSemanas.toISOString())
    ]);
    [ciclos, alertasCrit, productos, alertasRec, gastos, movs].forEach((res) => {
      if (res.error) throw convertirError(res.error);
    });

    const gastosPorCategoria = {};
    gastos.data.forEach((g) => {
      gastosPorCategoria[g.categoria] = (gastosPorCategoria[g.categoria] || 0) + Number(g.monto || 0);
    });

    const semanas = [];
    for (let i = 0; i < 6; i++) {
      const d = new Date(inicioSemanas);
      d.setDate(d.getDate() + i * 7);
      semanas.push({ semana: d.toLocaleDateString("es-CO", { day: "numeric", month: "short" }), entradas: 0, salidas: 0 });
    }
    movs.data.forEach((m) => {
      const idx = Math.round((lunesDeSemana(new Date(m.fecha)) - inicioSemanas) / (7 * 86400000));
      if (idx < 0 || idx > 5) return;
      if (m.tipo === "entrada") semanas[idx].entradas += Number(m.cantidad);
      if (m.tipo === "salida") semanas[idx].salidas += Number(m.cantidad);
    });
    const hayMovimientos = semanas.some((s) => s.entradas || s.salidas);

    return {
      ciclos_activos: ciclos.count || 0,
      alertas_criticas: alertasCrit.count || 0,
      productos_stock_critico: productos.data.filter((p) => Number(p.stock_actual) <= Number(p.stock_minimo)).length,
      valor_inventario: productos.data.reduce((s, p) => s + Number(p.stock_actual) * Number(p.precio_unitario), 0),
      alertas_recientes: alertasRec.data,
      gastos_por_categoria: gastosPorCategoria,
      movimientos_kardex_semanal: hayMovimientos ? semanas : []
    };
  }

  /* ----------------------------------------------------------------------
     6. Autenticación con correo y contraseña
     ---------------------------------------------------------------------- */
  async function rutaAuth(ruta, cuerpo) {
    if (ruta === "/api/auth/register") {
      const { data, error } = await db.auth.signUp({
        email: cuerpo.correo,
        password: cuerpo.password,
        options: {
          data: { full_name: cuerpo.nombre_completo, username: cuerpo.nombre_usuario },
          emailRedirectTo: location.origin + "/"
        }
      });
      if (error) throw convertirError(error);
      if (!data.session) {
        throw new Error("Te enviamos un correo para confirmar tu cuenta. Confírmalo y luego inicia sesión.");
      }
      return { id: data.user.id };
    }

    if (ruta === "/api/auth/login") {
      const { data, error } = await db.auth.signInWithPassword({ email: cuerpo.identificador, password: cuerpo.password });
      if (error) {
        if (/Invalid login credentials/i.test(error.message)) throw new Error("Correo o contraseña incorrectos.");
        if (/Email not confirmed/i.test(error.message)) throw new Error("Primero confirma tu correo (te enviamos un enlace).");
        throw convertirError(error);
      }
      return { access_token: data.session.access_token, usuario: await cargarPerfil(data.session) };
    }

    if (ruta === "/api/auth/me") {
      const sesion = await sesionLista;
      if (!sesion) throw new Error("Sin sesión");
      return cargarPerfil(sesion);
    }

    throw new Error("Ruta de autenticación no soportada");
  }

  // Formulario "Iniciar sesión con correo" (agregado al HTML por aplicar_cambios.py)
  document.getElementById("form-login-correo")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const caja = document.getElementById("error-login");
    caja.style.display = "none";
    const boton = e.target.querySelector("button[type=submit]");
    cambiarEstadoCarga(boton, true, "Ingresando...");
    try {
      const datos = await window.apiFetch("/api/auth/login", {
        method: "POST",
        body: JSON.stringify({
          identificador: document.getElementById("login-correo").value.trim().toLowerCase(),
          password: document.getElementById("login-password").value
        })
      });
      TOKEN = datos.access_token;
      USUARIO = datos.usuario;
      localStorage.setItem("agrocontrol_token", TOKEN);
      localStorage.setItem("agrocontrol_usuario", JSON.stringify(USUARIO));
      e.target.reset();
      iniciarApp();
    } catch (err) {
      caja.textContent = err.message || "No se pudo iniciar sesión.";
      caja.style.display = "block";
    } finally {
      cambiarEstadoCarga(boton, false, "Iniciar sesión");
    }
  });

  /* ----------------------------------------------------------------------
     7. apiFetch: punto de entrada que usa toda la app
     ---------------------------------------------------------------------- */
  async function enrutar(path, opciones) {
    const url = new URL(path, "http://local");
    const ruta = url.pathname;
    const q = url.searchParams;
    const metodo = (opciones.method || "GET").toUpperCase();
    const cuerpo = opciones.body ? JSON.parse(opciones.body) : null;

    if (ruta.startsWith("/api/auth/")) return rutaAuth(ruta, cuerpo || {});

    const { data: { session } } = await db.auth.getSession();
    if (!session) {
      if (window.cerrarSesion) window.cerrarSesion();
      throw new Error("Sesión expirada");
    }

    if (ruta === "/api/dashboard/resumen") return resumenDashboard(q.get("periodo") || "mes");
    if (ruta === "/api/inventario/movimientos") return movimientos(metodo, cuerpo, q);

    const m = ruta.match(/^\/api\/(.+?)(?:\/(\d+))?$/);
    const recurso = m && RECURSOS[m[1]];
    if (!recurso) throw new Error("Ruta no soportada: " + ruta);
    return crud(recurso, metodo, m[2] ? Number(m[2]) : null, cuerpo, q);
  }

  window.apiFetch = async function (path, opciones = {}) {
    try {
      return await enrutar(path, opciones);
    } catch (err) {
      if (err instanceof TypeError || /Failed to fetch/i.test(err.message || "")) {
        throw new Error("ERR_NETWORK_DISCONNECTED");
      }
      throw err;
    }
  };

  /* ----------------------------------------------------------------------
     8. Reportes (Excel y PDF generados en el navegador)
     ---------------------------------------------------------------------- */
  async function datosReporte(tipo, q) {
    if (tipo === "inventario") {
      const { data, error } = await db.from("productos")
        .select("codigo,nombre,categoria,unidad_medida,stock_actual,stock_minimo,precio_unitario")
        .eq("activo", true).order("nombre");
      if (error) throw convertirError(error);
      return {
        titulo: "Inventario actual",
        columnas: ["Código", "Nombre", "Categoría", "Unidad", "Stock actual", "Stock mínimo", "Precio unitario", "Valor total", "Estado"],
        filas: data.map((p) => [p.codigo, p.nombre, p.categoria || "", p.unidad_medida, p.stock_actual, p.stock_minimo,
          p.precio_unitario, p.stock_actual * p.precio_unitario, p.stock_actual <= p.stock_minimo ? "Crítico" : "OK"])
      };
    }

    if (tipo === "kardex") {
      let c = db.from("movimientos_inventario")
        .select("fecha,tipo,cantidad,referencia,productos(codigo,nombre),bodegas(nombre,finca_id)")
        .order("fecha", { ascending: false });
      if (q.get("desde")) c = c.gte("fecha", q.get("desde") + "T00:00:00");
      if (q.get("hasta")) c = c.lte("fecha", q.get("hasta") + "T23:59:59");
      const { data, error } = await c;
      if (error) throw convertirError(error);
      const finca = q.get("finca_id");
      const filas = finca ? data.filter((m) => String(m.bodegas && m.bodegas.finca_id) === finca) : data;
      return {
        titulo: "Kardex de movimientos",
        columnas: ["Fecha", "Tipo", "Código", "Producto", "Bodega", "Cantidad", "Referencia"],
        filas: filas.map((m) => [new Date(m.fecha).toLocaleString("es-CO"), m.tipo, m.productos ? m.productos.codigo : "",
          m.productos ? m.productos.nombre : "", m.bodegas ? m.bodegas.nombre : "", m.cantidad, m.referencia || ""])
      };
    }

    let c = db.from("cosechas")
      .select("fecha,cantidad_kg,calidad,observaciones,ciclo_id,ciclos_productivos(nombre,cultivo,lotes(finca_id))")
      .order("fecha", { ascending: false });
    if (q.get("ciclo_id")) c = c.eq("ciclo_id", q.get("ciclo_id"));
    const { data, error } = await c;
    if (error) throw convertirError(error);
    const finca = q.get("finca_id");
    const filas = finca
      ? data.filter((x) => String(x.ciclos_productivos && x.ciclos_productivos.lotes && x.ciclos_productivos.lotes.finca_id) === finca)
      : data;
    return {
      titulo: "Cosechas",
      columnas: ["Fecha", "Ciclo", "Cultivo", "Cantidad (kg)", "Calidad", "Observaciones"],
      filas: filas.map((x) => [x.fecha, x.ciclos_productivos ? x.ciclos_productivos.nombre : "",
        x.ciclos_productivos ? x.ciclos_productivos.cultivo : "", x.cantidad_kg, x.calidad || "", x.observaciones || ""])
    };
  }

  window.descargarReporte = async function (ruta, nombreArchivo) {
    try {
      mostrarToast("Generando reporte...");
      const url = new URL(ruta, "http://local");
      const m = url.pathname.match(/^\/api\/reportes\/(inventario|kardex|cosechas)\/(excel|pdf)$/);
      if (!m) throw new Error("Reporte no soportado");
      const { titulo, columnas, filas } = await datosReporte(m[1], url.searchParams);

      if (m[2] === "excel") {
        if (!window.XLSX) throw new Error("No se cargó la librería de Excel (revisa tu conexión).");
        const hoja = window.XLSX.utils.aoa_to_sheet([columnas].concat(filas));
        const libro = window.XLSX.utils.book_new();
        window.XLSX.utils.book_append_sheet(libro, hoja, "Reporte");
        window.XLSX.writeFile(libro, nombreArchivo);
      } else {
        if (!window.jspdf) throw new Error("No se cargó la librería de PDF (revisa tu conexión).");
        const doc = new window.jspdf.jsPDF({ orientation: "landscape" });
        doc.setFontSize(14);
        doc.text("AgroControl Pro - " + titulo, 14, 15);
        doc.autoTable({ head: [columnas], body: filas, startY: 22, styles: { fontSize: 8 } });
        doc.save(nombreArchivo);
      }
      mostrarToast("Reporte descargado correctamente");
    } catch (err) {
      mostrarToast(err.message, true);
    }
  };

  /* ----------------------------------------------------------------------
     9. Recuperar contraseña
     ---------------------------------------------------------------------- */
  document.getElementById("olvide-password")?.addEventListener("click", async () => {
    const caja = document.getElementById("error-login");
    const correo = document.getElementById("login-correo").value.trim().toLowerCase();
    caja.style.display = "block";
    if (!correo) {
      caja.textContent = "Escribe tu correo arriba y vuelve a hacer clic aquí.";
      return;
    }
    const { error } = await db.auth.resetPasswordForEmail(correo, { redirectTo: location.origin + "/" });
    caja.textContent = error
      ? "No se pudo enviar el correo: " + error.message
      : "Si el correo existe, te enviamos un enlace para crear una nueva contraseña.";
  });

  // Cuando la persona vuelve desde el correo, mostramos el formulario de nueva contraseña
  if (esRecuperacion) {
    sesionLista.then(() => {
      document.getElementById("modal-contenido").innerHTML = `
        <h3>Crea tu nueva contraseña</h3>
        <form id="form-nueva-password" autocomplete="off">
          <div class="campo"><label>Nueva contraseña</label>
            <input type="password" id="nueva-password" minlength="8" required /></div>
          <div class="campo"><label>Confirmar contraseña</label>
            <input type="password" id="nueva-password2" minlength="8" required /></div>
          <div class="modal-acciones">
            <button type="submit" class="btn-primario">Guardar contraseña</button>
          </div>
        </form>`;
      document.getElementById("modal-fondo").classList.add("activo");
      document.getElementById("form-nueva-password").addEventListener("submit", async (e) => {
        e.preventDefault();
        const p1 = document.getElementById("nueva-password").value;
        const p2 = document.getElementById("nueva-password2").value;
        if (p1 !== p2) return mostrarToast("Las contraseñas no coinciden.", true);
        if (!esPasswordSegura(p1)) return mostrarToast("Usa 8+ caracteres con mayúscula, minúscula y número.", true);
        const { error } = await db.auth.updateUser({ password: p1 });
        if (error) return mostrarToast(error.message, true);
        await db.auth.signOut();
        cerrarModal();
        mostrarToast("Contraseña cambiada. Ya puedes iniciar sesión.");
      });
    });
  }
})();