/** Check the fixed stylesheet's text-role contrast without generating a palette. */
import { readFile } from "node:fs/promises";

const stylesheet = await readFile("static/css/app.css", "utf8");

/** @param {string} role @returns {string} */
function roleColor(role) {
    const declaration = new RegExp(`--md-sys-color-${role}:\\s*(#[0-9a-f]{6});`, "i");
    const match = stylesheet.match(declaration);
    if (match === null) {
        throw new SyntaxError(
            `static/css/app.css must define --md-sys-color-${role} as a six-digit hex color.`,
        );
    }
    return match[1];
}

/** @param {number} channel @returns {number} */
function linearChannel(channel) {
    const value = channel / 255;
    return value <= 0.04045 ? value / 12.92 : ((value + 0.055) / 1.055) ** 2.4;
}

/** @param {string} color @returns {number} */
function luminance(color) {
    const red = linearChannel(Number.parseInt(color.slice(1, 3), 16));
    const green = linearChannel(Number.parseInt(color.slice(3, 5), 16));
    const blue = linearChannel(Number.parseInt(color.slice(5, 7), 16));
    return 0.2126 * red + 0.7152 * green + 0.0722 * blue;
}

for (const [foregroundRole, backgroundRole] of [
    ["on-primary", "primary"],
    ["on-primary-container", "primary-container"],
    ["on-secondary-container", "secondary-container"],
    ["on-tertiary-container", "tertiary-container"],
    ["on-error", "error"],
    ["on-error-container", "error-container"],
    ["on-surface", "surface"],
    ["on-surface-variant", "surface-container-highest"],
    ["primary", "surface-container-low"],
]) {
    const foreground = roleColor(foregroundRole);
    const background = roleColor(backgroundRole);
    const first = luminance(foreground);
    const second = luminance(background);
    const ratio = (Math.max(first, second) + 0.05) / (Math.min(first, second) + 0.05);
    if (ratio < 4.5) {
        throw new RangeError(
            `Theme roles ${foregroundRole}/${backgroundRole} (${foreground}/${background}) have contrast ${ratio.toFixed(2)}; at least 4.5 is required.`,
        );
    }
}

console.log("All nine fixed theme text-role pairs meet 4.5:1 contrast.");
