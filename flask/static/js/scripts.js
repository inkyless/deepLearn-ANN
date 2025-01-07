
const ImageUpload = document.getElementById('images');
const fileInput = document.querySelector("#output")
const submitButton = document.getElementById("submit")
fileInput.style.display = "none";

ImageUpload.addEventListener('change', function () {
  const file = ImageUpload.files[0];

  const reader = new FileReader();

  reader.onload = function (e) {
    const imageDataUrl = e.target.result;

    const imagepreview = document.getElementById("image-preview")
    const resetButton = document.getElementById("reset")
    const submitBox = document.getElementById("submit-wrap")

    imagepreview.innerHTML = "Hasil Unggahan Gambar"
    submitButton.style.visibility = "visible"
    submitBox.style.display = 'flex'
    submitButton.innerText = "Kumpul"
    resetButton.innerText = "Ulangi"
    resetButton.style.visibility = "visible"
    fileInput.src = imageDataUrl;
    fileInput.style.display = "block";

  };

  reader.readAsDataURL(file);
});




