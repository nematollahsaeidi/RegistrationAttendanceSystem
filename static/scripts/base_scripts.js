//function set_date() {
//    var date = new Date();
//    var day = date.getDate();
//    var month = date.getMonth() + 1;
//    var year = date.getFullYear();
//    if (month < 10) month = "0" + month;
//    if (day < 10) day = "0" + day;
//    var today = year + "-" + month + "-" + day;
//    document.getElementById("start_date").value = today;
//}

// Script to open and close sidebar
function w3_open() {
  document.getElementById("mySidebar").style.display = "block";
  document.getElementById("myOverlay").style.display = "block";
}

function w3_close() {
  document.getElementById("mySidebar").style.display = "none";
  document.getElementById("myOverlay").style.display = "none";
}

// Modal Image Gallery
function onClick(element) {
  document.getElementById("img01").src = element.src;
  document.getElementById("modal01").style.display = "block";
  var captionText = document.getElementById("caption");
  captionText.innerHTML = element.alt;
}

function alert1() {
  alert("درخواست شما فرستاده شد. لطفا شکیبا باشید...");
  this.form.reset();
}