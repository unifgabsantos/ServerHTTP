function enviar(){
    const recurso = document.getElementById("Recurso").value;
    if(recurso==""){
        alert("O campo recurso precisa ser preenchido");
        return false;
    }
    var request = new XMLHttpRequest();
    request.open("DELETE","http://localhost/"+recurso);
    request.onreadystatechange = function() {
        if (request.readyState == 4) {
            alert(request.responseText);
        }
    }
    request.send();
}