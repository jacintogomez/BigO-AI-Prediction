document.querySelector('form').addEventListener('submit',async function(e){
    e.preventDefault();
    const formdata=new FormData(this);
    const response=await fetch('/process',{
        method:'POST',
        body:formdata
    });
    const result=await response.text();
    document.getElementById('result').innerText=result;
});