(function ( $ ) {
    'use strict';
    window.addEventListener('load', function() {
        var forms = document.getElementsByClassName('needs-validation');
        var validation = Array.prototype.filter.call(forms, function(form) {
            form.addEventListener('submit', function(event) {
                if (form.checkValidity() === false) {
                    event.preventDefault();
                    event.stopPropagation();
                }
                form.classList.add('was-validated');
            }, false);
        });
    }, false);

    var openUserModal = function (slug, item) {
        let heading = "Add User";
        let buttonText = "Create";
        if(slug === 'edit') {
            heading = 'Edit';
            buttonText = 'Update';
        }
        $("#userModalLabel").text(heading);
        $("#userForm button[type='submit']").text(buttonText);
        $("#userModal").modal({
            backdrop: 'static',
            keyboard: false
        });
    }

    var setUserFormAction = function(slug) {
        //Remove last char from URL and set for update
        var cc = $("#userForm").attr("action")
        var arr = cc.split('/');
        arr.pop();
        return arr.join('/')+ '/' + slug
    }

    $("#_openUserModal").on("click", function() {
        document.getElementById("userForm").reset();
        //Set form action to create
        $("#userForm").attr("action", setUserFormAction('create'));

        openUserModal('add', []);
    });

    $("._item_edit").on("click", function() {
        const item = JSON.parse($(this).closest('td').find('.item_value').val(), true);
        $("#_inputName").val(item.name);
        $("#_inputEmail").val(item.email);
        $("#_inputRole").val(item.is_admin);
        $("#user_id").val(item.id);

        // //Set form action to update
        $("#userForm").attr("action", setUserFormAction('update'));
        openUserModal('edit', item);
    });

    $("._item_delete").on("click", function() {
        const id = $(this).data('id');
        $("#deleteItemId").val(id);
        $("#deleteModal").modal({
            backdrop: 'static',
            keyboard: false
        })
    });

}( jQuery ));
