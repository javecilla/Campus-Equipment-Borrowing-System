/** Keep the current destination visible in compact, horizontally scrolling navigation. */
for (const navigation of document.querySelectorAll("[data-scroll-navigation]")) {
    if (!(navigation instanceof HTMLElement)) {
        throw new TypeError("Workspace navigation must be an HTML element.");
    }
    const current = navigation.querySelector('[aria-current="page"]');
    if (current === null) {
        continue; // Own-profile pages do not select a primary destination.
    }
    if (!(current instanceof HTMLElement)) {
        throw new TypeError("The current navigation destination must be an HTML element.");
    }
    navigation.scrollLeft =
        current.offsetLeft -
        navigation.offsetLeft -
        (navigation.clientWidth - current.clientWidth) / 2;
}
