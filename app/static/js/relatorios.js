const list_items = document.getElementsByClassName('rlist');

async function delete_item(item_id){
    var response = await fetch("/report/remove_by_img?image_url="+item_id, {method: 'DELETE'});
    return response.status
}

async function delete_everything(){
    var response = await fetch("/report/del_all", {method: 'DELETE'});
    return response.status
}

async function confirmation_delete_item(id) {
    let modal = new bootstrap.Modal(document.getElementById('modal'));
    let modal_element = document.getElementById('modal');
    modal_element.querySelector('.modal-body p').innerText= `Tem certeza que deseja deletar o item ${id}?`;
    deleteButton = modal_element.querySelector('.modal_delete');
    deleteButton.onclick = async () => {
        table_item = document.getElementById(id);
        let status = await delete_item(id);
        if(status==200){
            console.log('Deletado item '+id);
            table_item.remove();
        } else {
            alert('Erro na requisição - não foi possível deletar o item!')
        }
        modal_element.querySelector('.modal-body p').innerText= "";
        modal.hide();
        deleteButton.onclick = () => {};
    };
    
    modal.show();
}

async function confirmation_delete_everything() {
    let modal = new bootstrap.Modal(document.getElementById('modal'));
    let modal_element = document.getElementById('modal');
    modal_element.querySelector('.modal-body p').innerText= `Tem certeza que deseja deletar TODOS OS ITENS da base de dados?`;
    deleteButton = modal_element.querySelector('.modal_delete');
    deleteButton.onclick = async () => {
        let status = await delete_everything();
        if(status==200){
            console.log('Tudo foi deletado!');
            window.location.reload();
        } else {
            alert('Erro na requisição - não foi possível deletar!')
        }
        modal_element.querySelector('.modal-body p').innerText= "";
        modal.hide();
        deleteButton.onclick = () => {};
    };
    
    modal.show();
}

document.getElementById('delete_all').onclick = () => {
    confirmation_delete_everything()
}

for(let item of list_items){
    let date_item = item.querySelector('.table_date');
    let isodate = date_item.innerText+'Z'
    let icon = item.querySelector('td button')
    let rdate = new Date(isodate);
    date_item.innerText = rdate.toLocaleString();

    item.addEventListener('mouseover', () => {
      icon.classList.remove('invisible');
    });

    icon.addEventListener('click', () => {
        confirmation_delete_item(item.id);
    });

    item.addEventListener('mouseout', () => {
      icon.classList.add('invisible');
    });
}
