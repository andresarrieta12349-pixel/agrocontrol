"""
aplicar_cambios.py
Conecta frontend/index.html con Supabase haciendo 7 cambios pequeños.
Antes de tocar nada guarda una copia en frontend/index.html.bak

Uso (desde la carpeta agrocontrol-pro):
    python aplicar_cambios.py
"""
import pathlib
import shutil
import sys

ruta = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "frontend/index.html")
if not ruta.exists():
    sys.exit(f"No encuentro {ruta}. Ejecuta este script desde la carpeta agrocontrol-pro.")

texto = ruta.read_text(encoding="utf-8").replace("\r\n", "\n")

if "supabase-api.js" in texto:
    sys.exit("Los cambios ya estaban aplicados. No hice nada.")

FORM_LOGIN = """<form id="form-login-correo" class="form-login-dark" style="margin-top:14px;">
            <div style="text-align:center;opacity:.7;font-size:13px;margin:4px 0 10px;">o con tu correo</div>
            <div class="campo"><input id="login-correo" class="campo-input-dark" type="email" placeholder="Correo electrónico" autocomplete="email" required /></div>
            <div class="campo"><input id="login-password" class="campo-input-dark" type="password" placeholder="Contraseña" autocomplete="current-password" required /></div>
            <button type="submit" class="btn-continuar-blanco">Iniciar sesión</button>
          </form>
          <div class="error-login" id="error-login"></div>"""

SCRIPTS = """<script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf-autotable/3.8.2/jspdf.plugin.autotable.min.js"></script>
<script src="/js/config.js"></script>
<script src="/js/supabase-api.js"></script>
<script src="/js/theme.js"></script>"""

CAMBIOS = [
    ("scripts de Supabase",
     '<script src="/js/theme.js"></script>',
     SCRIPTS),
    ("apiFetch viejo (queda sin uso)",
     "async function apiFetch(path, opciones={}){",
     "async function apiFetchViejo(path, opciones={}){"),
    ("botón de Google",
     '  window.location.href = API_BASE + "/api/auth/google/login";',
     "  window.loginConGoogle();"),
    ("cerrar sesión",
     "  TOKEN = null; USUARIO = null;",
     "  if (window.supabaseClient) window.supabaseClient.auth.signOut();\n  TOKEN = null; USUARIO = null;"),
    ("formulario de login con correo",
     '<div class="error-login" id="error-login"></div>',
     FORM_LOGIN),
    ("descargarReporte viejo (queda sin uso)",
     "async function descargarReporte(ruta, nombreArchivo){",
     "async function descargarReporteViejo(ruta, nombreArchivo){"),
]

# Verifica que cada texto exista exactamente una vez ANTES de modificar nada
for nombre, viejo, _ in CAMBIOS:
    veces = texto.count(viejo)
    if veces != 1:
        sys.exit(f"No pude aplicar '{nombre}': encontré {veces} coincidencias (debía ser 1). No se modificó nada.")

shutil.copyfile(ruta, str(ruta) + ".bak")
for nombre, viejo, nuevo in CAMBIOS:
    texto = texto.replace(viejo, nuevo)
    print(f"OK  {nombre}")

ruta.write_text(texto, encoding="utf-8")
print(f"\nListo. Copia de seguridad en {ruta}.bak")