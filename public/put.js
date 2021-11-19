function enviar(){
    const recurso = document.getElementById("Recurso").value;
    const conteudo = document.getElementById("Conteudo").value;
    if(recurso=="" || conteudo==""){
        alert("Todos os campos devem estar preenchidos");
        return false;
    }
    var request = new XMLHttpRequest();
    request.open("PUT","http://localhost/"+recurso);
    request.onreadystatechange = function() {
        if (request.readyState == 4) {
            alert(request.responseText);
        }
    }
    request.send(conteudo);
}