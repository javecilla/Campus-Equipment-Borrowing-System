/** Verify that both specimen fonts have loaded real font faces.
 * @returns {Promise<void>}
 */
async function verifyFonts() {
    const status = document.querySelector('[data-testid="font-load-status"]');
    if (!(status instanceof HTMLParagraphElement)) {
        throw new TypeError("The frontend test page is missing its font status paragraph.");
    }

    try {
        const [bodyFaces, headingFaces] = await Promise.all([
            document.fonts.load('400 16px "DM Sans"'),
            document.fonts.load('600 16px "Poppins"'),
        ]);
        if (bodyFaces.length === 0 || headingFaces.length === 0) {
            throw new Error("DM Sans or Poppins has no matching font-face declaration.");
        }
        status.textContent = "DM Sans and Poppins loaded successfully from local assets.";
    } catch (error) {
        status.textContent =
            "Font loading failed. Run npm run build and check /static/fonts/ requests in DevTools.";
        throw error;
    }
}

await verifyFonts();
