const printButton = document.getElementById("loan-slip-print");

if (!(printButton instanceof HTMLButtonElement)) {
    throw new Error("The borrowing slip requires its print button.");
}

printButton.addEventListener("click", () => window.print());
