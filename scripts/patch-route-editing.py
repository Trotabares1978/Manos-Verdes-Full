#!/usr/bin/env python3
"""Inject editable-stop controls into the web UI packaged inside Manos Verdes Full."""
from pathlib import Path
import sys

MARKER = "MANOS_VERDES_FULL_EDITABLE_ROUTE_STOPS_V1"

INJECTION = r"""
<script>
/* MANOS_VERDES_FULL_EDITABLE_ROUTE_STOPS_V1 */
(function () {
  "use strict";
  if (window.__mvFullEditableRoutesInstalled) return;
  window.__mvFullEditableRoutesInstalled = true;

  function activeRoute() {
    return (typeof routeTemplates !== "undefined" ? routeTemplates : []).find(r => String(r.id) === String(activeRouteId));
  }

  function invalidateOptimization(route) {
    route.optimizedOrderIds = [];
    route.optimizedAt = null;
  }

  // Route stops may be existing orders or custom address stops (custom-* IDs).
  if (typeof window.routeStopsForActiveRoute === "function") {
    const originalRouteStops = window.routeStopsForActiveRoute;
    window.routeStopsForActiveRoute = function () {
      const route = activeRoute();
      if (!route) return [];
      const pending = (typeof orders !== "undefined" ? orders : []).filter(o => !o.delivered);
      const pendingById = new Map(pending.map(o => [String(o.id), o]));
      const result = [];
      for (const stop of (route.stops || [])) {
        const id = String(stop.orderId ?? stop.customId ?? stop.id ?? "");
        const order = pendingById.get(id);
        if (order) {
          result.push({
            ...order,
            id: order.id,
            name: order.name || stop.name,
            address: order.address || stop.address,
            phone: order.phone || stop.phone || "",
            lat: order.lat ?? stop.lat ?? null,
            lng: order.lng ?? stop.lng ?? null,
            placeId: order.placeId || stop.placeId || ""
          });
        } else if (id.startsWith("custom-") && stop.address) {
          result.push({
            id,
            custom: true,
            name: stop.name || stop.address,
            address: stop.address,
            phone: stop.phone || "",
            lat: stop.lat ?? null,
            lng: stop.lng ?? null,
            placeId: stop.placeId || ""
          });
        }
      }
      return result;
    };
  }

  window.removeEditableRouteStop = function (id) {
    const route = activeRoute();
    if (!route) return;
    const key = String(id);
    const stop = (route.stops || []).find(s =>
      String(s.orderId ?? s.customId ?? s.id ?? "") === key
    );
    if (!stop) return;
    const label = stop.name || stop.address || "esta parada";
    if (!confirm("¿Quitar " + label + " de esta ruta?\\n\\nNo se eliminará el cliente ni el pedido de la aplicación; solo se quitará de esta ruta.")) return;
    const before = (route.stops || []).length;
    route.stops = (route.stops || []).filter(s =>
      String(s.orderId ?? s.customId ?? s.id ?? "") !== key
    );
    route.optimizedOrderIds = (route.optimizedOrderIds || []).filter(x => String(x) !== key);
    if (route.stops.length === before) return;
    invalidateOptimization(route);
    if (typeof window.save === "function") window.save();
    if (typeof window.render === "function") window.render();
  };

  window.addCustomRouteStop = function () {
    const route = activeRoute();
    if (!route) { alert("Primero cargá o creá una ruta."); return; }
    const input = document.getElementById("mvf-custom-stop-input");
    const label = (input?.value || "").trim();
    const lat = input?.dataset.lat;
    const lng = input?.dataset.lng;
    const placeId = input?.dataset.placeId || "";
    if (!label) { alert("Buscá y seleccioná una dirección para agregarla."); return; }
    if (lat === "" || lng === "" || lat == null || lng == null) {
      alert("Elegí una sugerencia de Google Maps para confirmar la ubicación de la parada.");
      return;
    }
    const id = "custom-" + Date.now().toString(36) + "-" + Math.random().toString(36).slice(2, 7);
    route.stops = route.stops || [];
    route.stops.push({
      orderId: id,
      custom: true,
      name: label,
      address: label,
      phone: "",
      lat: Number(lat),
      lng: Number(lng),
      placeId
    });
    invalidateOptimization(route);
    if (typeof window.save === "function") window.save();
    if (typeof window.render === "function") window.render();
  };

  function installRouteStopEditor() {
    const main = document.getElementById("main");
    const route = activeRoute();
    if (!main || !route || document.getElementById("mvf-route-stop-editor")) return;

    const card = document.createElement("section");
    card.className = "card";
    card.id = "mvf-route-stop-editor";
    card.innerHTML = '<h3 style="margin-top:0">✏️ Editar paradas de esta ruta</h3>' +
      '<p class="muted">Quitá paradas o agregá una dirección nueva. Después tocá “Optimizar paradas restantes desde mi ubicación” para recalcular desde tu ubicación actual hasta el destino final guardado.</p>' +
      '<label for="mvf-custom-stop-input">➕ Agregar una parada nueva</label>' +
      '<div class="route-address-wrap"><input id="mvf-custom-stop-input" placeholder="Buscá una dirección en Google Maps" autocomplete="off">' +
      '<button type="button" class="route-clear-btn" onclick="document.getElementById(\'mvf-custom-stop-input\').value=\'\';document.getElementById(\'mvf-custom-stop-input\').dataset.lat=\'\';document.getElementById(\'mvf-custom-stop-input\').dataset.lng=\'\';" title="Borrar dirección">✕</button></div>' +
      '<div id="mvf-custom-stop-status" class="address-status"></div>' +
      '<div class="actions" style="margin-top:8px"><button type="button" class="primary" onclick="addCustomRouteStop()">➕ Agregar parada</button></div>' +
      '<div id="mvf-route-stop-editor-list" style="margin-top:12px"></div>';

    const routeCard = main.querySelector(".card");
    if (routeCard && routeCard.nextSibling) main.insertBefore(card, routeCard.nextSibling);
    else main.appendChild(card);

    const list = card.querySelector("#mvf-route-stop-editor-list");
    const stops = route.stops || [];
    if (!stops.length) {
      list.innerHTML = '<div class="empty">La ruta no tiene paradas. Podés agregar una dirección arriba o seleccionar pedidos disponibles.</div>';
    } else {
      list.innerHTML = stops.map((s, i) => {
        const id = String(s.orderId ?? s.customId ?? s.id ?? "");
        const name = String(s.name || s.address || "Parada").replace(/[&<>"]/g, ch => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[ch]));
        const address = String(s.address || "").replace(/[&<>"]/g, ch => ({"&":"&amp;","<":"&lt;",">":"&gt;"}[ch]));
        return '<div class="stock-row"><span><b>' + (i + 1) + '. ' + name + '</b><br><small>📍 ' + address + (id.startsWith("custom-") ? ' · Parada agregada' : '') + '</small></span>' +
          '<button type="button" class="danger small" data-stop-id="' + encodeURIComponent(id) + '" aria-label="Eliminar parada">✕</button></div>';
      }).join("");
      list.querySelectorAll("[data-stop-id]").forEach(button => {
        button.addEventListener("click", () => {
          window.removeEditableRouteStop(decodeURIComponent(button.dataset.stopId || ""));
        });
      });
    }

    if (typeof window.setupRouteAutocomplete === "function") {
      window.setupRouteAutocomplete("mvf-custom-stop-input", "mvf-custom-stop-status", "");
    }
  }

  // Add the editor whenever the route page is rendered, without replacing existing UI.
  if (typeof window.routePage === "function") {
    const originalRoutePage = window.routePage;
    window.routePage = function (main) {
      const result = originalRoutePage.apply(this, arguments);
      setTimeout(installRouteStopEditor, 0);
      return result;
    };
  }

  // Add a cross to each stop in the optimized route list as well.
  if (typeof window.renderOptimizedRouteMap === "function") {
    const originalRenderOptimizedRouteMap = window.renderOptimizedRouteMap;
    window.renderOptimizedRouteMap = function (result, optimized, origin, destination) {
      const output = originalRenderOptimizedRouteMap.apply(this, arguments);
      setTimeout(() => {
        const list = document.getElementById("route-optimized-list");
        if (!list) return;
        list.querySelectorAll(".route-stop-result").forEach((row, index) => {
          if (row.querySelector(".mvf-remove-optimized-stop")) return;
          const stop = optimized && optimized[index];
          if (!stop) return;
          const button = document.createElement("button");
          button.type = "button";
          button.className = "danger small mvf-remove-optimized-stop";
          button.title = "Quitar esta parada de la ruta";
          button.setAttribute("aria-label", "Quitar parada");
          button.textContent = "✕";
          button.style.marginLeft = "5px";
          button.onclick = () => window.removeEditableRouteStop(String(stop.id));
          const actions = row.querySelector(".route-stop-gps");
          if (actions) actions.appendChild(button);
        });
      }, 0);
      return output;
    };
  }
})();
</script>
"""

def patch_html(html: str) -> str:
    if MARKER in html:
        return html
    required = [
        "function routePage(",
        "function optimizeActiveRoute(",
        "function reoptimizeFromCurrentLocation(",
        "function routeStopsForActiveRoute("
    ]
    missing = [needle for needle in required if needle not in html]
    if missing:
        raise SystemExit(
            "No se puede aplicar la edición segura de rutas: faltan anclas del motor de rutas: "
            + ", ".join(missing)
        )
    if "</body>" not in html:
        raise SystemExit("No se encontró </body> en el HTML de la APK.")
    return html.replace("</body>", INJECTION + "\n</body>", 1)

def main():
    if len(sys.argv) != 2:
        raise SystemExit("Uso: patch-route-editing.py RUTA_A_INDEX_HTML")
    path = Path(sys.argv[1])
    original = path.read_text(encoding="utf-8")
    patched = patch_html(original)
    path.write_text(patched, encoding="utf-8")
    print("Edición de paradas integrada: eliminar, agregar dirección y reoptimizar.")

if __name__ == "__main__":
    main()
