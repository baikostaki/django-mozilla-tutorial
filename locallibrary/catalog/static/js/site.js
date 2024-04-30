const toastElementList = document.querySelectorAll('.toast')
const toastList = [...toastElementList].map(function (toastElement) {
        return new bootstrap.Toast(toastElement, {autohide: true}).show()
    }
)
// const myModal = document.getElementById('myModal')
// const myInput = document.getElementById('myInput')

// myModal.addEventListener('shown.bs.modal', () => {
//   myInput.focus()
// })