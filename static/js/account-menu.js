/** Close an open account disclosure after an outside click or Escape. */
for (const menu of document.querySelectorAll("[data-account-menu]")) {
    if (!(menu instanceof HTMLDetailsElement)) {
        throw new TypeError("The account menu must be a details element.");
    }
    const toggle = menu.querySelector("summary");
    if (!(toggle instanceof HTMLElement)) {
        throw new TypeError("The account menu is missing its summary control.");
    }

    document.addEventListener("click", (event) => {
        if (menu.open && event.target instanceof Node && !menu.contains(event.target)) {
            menu.open = false;
        }
    });
    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape" && menu.open) {
            menu.open = false;
            toggle.focus();
        }
    });
}
