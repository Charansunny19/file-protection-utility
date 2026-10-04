// ============================================================
// ELEMENTS
// ============================================================

const fileInput = document.getElementById("fileInput");

const chooseButton =
    document.getElementById("chooseButton");

const uploadArea =
    document.getElementById("uploadArea");

const selectedFile =
    document.getElementById("selectedFile");

const password =
    document.getElementById("password");

const togglePassword =
    document.getElementById("togglePassword");

const encryptMode =
    document.getElementById("encryptMode");

const decryptMode =
    document.getElementById("decryptMode");

const actionButton =
    document.getElementById("actionButton");

const uploadTitle =
    document.getElementById("uploadTitle");

const statusBox =
    document.getElementById("status");

const progressContainer =
    document.getElementById("progressContainer");

const progressText =
    document.getElementById("progressText");

const passwordStrength =
    document.getElementById("passwordStrength");


let currentMode = "encrypt";


// ============================================================
// FILE SELECTION
// ============================================================

chooseButton.addEventListener("click", function () {

    fileInput.click();

});


fileInput.addEventListener("change", function () {

    if (fileInput.files.length === 0) {
        selectedFile.textContent = "";
        return;
    }

    const file = fileInput.files[0];

    selectedFile.textContent =
        "Selected: " + file.name;

});


// ============================================================
// DRAG AND DROP
// ============================================================

uploadArea.addEventListener("dragover", function (event) {

    event.preventDefault();

    uploadArea.style.borderColor = "#4e9fe0";

});


uploadArea.addEventListener("dragleave", function () {

    uploadArea.style.borderColor = "";

});


uploadArea.addEventListener("drop", function (event) {

    event.preventDefault();

    uploadArea.style.borderColor = "";

    if (event.dataTransfer.files.length > 0) {

        fileInput.files =
            event.dataTransfer.files;

        selectedFile.textContent =
            "Selected: " +
            event.dataTransfer.files[0].name;

    }

});


// ============================================================
// MODE SWITCHING
// ============================================================

encryptMode.addEventListener("click", function () {

    currentMode = "encrypt";

    encryptMode.classList.add("active");

    decryptMode.classList.remove("active");

    uploadTitle.textContent =
        "Select a file to encrypt";

    actionButton.textContent =
        "🔒 Encrypt File";

    clearStatus();

});


decryptMode.addEventListener("click", function () {

    currentMode = "decrypt";

    decryptMode.classList.add("active");

    encryptMode.classList.remove("active");

    uploadTitle.textContent =
        "Select an encrypted file";

    actionButton.textContent =
        "🔓 Decrypt File";

    clearStatus();

});


// ============================================================
// PASSWORD VISIBILITY
// ============================================================

togglePassword.addEventListener("click", function () {

    if (password.type === "password") {

        password.type = "text";

        togglePassword.textContent = "🙈";

    } else {

        password.type = "password";

        togglePassword.textContent = "👁";

    }

});


// ============================================================
// PASSWORD STRENGTH
// ============================================================

password.addEventListener("input", function () {

    const value = password.value;

    if (value.length === 0) {

        passwordStrength.style.background =
            "#263344";

        return;
    }

    let strength = 0;

    if (value.length >= 8) strength++;

    if (value.length >= 12) strength++;

    if (/[A-Z]/.test(value)) strength++;

    if (/[a-z]/.test(value)) strength++;

    if (/[0-9]/.test(value)) strength++;

    if (/[^A-Za-z0-9]/.test(value)) strength++;


    if (strength <= 2) {

        passwordStrength.style.background =
            "#d95b63";

    } else if (strength <= 4) {

        passwordStrength.style.background =
            "#d5a94d";

    } else {

        passwordStrength.style.background =
            "#4acb82";

    }

});


// ============================================================
// ACTION
// ============================================================

actionButton.addEventListener("click", async function () {

    clearStatus();

    // Check file

    if (!fileInput.files.length) {

        showError(
            "Please select a file first."
        );

        return;
    }


    // Check password

    if (!password.value) {

        showError(
            "Please enter a password."
        );

        return;
    }


    const file = fileInput.files[0];

    const formData = new FormData();

    formData.append(
        "file",
        file
    );

    formData.append(
        "password",
        password.value
    );


    // UI

    actionButton.disabled = true;

    progressContainer.style.display = "block";

    progressText.textContent =
        currentMode === "encrypt"
            ? "Encrypting your file..."
            : "Verifying and decrypting your file...";


    try {

        const endpoint =
            currentMode === "encrypt"
                ? "/encrypt"
                : "/decrypt";


        const response =
            await fetch(
                "http://127.0.0.1:5000" + endpoint,
                {
                    method: "POST",
                    body: formData
                }
            );


        if (!response.ok) {

            let errorMessage =
                "Operation failed.";

            try {

                const errorData =
                    await response.json();

                errorMessage =
                    errorData.message ||
                    errorMessage;

            } catch (error) {

                // Ignore JSON parsing error

            }

            throw new Error(
                errorMessage
            );
        }


        // Get file from response

        const blob =
            await response.blob();


        // Get filename

        const contentDisposition =
            response.headers.get(
                "Content-Disposition"
            );


        let filename =
            currentMode === "encrypt"
                ? file.name + ".enc"
                : file.name + ".decrypted";


        if (contentDisposition) {

            const match =
                contentDisposition.match(
                    /filename="?([^"]+)"?/
                );

            if (match) {

                filename =
                    match[1];

            }

        }


        // Download

        const url =
            window.URL.createObjectURL(
                blob
            );

        const link =
            document.createElement("a");

        link.href = url;

        link.download = filename;

        document.body.appendChild(link);

        link.click();

        link.remove();

        window.URL.revokeObjectURL(url);


        // Success

        if (currentMode === "encrypt") {

            showSuccess(
                "File encrypted successfully! Your .enc file has been downloaded."
            );

        } else {

            showSuccess(
                "HMAC integrity verified and file decrypted successfully!"
            );

        }

    } catch (error) {

        showError(
            error.message
        );

    } finally {

        actionButton.disabled = false;

        progressContainer.style.display =
            "none";

    }

});


// ============================================================
// STATUS FUNCTIONS
// ============================================================

function showSuccess(message) {

    statusBox.className =
        "status success";

    statusBox.textContent =
        "✅ " + message;

}


function showError(message) {

    statusBox.className =
        "status error";

    statusBox.textContent =
        "❌ " + message;

}


function clearStatus() {

    statusBox.className =
        "status";

    statusBox.textContent =
        "";

}