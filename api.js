// طبقة بسيطة للتواصل مع Backend API
const Api = (() => {
  async function request(path, options = {}) {
    const res = await fetch(path, {
      method: options.method || "GET",
      headers: { "Content-Type": "application/json" },
      credentials: "same-origin",
      body: options.body ? JSON.stringify(options.body) : undefined,
    });
    let data = null;
    try { data = await res.json(); } catch (e) { data = null; }
    if (!res.ok) {
      const err = new Error((data && data.error) || "حدث خطأ غير متوقع");
      err.status = res.status;
      err.data = data;
      throw err;
    }
    return data;
  }

  return {
    get: (path) => request(path, { method: "GET" }),
    post: (path, body) => request(path, { method: "POST", body }),
    del: (path) => request(path, { method: "DELETE" }),

    health: () => request("/api/health"),
    airports: (q) => request(`/api/airports?q=${encodeURIComponent(q || "")}`),
    searchFlights: (payload) => request("/api/flights/search", { method: "POST", body: payload }),
    flightDetails: (payload) => request("/api/flights/details", { method: "POST", body: payload }),
    compareFlights: (a, b) => request("/api/flights/compare", { method: "POST", body: { flight_a: a, flight_b: b } }),
    budgetEstimate: (payload) => request("/api/budget/estimate", { method: "POST", body: payload }),

    popularPlaces: (destination) => request("/api/ai/popular-places", { method: "POST", body: { destination } }),
    planTrip: (payload) => request("/api/ai/plan-trip", { method: "POST", body: payload }),
    planFullTrip: (payload) => request("/api/ai/plan-full-trip", { method: "POST", body: payload }),

    destinations: () => request("/api/destinations"),
    destination: (code) => request(`/api/destinations/${code}`),

    me: () => request("/api/auth/me"),
    login: (email, password) => request("/api/auth/login", { method: "POST", body: { email, password } }),
    register: (full_name, email, password) => request("/api/auth/register", { method: "POST", body: { full_name, email, password } }),
    logout: () => request("/api/auth/logout", { method: "POST" }),

    favorites: () => request("/api/favorites"),
    addFavorite: (item_type, item_ref, item_data) => request("/api/favorites", { method: "POST", body: { item_type, item_ref, item_data } }),
    removeFavorite: (id) => request(`/api/favorites/${id}`, { method: "DELETE" }),

    adminStats: () => request("/api/admin/stats"),
    adminSearches: () => request("/api/admin/searches"),
    adminAirlines: () => request("/api/admin/airlines"),
    adminUsers: () => request("/api/admin/users"),
    adminProvidersStatus: () => request("/api/admin/providers-status"),
  };
})();
