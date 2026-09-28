document.addEventListener("DOMContentLoaded", () => {
  // DOM Elements
  const servicesInput = document.getElementById("servicesInput");
  const locationsInput = document.getElementById("locationsInput");
  const servicesCount = document.getElementById("servicesCount");
  const locationsCount = document.getElementById("locationsCount");
  const servicesBadges = document.getElementById("servicesBadges");
  const locationsBadges = document.getElementById("locationsBadges");
  
  const combosCount = document.getElementById("combosCount");
  const combosList = document.getElementById("combosList");
  const combosHeader = document.getElementById("combosHeader");
  const combosBody = document.getElementById("combosBody");
  const combosToggleIcon = document.getElementById("combosToggleIcon");

  const btnLoadSample = document.getElementById("btnLoadSample");
  const maxResultsSelect = document.getElementById("maxResultsSelect");
  const maxResultsCustom = document.getElementById("maxResultsCustom");
  const btnDedupRemove = document.getElementById("btnDedupRemove");
  const btnDedupKeep = document.getElementById("btnDedupKeep");

  const btnStart = document.getElementById("btnStart");
  const btnPause = document.getElementById("btnPause");
  const btnResume = document.getElementById("btnResume");
  const btnStop = document.getElementById("btnStop");
  const btnExportExcel = document.getElementById("btnExportExcel");

  const statusBadge = document.getElementById("statusBadge");
  const statusDot = document.getElementById("statusDot");
  const statusText = document.getElementById("statusText");
  const progressStatusMsg = document.getElementById("progressStatusMsg");
  const progressBar = document.getElementById("progressBar");
  const progressPercentText = document.getElementById("progressPercentText");

  const statCombos = document.getElementById("statCombos");
  const statCombosSub = document.getElementById("statCombosSub");
  const statCurrentSearch = document.getElementById("statCurrentSearch");
  const statSearchSub = document.getElementById("statSearchSub");
  const statFound = document.getElementById("statFound");
  const statProcessed = document.getElementById("statProcessed");
  const statRemaining = document.getElementById("statRemaining");
  const statCurrentBiz = document.getElementById("statCurrentBiz");

  const topCollectedCount = document.getElementById("topCollectedCount");
  const tableCountBadge = document.getElementById("tableCountBadge");
  const tableShowingCount = document.getElementById("tableShowingCount");
  const resultsTableBody = document.getElementById("resultsTableBody");

  // Filters
  const filterSearch = document.getElementById("filterSearch");
  const filterService = document.getElementById("filterService");
  const filterLocation = document.getElementById("filterLocation");
  const filterClaim = document.getElementById("filterClaim");
  const filterHasEmail = document.getElementById("filterHasEmail");

  // State
  let removeDuplicates = true;
  let allBusinesses = [];
  let currentJobState = "idle";
  let eventSource = null;

  // 1. Text Parsing Helpers
  function parseList(text) {
    if (!text) return [];
    return text
      .split(/[\n,]+/)
      .map(item => item.trim())
      .filter(item => item.length > 0);
  }

  function updateInputsPreview() {
    const services = parseList(servicesInput.value);
    const locations = parseList(locationsInput.value);

    // Update Services Badges
    servicesCount.textContent = `${services.length} services`;
    servicesBadges.innerHTML = services.map(s => 
      `<span class="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-indigo-50 text-indigo-700 border border-indigo-100">${escapeHtml(s)}</span>`
    ).join("");

    // Update Locations Badges
    locationsCount.textContent = `${locations.length} locations`;
    locationsBadges.innerHTML = locations.map(l => 
      `<span class="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-rose-50 text-rose-700 border border-rose-100">${escapeHtml(l)}</span>`
    ).join("");

    // Calculate Cartesian Product
    const combos = [];
    services.forEach(s => {
      locations.forEach(l => {
        combos.push({ service: s, location: l });
      });
    });

    combosCount.textContent = combos.length;
    combosList.innerHTML = combos.map((c, i) => `
      <div class="p-2 rounded-lg bg-white border border-slate-200 flex items-center space-x-2">
        <span class="w-5 h-5 rounded bg-slate-100 text-slate-500 font-bold flex items-center justify-center text-[10px] shrink-0">${i + 1}</span>
        <div class="truncate">
          <span class="font-semibold text-slate-800">${escapeHtml(c.service)}</span>
          <span class="text-slate-400 mx-1">in</span>
          <span class="text-slate-600">${escapeHtml(c.location)}</span>
        </div>
      </div>
    `).join("");
  }

  // Input Event Listeners
  servicesInput.addEventListener("input", updateInputsPreview);
  locationsInput.addEventListener("input", updateInputsPreview);

  // Toggle Combinations Accordion
  combosHeader.addEventListener("click", () => {
    const isHidden = combosBody.classList.contains("hidden");
    if (isHidden) {
      combosBody.classList.remove("hidden");
      combosToggleIcon.classList.add("rotate-180");
    } else {
      combosBody.classList.add("hidden");
      combosToggleIcon.classList.remove("rotate-180");
    }
  });

  // Load Sample Button
  btnLoadSample.addEventListener("click", () => {
    servicesInput.value = "Dumpster Rental\nPest Control";
    locationsInput.value = "New York\nCalifornia";
    updateInputsPreview();
  });

  // Duplicate Toggle Buttons
  btnDedupRemove.addEventListener("click", () => {
    removeDuplicates = true;
    btnDedupRemove.className = "px-2.5 py-1 text-xs font-semibold rounded-md bg-white text-indigo-700 shadow-xs transition";
    btnDedupKeep.className = "px-2.5 py-1 text-xs font-medium rounded-md text-slate-600 hover:text-slate-900 transition";
  });

  btnDedupKeep.addEventListener("click", () => {
    removeDuplicates = false;
    btnDedupKeep.className = "px-2.5 py-1 text-xs font-semibold rounded-md bg-white text-indigo-700 shadow-xs transition";
    btnDedupRemove.className = "px-2.5 py-1 text-xs font-medium rounded-md text-slate-600 hover:text-slate-900 transition";
  });

  // Max Results Select Change
  maxResultsSelect.addEventListener("change", () => {
    if (maxResultsSelect.value === "custom") {
      maxResultsCustom.classList.remove("hidden");
      maxResultsCustom.focus();
    } else {
      maxResultsCustom.classList.add("hidden");
    }
  });

  // 2. Control Action Handlers
  btnStart.addEventListener("click", async () => {
    const services = parseList(servicesInput.value);
    const locations = parseList(locationsInput.value);

    if (services.length === 0 || locations.length === 0) {
      alert("Please enter at least one service and one location before starting.");
      return;
    }

    const maxResultsValue = maxResultsSelect.value === "custom"
      ? (parseInt(maxResultsCustom.value) || 1000)
      : (parseInt(maxResultsSelect.value) || 25);

    const payload = {
      services: services,
      locations: locations,
      max_results: maxResultsValue,
      remove_duplicates: removeDuplicates
    };

    btnStart.disabled = true;
    try {
      const resp = await fetch("/api/start", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      const data = await resp.json();
      if (!data.success) {
        alert(data.message || "Failed to start job.");
      }
      applySnapshot(data.snapshot);
    } catch (err) {
      alert("Error starting job: " + err.message);
    } finally {
      btnStart.disabled = false;
    }
  });

  btnPause.addEventListener("click", async () => {
    try {
      const resp = await fetch("/api/pause", { method: "POST" });
      const data = await resp.json();
      applySnapshot(data.snapshot);
    } catch (err) {
      console.error("Pause error:", err);
    }
  });

  btnResume.addEventListener("click", async () => {
    try {
      const resp = await fetch("/api/resume", { method: "POST" });
      const data = await resp.json();
      applySnapshot(data.snapshot);
    } catch (err) {
      console.error("Resume error:", err);
    }
  });

  btnStop.addEventListener("click", async () => {
    if (!confirm("Are you sure you want to stop the scraping process? Data collected so far will be preserved.")) {
      return;
    }
    try {
      const resp = await fetch("/api/stop", { method: "POST" });
      const data = await resp.json();
      applySnapshot(data.snapshot);
    } catch (err) {
      console.error("Stop error:", err);
    }
  });

  btnExportExcel.addEventListener("click", () => {
    window.location.href = "/api/export";
  });

  // 3. UI State & Snapshot Applier
  function applySnapshot(snap) {
    if (!snap) return;
    currentJobState = snap.state;

    // Badge styling
    updateStateBadge(snap.state);

    // Update Action Buttons
    btnStart.disabled = (snap.state === "running" || snap.state === "paused");
    btnPause.disabled = (snap.state !== "running");
    btnResume.disabled = (snap.state !== "paused");
    btnStop.disabled = (snap.state !== "running" && snap.state !== "paused");

    // Progress bar & texts
    const pct = Math.max(0, Math.min(100, snap.progress_percent || 0));
    progressBar.style.width = `${pct}%`;
    progressPercentText.textContent = `${pct}%`;
    progressStatusMsg.textContent = snap.status_message || "Ready";

    // Metrics Grid
    statCombos.textContent = `${snap.current_combination_idx} / ${snap.total_combinations}`;
    statCombosSub.textContent = `${snap.total_combinations} total combos`;

    if (snap.current_service && snap.current_location) {
      statCurrentSearch.textContent = `${snap.current_service} in ${snap.current_location}`;
      statSearchSub.textContent = `Combo #${snap.current_combination_idx}`;
    } else {
      statCurrentSearch.textContent = "None";
      statSearchSub.textContent = "Waiting to start";
    }

    statFound.textContent = snap.businesses_found || 0;
    statProcessed.textContent = snap.businesses_processed || 0;
    statRemaining.textContent = snap.businesses_remaining || 0;
    statCurrentBiz.textContent = snap.current_business_name || "-";

    // Businesses list & table
    if (snap.businesses) {
      allBusinesses = snap.businesses;
      topCollectedCount.textContent = allBusinesses.length;
      tableCountBadge.textContent = `${allBusinesses.length} Businesses`;
      btnExportExcel.disabled = (allBusinesses.length === 0);
      updateFilterOptions();
      renderFilteredTable();
    }
  }

  function updateStateBadge(state) {
    statusBadge.className = "inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold border transition";
    statusDot.className = "w-2 h-2 rounded-full mr-2";

    switch (state) {
      case "running":
        statusBadge.classList.add("bg-blue-50", "text-blue-700", "border-blue-200");
        statusDot.classList.add("bg-blue-500", "animate-ping");
        statusText.textContent = "Automation Running";
        break;
      case "paused":
        statusBadge.classList.add("bg-amber-50", "text-amber-700", "border-amber-200");
        statusDot.classList.add("bg-amber-500");
        statusText.textContent = "Process Paused";
        break;
      case "completed":
        statusBadge.classList.add("bg-emerald-50", "text-emerald-700", "border-emerald-200");
        statusDot.classList.add("bg-emerald-500");
        statusText.textContent = "Search Completed";
        break;
      case "stopped":
        statusBadge.classList.add("bg-rose-50", "text-rose-700", "border-rose-200");
        statusDot.classList.add("bg-rose-500");
        statusText.textContent = "Process Stopped";
        break;
      case "error":
        statusBadge.classList.add("bg-red-50", "text-red-700", "border-red-200");
        statusDot.classList.add("bg-red-500");
        statusText.textContent = "Error Occurred";
        break;
      default:
        statusBadge.classList.add("bg-slate-100", "text-slate-700", "border-slate-200");
        statusDot.classList.add("bg-slate-400");
        statusText.textContent = "System Ready";
        break;
    }
  }

  // 4. Table Rendering & Dynamic Filters
  function updateFilterOptions() {
    const servicesSet = new Set();
    const locationsSet = new Set();

    allBusinesses.forEach(b => {
      (b.searchService || "").split(",").forEach(s => s.trim() && servicesSet.add(s.trim()));
      (b.searchLocation || "").split(",").forEach(l => l.trim() && locationsSet.add(l.trim()));
    });

    // Populate Service filter dropdown
    const currentSelectedService = filterService.value;
    filterService.innerHTML = '<option value="">All Services</option>' + 
      Array.from(servicesSet).sort().map(s => 
        `<option value="${escapeHtml(s)}"${s === currentSelectedService ? " selected" : ""}>${escapeHtml(s)}</option>`
      ).join("");

    // Populate Location filter dropdown
    const currentSelectedLocation = filterLocation.value;
    filterLocation.innerHTML = '<option value="">All Locations</option>' + 
      Array.from(locationsSet).sort().map(l => 
        `<option value="${escapeHtml(l)}"${l === currentSelectedLocation ? " selected" : ""}>${escapeHtml(l)}</option>`
      ).join("");
  }

  function renderFilteredTable() {
    const q = (filterSearch.value || "").toLowerCase();
    const srv = filterService.value;
    const loc = filterLocation.value;
    const claim = filterClaim.value;
    const hasEmail = filterHasEmail.value;

    const filtered = allBusinesses.filter(b => {
      // Free text search
      if (q) {
        const textBlob = `${b.name} ${b.category} ${b.address} ${b.phone} ${b.email} ${b.city} ${b.state}`.toLowerCase();
        if (!textBlob.includes(q)) return false;
      }
      // Service filter
      if (srv && !((b.searchService || "").toLowerCase().includes(srv.toLowerCase()))) {
        return false;
      }
      // Location filter
      if (loc && !((b.searchLocation || "").toLowerCase().includes(loc.toLowerCase()))) {
        return false;
      }
      // Claim status filter
      if (claim && b.claimStatus !== claim) {
        return false;
      }
      // Email filter
      if (hasEmail === "yes" && (!b.email || b.email === "Not Available")) {
        return false;
      }
      if (hasEmail === "no" && b.email && b.email !== "Not Available") {
        return false;
      }
      return true;
    });

    tableShowingCount.textContent = `Showing ${filtered.length} of ${allBusinesses.length} businesses`;

    if (filtered.length === 0) {
      resultsTableBody.innerHTML = `
        <tr>
          <td colspan="14" class="py-12 text-center text-slate-400">
            <i class="fa-solid fa-filter-circle-xmark text-2xl text-slate-300 mb-2"></i>
            <p class="font-medium text-xs text-slate-600">No matching business listings found</p>
            <p class="text-[11px] text-slate-400">Try adjusting your search query or filters.</p>
          </td>
        </tr>
      `;
      return;
    }

    resultsTableBody.innerHTML = filtered.map((b, i) => {
      // Claim Status Pill
      let claimBadge = `<span class="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-slate-100 text-slate-600 border border-slate-200">Not Available</span>`;
      if (b.claimStatus === "Available") {
        claimBadge = `<span class="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-300"><i class="fa-solid fa-check mr-1 text-[10px]"></i>Available</span>`;
      } else if (b.claimStatus === "Unknown") {
        claimBadge = `<span class="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-amber-100 text-amber-800 border border-amber-300">Unknown</span>`;
      }

      // Email Pill
      let emailBadge = `<span class="text-slate-400">Not Available</span>`;
      if (b.email && b.email !== "Not Available") {
        emailBadge = `<a href="mailto:${escapeHtml(b.email)}" class="inline-flex items-center text-indigo-600 hover:text-indigo-800 font-medium truncate max-w-[150px]"><i class="fa-regular fa-envelope mr-1 text-slate-400"></i>${escapeHtml(b.email)}</a>`;
      }

      // Website link
      let websiteLink = `<span class="text-slate-300">-</span>`;
      if (b.website && b.website !== "Not Available") {
        websiteLink = `<a href="${escapeHtml(b.website)}" target="_blank" rel="noopener" class="inline-flex items-center justify-center w-6 h-6 rounded bg-slate-100 hover:bg-slate-200 text-slate-600 transition" title="${escapeHtml(b.website)}"><i class="fa-solid fa-arrow-up-right-from-square text-[10px]"></i></a>`;
      }

      // Maps link
      let mapsLink = `<span class="text-slate-300">-</span>`;
      if (b.url && b.url !== "Not Available") {
        mapsLink = `<a href="${escapeHtml(b.url)}" target="_blank" rel="noopener" class="inline-flex items-center justify-center w-6 h-6 rounded bg-blue-50 hover:bg-blue-100 text-blue-600 transition" title="Open in Google Maps"><i class="fa-solid fa-location-dot text-xs"></i></a>`;
      }

      // Rating & Reviews
      let ratingDisplay = `<span class="text-slate-400">-</span>`;
      if (b.rating && b.rating !== "Not Available") {
        ratingDisplay = `<div class="inline-flex items-center"><i class="fa-solid fa-star text-amber-400 mr-1 text-[10px]"></i><span class="font-bold text-slate-800">${escapeHtml(b.rating)}</span>${b.reviews && b.reviews !== 'Not Available' ? `<span class="text-slate-400 ml-1">(${escapeHtml(b.reviews)})</span>` : ''}</div>`;
      }

      return `
        <tr class="hover:bg-slate-50/80 transition">
          <td class="py-2.5 px-3 text-center text-slate-400 font-mono text-[11px]">${i + 1}</td>
          <td class="py-2.5 px-3 font-semibold text-slate-900">${escapeHtml(b.name)}</td>
          <td class="py-2.5 px-3 text-slate-600">${escapeHtml(b.category)}</td>
          <td class="py-2.5 px-3 text-slate-700 font-mono text-[11px] whitespace-nowrap">${escapeHtml(b.phone)}</td>
          <td class="py-2.5 px-3">${emailBadge}</td>
          <td class="py-2.5 px-3 text-center">${websiteLink}</td>
          <td class="py-2.5 px-3 text-slate-600 truncate max-w-[200px]" title="${escapeHtml(b.address)}">${escapeHtml(b.address)}</td>
          <td class="py-2.5 px-3 text-slate-700">${escapeHtml(b.city)}</td>
          <td class="py-2.5 px-3 text-slate-700">${escapeHtml(b.state)}</td>
          <td class="py-2.5 px-3 text-center">${ratingDisplay}</td>
          <td class="py-2.5 px-3 text-center">${claimBadge}</td>
          <td class="py-2.5 px-3 text-slate-600">${escapeHtml(b.searchService)}</td>
          <td class="py-2.5 px-3 text-slate-600">${escapeHtml(b.searchLocation)}</td>
          <td class="py-2.5 px-3 text-center">${mapsLink}</td>
        </tr>
      `;
    }).join("");
  }

  // Filter Listeners
  filterSearch.addEventListener("input", renderFilteredTable);
  filterService.addEventListener("change", renderFilteredTable);
  filterLocation.addEventListener("change", renderFilteredTable);
  filterClaim.addEventListener("change", renderFilteredTable);
  filterHasEmail.addEventListener("change", renderFilteredTable);

  function escapeHtml(text) {
    if (!text) return "";
    return String(text)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  // 5. Connect SSE Stream & Polling Fallback
  function initEventStream() {
    if (window.EventSource) {
      eventSource = new EventSource("/api/events");
      eventSource.onmessage = (event) => {
        try {
          const snap = JSON.parse(event.data);
          applySnapshot(snap);
        } catch (e) {
          console.error("SSE parse error:", e);
        }
      };
      eventSource.onerror = () => {
        // Fallback to polling if SSE drops
        console.warn("SSE connection interrupted, using backup polling.");
      };
    }

    // Backup polling every 2 seconds
    setInterval(async () => {
      try {
        const resp = await fetch("/api/status");
        if (resp.ok) {
          const snap = await resp.json();
          applySnapshot(snap);
        }
      } catch (e) {
        // quiet error
      }
    }, 2000);
  }

  // Initial Load
  updateInputsPreview();
  initEventStream();
});
