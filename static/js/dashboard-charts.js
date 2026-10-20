import { BarController, BarElement, CategoryScale, Chart, LinearScale, Tooltip } from "chart.js";

Chart.register(BarController, BarElement, CategoryScale, LinearScale, Tooltip);

/** @typedef {{ label: string, value: number }} ChartPoint */
/** @typedef {{ primary: string, secondary: string, text: string, grid: string, font: string }} ChartTheme */

/** @param {string} scriptId @returns {ChartPoint[]} */
function readSeries(scriptId) {
    const script = document.getElementById(scriptId);
    if (!(script instanceof HTMLScriptElement)) {
        throw new Error(`Dashboard chart data ${scriptId} is missing.`);
    }
    const parsed = JSON.parse(script.textContent);
    if (!Array.isArray(parsed)) {
        throw new Error(`Dashboard chart data ${scriptId} must be an array.`);
    }
    return parsed.map((point) => {
        if (
            typeof point !== "object" ||
            point === null ||
            typeof point.label !== "string" ||
            !Number.isSafeInteger(point.value) ||
            point.value < 0
        ) {
            throw new Error(`Dashboard chart data ${scriptId} contains an invalid point.`);
        }
        return { label: point.label, value: point.value };
    });
}

/** @returns {ChartTheme} */
function chartTheme() {
    const style = getComputedStyle(document.documentElement);
    const roles = [
        "--md-sys-color-primary",
        "--md-sys-color-tertiary",
        "--md-sys-color-on-surface-variant",
        "--md-sys-color-outline-variant",
    ].map((name) => {
        const color = style.getPropertyValue(name).trim();
        if (!color) {
            throw new Error(`Dashboard chart theme token ${name} is missing.`);
        }
        return color;
    });
    return {
        primary: roles[0],
        secondary: roles[1],
        text: roles[2],
        grid: roles[3],
        font: getComputedStyle(document.body).fontFamily,
    };
}

/** @param {import("chart.js").TooltipItem<"bar">[]} items @returns {string[]} */
function tooltipTitle(items) {
    const length = Math.max(12, Math.floor((items[0].chart.width - 32) / 8));
    let label = items[0].label;
    const lines = [];
    while (label.length > length) {
        const space = label.lastIndexOf(" ", length);
        const end = space > 0 ? space : length;
        lines.push(label.slice(0, end));
        label = label.slice(end).trimStart();
    }
    lines.push(label);
    return lines;
}

/** @param {ChartTheme} theme @returns {import("chart.js").ChartOptions<"bar">} */
function chartOptions(theme) {
    return {
        responsive: true,
        maintainAspectRatio: false,
        animation: false,
        color: theme.text,
        font: { family: theme.font, size: 12 },
        interaction: { mode: "nearest", axis: "xy", intersect: true },
        plugins: {
            tooltip: {
                displayColors: false,
                padding: 12,
                titleFont: { family: theme.font },
                bodyFont: { family: theme.font },
                callbacks: { title: tooltipTitle },
            },
        },
    };
}

/** @param {ChartPoint[]} series @param {ChartTheme} theme */
function renderMonthlyChart(series, theme) {
    const container = document.getElementById("monthly-chart-container");
    const canvas = document.getElementById("monthly-issued-loans-chart");
    if (!(container instanceof HTMLElement) || !(canvas instanceof HTMLCanvasElement)) {
        throw new Error("Monthly loan chart canvas or container is missing.");
    }
    container.hidden = false;
    canvas.parentElement.style.minWidth = `${Math.max(200, series.length * 64)}px`;
    new Chart(canvas, {
        type: "bar",
        data: {
            labels: series.map((point) => point.label),
            datasets: [
                {
                    label: "Loans issued",
                    data: series.map((point) => point.value),
                    backgroundColor: theme.primary,
                    borderRadius: 5,
                    maxBarThickness: 44,
                },
            ],
        },
        options: {
            ...chartOptions(theme),
            scales: {
                x: { grid: { display: false }, ticks: { maxRotation: 0 } },
                y: {
                    beginAtZero: true,
                    suggestedMax: 1,
                    border: { display: false },
                    grid: { color: theme.grid },
                    ticks: { precision: 0 },
                    title: { display: true, text: "Loans issued" },
                },
            },
        },
    });
    canvas.dataset.chartReady = "true";
}

/** @param {ChartPoint[]} series @param {ChartTheme} theme */
function renderCategoryChart(series, theme) {
    const container = document.getElementById("category-chart-container");
    const canvas = document.getElementById("category-issued-units-chart");
    if (!(container instanceof HTMLElement) || !(canvas instanceof HTMLCanvasElement)) {
        throw new Error("Category usage chart canvas or container is missing.");
    }
    container.hidden = false;
    canvas.parentElement.style.height = `${Math.max(280, series.length * 52 + 64)}px`;
    new Chart(canvas, {
        type: "bar",
        data: {
            labels: series.map((point) => point.label),
            datasets: [
                {
                    label: "Units issued",
                    data: series.map((point) => point.value),
                    backgroundColor: theme.secondary,
                    borderRadius: 5,
                    maxBarThickness: 26,
                },
            ],
        },
        options: {
            ...chartOptions(theme),
            indexAxis: "y",
            scales: {
                x: {
                    beginAtZero: true,
                    suggestedMax: 1,
                    border: { display: false },
                    grid: { color: theme.grid },
                    ticks: { precision: 0 },
                    title: { display: true, text: "Physical units issued" },
                },
                y: {
                    grid: { display: false },
                    border: { display: false },
                    ticks: {
                        autoSkip: false,
                        callback: function (value) {
                            const label = this.getLabelForValue(value);
                            const length = Math.max(8, Math.floor((this.chart.width * 0.4) / 7));
                            return label.length > length ? `${label.slice(0, length)}…` : label;
                        },
                    },
                    afterFit: (scale) => {
                        scale.width = Math.min(scale.width, scale.chart.width * 0.45);
                    },
                },
            },
        },
    });
    canvas.dataset.chartReady = "true";
}

await document.fonts.ready;
const monthlySeries = readSeries("monthly-issued-loans-data");
const categorySeries = readSeries("category-issued-units-data");
const theme = chartTheme();
if (monthlySeries.length > 0) {
    renderMonthlyChart(monthlySeries, theme);
}
if (categorySeries.length > 0) {
    renderCategoryChart(categorySeries, theme);
}
