/** @odoo-module */




document.addEventListener("DOMContentLoaded", ()=>{
    console.log("oi, estou aqui!")
    const  inputCEP = document.querySelector("#cep_0")
    console.log(inputCEP)
})

window.addEventListener("load", (event) => {

    setTimeout(()=>{
        const  inputCPF = document.querySelector("#cpf_0")
        inputCPF.setAttribute("maxlength", 14)
        inputCPF.addEventListener("keyup", (e)=>{
            let v = e.target.value
                v=v.replace(/\D/g,"")                    //Remove tudo o que não é dígito
                v=v.replace(/(\d{3})(\d)/,"$1.$2")       //Coloca um ponto entre o terceiro e o quarto dígitos
                v=v.replace(/(\d{3})(\d)/,"$1.$2")       //Coloca um ponto entre o terceiro e o quarto dígitos
                                                         //de novo (para o segundo bloco de números)
                v=v.replace(/(\d{3})(\d{1,2})$/,"$1-$2") //Coloca um hífen entre o terceiro e o quarto dígitos
                
                e.target.value = v
        })

        const  inputCEP = document.querySelector("#cep_0")
        inputCEP.setAttribute("maxlength", 9)
        inputCEP.addEventListener("keyup", (e)=>{
            let v = e.target.value

            v = v.replace(/\D/g,'')
            v = v.replace(/(\d{5})(\d)/,'$1-$2')
          
            e.target.value = v
        })

        
        const  inputPhone = document.querySelector("#tel_0")
        inputPhone.setAttribute("maxlength", 15)
        inputPhone.addEventListener("keyup", (e)=>{
            

            let v = e.target.value

            if(v.length == 14){
            }else{
                v = v.replace(/\D/g,'');
                v = v.replace(/(^\d{2})(\d)/,'($1) $2');
                v = v.replace(/(\d{4,5})(\d{4}$)/,'$1-$2');
        
              
                e.target.value = v
            }


        })




        console.log(inputPhone)
    }, 1000)


});
