$(document).ready(function(){
    $('#uploadForm').submit(function(event){
        event.preventDefault();
        var formdata=new FormData(this);
        $.ajax({
            url:'/process',
            type:'POST',
            data:formdata,
            success:function(response){
                $('#summary').html(response.summary);
            },
            error:function(xhr,status,error){
                console.error(error);
            }
        });
    });
});