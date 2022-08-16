const toastElementList = document.querySelectorAll('.toast')
const toastList = [...toastElementList].map(function (toastElement){
    console.log('test', toastElement)
    return new bootstrap.Toast(toastElement, {autohide: false}).show()
    }
)
