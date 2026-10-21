import { registerPlugin } from "@capacitor/core";
import { Geolocation } from "@capacitor/geolocation";

const RuteroideContacts = registerPlugin("RuteroideContacts");

window.RuteroideGeo = {
  getCurrentPosition: async function () {
    return Geolocation.getCurrentPosition({
      enableHighAccuracy: true,
      timeout: 20000,
      maximumAge: 0
    });
  }
};

// Preserve the API expected by the existing app HTML.
window.RuteroideContacts = RuteroideContacts;
