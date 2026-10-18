/** Preview a selected local photo without uploading it or changing the saved item. */
for (const section of document.querySelectorAll("[data-photo-preview]")) {
    const input = section.querySelector('input[type="file"]');
    const image = section.querySelector("[data-photo-preview-image]");
    const clear = section.querySelector("[data-photo-clear]");
    const status = section.querySelector("[data-photo-preview-status]");
    if (
        !(input instanceof HTMLInputElement) ||
        !(image instanceof HTMLImageElement) ||
        !(clear instanceof HTMLButtonElement) ||
        !(status instanceof HTMLParagraphElement)
    ) {
        throw new TypeError(
            "Equipment photo preview is missing its file, image, clear or status control.",
        );
    }
    const originalSource = image.src;
    const originalStatus = status.textContent;
    let previewUrl = "";

    function releasePreview() {
        if (previewUrl !== "") {
            URL.revokeObjectURL(previewUrl);
            previewUrl = "";
        }
    }

    function restorePreview() {
        releasePreview();
        image.src = originalSource;
        clear.hidden = true;
        status.textContent = originalStatus;
    }

    input.addEventListener("change", () => {
        const selected = input.files?.item(0);
        restorePreview();
        if (selected !== null && selected !== undefined) {
            previewUrl = URL.createObjectURL(selected);
            image.src = previewUrl;
            clear.hidden = false;
            status.textContent = `Selected: ${selected.name}. Save the form to upload this image.`;
        }
    });
    image.addEventListener("error", () => {
        status.textContent =
            "The image could not be previewed. Choose a valid JPEG, PNG or WebP file.";
    });
    clear.addEventListener("click", () => {
        input.value = "";
        restorePreview();
        status.textContent =
            "Selected image removed. Choose another photo or keep the original image.";
        input.focus();
    });
    window.addEventListener("pagehide", (event) => {
        if (!event.persisted) {
            releasePreview();
        }
    });
}
