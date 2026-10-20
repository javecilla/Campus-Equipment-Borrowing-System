function readSeries(scriptId) {
    const script = document.getElementById(scriptId);

    if (!(script instanceof HTMLScriptElement)) {
        throw new Error(`Dashboard chart data ${scriptId} is missing.`);
    }

    const parsed = JSON.parse(script.textContent || "[]");
    if (!Array.isArray(parsed)) {
        throw new Error(`Dashboard chart data ${scriptId} must be an array.`);
    }

    return parsed.map((point) => {
        if (
            typeof point !== "object" ||
            point === null ||
            typeof point.label !== "string" ||
            !Number.isInteger(point.value) ||
            point.value < 0
        ) {
            throw new Error(`Dashboard chart data ${scriptId} contains an invalid point.`);
        }
        return point;
    });
}

function renderBarChart(rootId, scriptId) {
    const root = document.getElementById(rootId);
    if (!(root instanceof HTMLElement)) {
        return;
    }

    const series = readSeries(scriptId);
    if (series.length === 0) {
        return;
    }

    const maximum = Math.max(...series.map((point) => point.value), 1);
    const list = document.createElement("ul");
    list.className = "space-y-4";
    list.setAttribute("aria-label", root.dataset.chartLabel || "Dashboard chart");

    for (const point of series) {
        const row = document.createElement("li");
        row.className =
            "grid gap-2 text-sm sm:grid-cols-[minmax(8rem,1fr)_minmax(10rem,2fr)_3rem] sm:items-center";

        const label = document.createElement("span");
        label.className = "font-medium text-slate-700";
        label.textContent = point.label;

        const track = document.createElement("span");
        track.className = "h-3 overflow-hidden rounded-full bg-slate-100";
        track.setAttribute("aria-hidden", "true");

        const bar = document.createElement("span");
        bar.className = "block h-full rounded-full bg-accent";
        bar.style.width = `${Math.max((point.value / maximum) * 100, 2)}%`;
        track.append(bar);

        const value = document.createElement("span");
        value.className = "font-semibold text-slate-900 sm:text-right";
        value.textContent = String(point.value);

        row.append(label, track, value);
        list.append(row);
    }

    root.replaceChildren(list);
}

renderBarChart("monthly-issued-loans-chart", "monthly-issued-loans-data");
renderBarChart("category-issued-units-chart", "category-issued-units-data");
