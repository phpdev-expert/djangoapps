<div id="deleteModal" class="modal" tabindex="-1" role="dialog">
  <div class="modal-dialog" role="document">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title">Response from server</h5>
        <button type="button" class="close" data-dismiss="modal" aria-label="Close">
          <span aria-hidden="true">&times;</span>
        </button>
      </div>
      <div class="modal-body">
        <p>Are you sure you want to delete this item?</p>
        <form
            id="deleteForm"
            class="delete-form"
            method="POST"
            action="{{ route('user.delete') }}"
            >
            {{ csrf_field() }}
            <input type="hidden" id="deleteItemId" name="id">

            <br/>
            <div class="modal-footer">
                <button type="submit" class="btn btn-primary">Delete</button>
            </div>
        </form>
      </div>
    </div>
  </div>
</div>
