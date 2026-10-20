/** Open a request from its row while retaining the native link and text selection. */
for (const row of document.querySelectorAll("[data-request-row]")) {
    const link = row.querySelector("[data-request-link]");
    if (!(link instanceof HTMLAnchorElement)) {
        throw new TypeError("A request row must contain its detail link.");
    }

    row.addEventListener("click", (event) => {
        if (
            event.button !== 0 ||
            event.ctrlKey ||
            event.metaKey ||
            event.shiftKey ||
            event.altKey ||
            !(event.target instanceof Element) ||
            event.target.closest(
                "a, button, input, select, textarea, label, [role='button'], [contenteditable]",
            ) ||
            window.getSelection()?.isCollapsed === false
        ) {
            return;
        }
        window.location.assign(link.href);
    });
}
