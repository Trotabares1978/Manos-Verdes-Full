import { Geolocation } from "@capacitor/geolocation";

window.RuteroideGeo = {
  getCurrentPosition: async function () {
    return Geolocation.getCurrentPosition({
      enableHighAccuracy: true,
      timeout: 20000,
      maximumAge: 0
    });
  }
};
